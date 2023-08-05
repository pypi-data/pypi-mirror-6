#include "certinfo.hpp"

void CertInfo::init()
{
    psi = NULL;
    msg = NULL;
    cert = NULL;
}

CertInfo::CertInfo(Cert *c) throw (CSPException)
{
    LOG("CertInfo::CertInfo(%p)\n", c);
    init();
    cert = c;
    if(!cert) {
        throw CSPException("CertInfo: NULL certificate has no info");
    }
    cert->ref();
    psi = cert->pcert->pCertInfo;
}

CertInfo::CertInfo(CryptMsg *m, DWORD idx) throw (CSPException)
{
    LOG("CertInfo::CertInfo(%p, %u)\n", m, idx);
    init();
    msg = m;
    if(!msg) {
        throw CSPException("CertInfo: NULL message has no info");
    }
    msg->ref();
    DWORD spsi;
    HCRYPTMSG hmsg = msg->get_handle();

    if (!CryptMsgGetParam(hmsg, CMSG_SIGNER_CERT_INFO_PARAM, idx, NULL, &spsi)) {
        throw CSPException("CertInfo: Couldn't get signer info size");
    }
    psi = (CERT_INFO *) malloc(spsi);
    if (!CryptMsgGetParam(hmsg, CMSG_SIGNER_CERT_INFO_PARAM, idx, psi, &spsi)) {
        throw CSPException("CertInfo: Couldn't get signer info data");
    }
}

CertInfo::~CertInfo () throw(CSPException)
{
    LOG("CertInfo::~CertInfo(%p)\n", this);
    if (msg) {
        msg -> unref();
        if (psi) {
            free((void *)psi);
        }
    }
    if (cert) {
        cert -> unref();
    }
}

BYTE CertInfo::usage() throw(CSPException) {
    BYTE res = 0;
    DWORD dummy = 1;
    CertGetIntendedKeyUsage(MY_ENC_TYPE, psi, &res, dummy);
    return res;
}


DWORD CertInfo::version()
{
    return psi->dwVersion;
}

char *CertInfo::sign_algorithm()
{
    LOG("CertInfo::sign_algorithm\n");
    return psi->SignatureAlgorithm.pszObjId;
}

void CertInfo::name(BYTE **s, DWORD *slen, bool decode) throw(CSPException)
{
    LOG("CertInfo::name()\n");
    if (msg) {
        throw CSPException("CertInfo.name: Message signer info may not contain subject name", -1);
    }
    if (decode) {
        decode_name_blob(&psi->Subject, s, slen);
    } else {
        *slen = psi->Subject.cbData;
        *s = (BYTE *)malloc(*slen);
        memcpy(*s, psi->Subject.pbData, *slen);
    }
}

void CertInfo::issuer(BYTE **s, DWORD *slen, bool decode) throw(CSPException)
{
    LOG("CertInfo::issuer()\n");
    if (decode) {
        decode_name_blob(&psi->Issuer, s, slen);
    } else {
        *slen = psi->Issuer.cbData;
        *s = (BYTE *)malloc(*slen);
        memcpy(*s, psi->Issuer.pbData, *slen);
    }
}

void CertInfo::serial(BYTE **s, DWORD *slen) throw(CSPException)
{
    *slen = psi->SerialNumber.cbData;
    *s = (BYTE *)malloc(*slen);
    memcpy(*s, psi->SerialNumber.pbData, *slen);
}

void CertInfo::not_before(BYTE **s, DWORD *slen) throw(CSPException)
{
    *slen = sizeof(FILETIME);
    *s = (BYTE *)malloc(*slen);
    memcpy(*s, &psi->NotBefore, *slen);
}

void CertInfo::not_after(BYTE **s, DWORD *slen) throw(CSPException)
{
    *slen = sizeof(FILETIME);
    *s = (BYTE *)malloc(*slen);
    memcpy(*s, &psi->NotAfter, *slen);
}

void CertInfo::decode_name_blob(PCERT_NAME_BLOB pNameBlob, BYTE **s, DWORD *slen)
{
    DWORD flags = CERT_X500_NAME_STR | CERT_NAME_STR_NO_PLUS_FLAG;
    LOG("CertInfo::decode_name_blob %p\n", pNameBlob);

    *slen = CertNameToStr( X509_ASN_ENCODING, pNameBlob, flags, NULL, 0);
    if (*slen <= 1) {
        throw CSPException("CertInfo.decode_name_blob: Wrong size for blob decoded data");
    }

    *s = (BYTE *)malloc(*slen);

    *slen = CertNameToStr(X509_ASN_ENCODING, pNameBlob, flags, (char *)*s, *slen);

    if (*slen <= 1) {
        free(*s);
        throw CSPException("CertInfo.decode_name_blob: Couldn't decode cert blob");
    }
    (*slen)--;
}

ExtIter *CertInfo::extensions() throw(CSPException) {
    return new ExtIter(this);
}

ExtIter::ExtIter(CertInfo *p) throw (CSPException)
    : parent(p), i(0)
{
    LOG("ExtIter::ExtIter(%p)\n", parent);
    if(!parent) {
        throw CSPException("CertInfo.extensions: NULL reference to CertInfo", -1);
    }
    parent->ref();
    n = parent->psi->cExtension;
    ext = parent->psi->rgExtension;
}

ExtIter::~ExtIter() throw (CSPException) {
    LOG("ExtIter::~ExtIter(%p)\n", this);
    if (parent)
        parent->unref();
}

CertExtension *ExtIter::next() throw (Stop_Iteration, CSPException) {
    LOG("ExtIter::next()\n");
    if (i >= n) {
        LOG("    Stop iter\n");
        throw Stop_Iteration();
    }
    CertExtension *res = new CertExtension(&ext[i], parent);
    i ++;
    return res;
}

