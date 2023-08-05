#include "common.hpp"
#include "context.hpp"
#include "request.hpp"
#include "ext.hpp"
#include <vector>

using namespace std;

int CertRequest::add_attribute(BYTE *STRING, DWORD LENGTH) throw (CSPException)
{
    CRYPT_ATTRIBUTE *pa;
    DWORD n = CertReqInfo.cAttribute;
    LOG("CertRequest::add_attribute(%s)\n", STRING);

    CertReqInfo.rgAttribute = (CRYPT_ATTRIBUTE *)realloc(CertReqInfo.rgAttribute, (n + 1) * sizeof(CRYPT_ATTRIBUTE));
    pa = &CertReqInfo.rgAttribute[n];
    ZeroMemory(pa, sizeof(CRYPT_ATTRIBUTE));
    CertReqInfo.cAttribute ++;
    pa -> pszObjId = new char[LENGTH + 1];
    strncpy(pa -> pszObjId, (char *)STRING, LENGTH + 1);
    pa -> pszObjId[LENGTH] = 0;
    pa -> cValue = 0;
    pa -> rgValue = NULL;
    LOG("    added attribute %i\n", n);
    return n;
}

void CertRequest::add_attribute_value(int n, BYTE *STRING, DWORD LENGTH) throw (CSPException) {
    CRYPT_ATTRIBUTE *pa;
    CRYPT_ATTR_BLOB *pdata;
    LOG("CertRequest::add_attribute_value(%i, %p, %u)\n", n, STRING, LENGTH);

    if (n >= CertReqInfo.cAttribute) {
        throw CSPException("CertRequest.add_attribute_value: Attribute index out of range", -1);
    }
    pa = &CertReqInfo.rgAttribute[n];
    pa -> rgValue = (PCRYPT_ATTR_BLOB) realloc(pa -> rgValue, sizeof(CRYPT_ATTR_BLOB) * (pa -> cValue + 1) );
    pdata = &(pa -> rgValue[pa -> cValue]);
    (pa -> cValue) ++;

    ZeroMemory(pdata, sizeof(CRYPT_ATTR_BLOB));
    pdata -> cbData = LENGTH;
    pdata -> pbData = (BYTE *)malloc(LENGTH);
    memcpy(pdata->pbData, STRING, LENGTH);
}

CertRequest::CertRequest(Crypt *ctx) throw (CSPException) : ctx(ctx) {
    LOG("CertRequest::CertRequest(%p)\n", ctx);
    if (ctx) {
        ctx -> ref();
    } else {
        throw CSPException("CertRequest: Null key container can not generate requests", -1);
    }
    cbNameEncoded = 0;
    pbNameEncoded = NULL;

    ZeroMemory(&CertReqInfo, sizeof(CertReqInfo));
    CertReqInfo.dwVersion = CERT_REQUEST_V1;

    ZeroMemory(&SigAlg, sizeof(SigAlg));
    SigAlg.pszObjId = (char *)szOID_CP_GOST_R3411_R3410EL;

    pbPublicKeyInfo = NULL;
    bool res = CryptExportPublicKeyInfo( ctx->hprov, AT_KEYEXCHANGE, MY_ENC_TYPE,
            NULL, &cbPublicKeyInfo );
    if (!res) {
        throw CSPException("CertRequest: Couldn't determine exported key info length");
    }
    pbPublicKeyInfo = (CERT_PUBLIC_KEY_INFO*) malloc( cbPublicKeyInfo );
    res = CryptExportPublicKeyInfo( ctx->hprov, AT_KEYEXCHANGE,
                              MY_ENC_TYPE, pbPublicKeyInfo, &cbPublicKeyInfo );
    if (!res) {
        throw CSPException("CertRequest: Couldn't export public key info");
    }
    CertReqInfo.SubjectPublicKeyInfo = *pbPublicKeyInfo;
    CertReqInfo.cAttribute = 0;
    CertReqInfo.rgAttribute = NULL;
}

CertRequest::~CertRequest() throw (CSPException) {
    LOG("CertRequest::~CertRequest(%p)\n", this);
    if (ctx) {
        ctx -> unref();
    }
    if (CertReqInfo.Subject.pbData) {
        free(CertReqInfo.Subject.pbData);
    }
    if (pbPublicKeyInfo) {
        free(pbPublicKeyInfo);
    }

    CRYPT_ATTRIBUTE *pa;
    CRYPT_ATTR_BLOB *pdata;
    for (size_t i = 0; i < CertReqInfo.cAttribute; i++)
    {
        pa = &CertReqInfo.rgAttribute[i];
        for (size_t j = 0; j < pa->cValue; j++)
        {
            pdata = &(pa -> rgValue[j]);
            if(pdata -> pbData)
                free((void *)pdata -> pbData);
        }
        free((void*) pa->rgValue);
        delete[] pa->pszObjId;
    }
    free((void*) CertReqInfo.rgAttribute);
}

void CertRequest::set_subject(BYTE *STRING, DWORD LENGTH) throw (CSPException) {
    LOG("CertRequest::set_subject(%s)\n", STRING);

    CertReqInfo.Subject.cbData = LENGTH;
    if (CertReqInfo.Subject.pbData) {
        free(CertReqInfo.Subject.pbData);
        CertReqInfo.Subject.pbData = NULL;
    }
    CertReqInfo.Subject.pbData = (BYTE *)malloc(CertReqInfo.Subject.cbData);
    memcpy(CertReqInfo.Subject.pbData, STRING, LENGTH);

}

void CertRequest::get_data(BYTE **s, DWORD *slen) throw (CSPException) {
    //
    // XXX
    //
    LOG("CertRequest::get_data()\n");

    bool res = CryptSignAndEncodeCertificate(
        ctx->hprov, AT_KEYEXCHANGE, MY_ENC_TYPE,
        X509_CERT_REQUEST_TO_BE_SIGNED, &CertReqInfo,
        &SigAlg, NULL, NULL, slen );
    if(!res) {
        throw CSPException("CertRequest.get_data: Couldn't determine encoded request size");
    }

    *s = (BYTE *)malloc(*slen);

    res = CryptSignAndEncodeCertificate(
        ctx->hprov, AT_KEYEXCHANGE, MY_ENC_TYPE,
        X509_CERT_REQUEST_TO_BE_SIGNED, &CertReqInfo,
        &SigAlg, NULL, *s, slen );

    if(!res) {
        throw CSPException("CertRequest.get_data: Couldn't encode certificate request");
    }
}
