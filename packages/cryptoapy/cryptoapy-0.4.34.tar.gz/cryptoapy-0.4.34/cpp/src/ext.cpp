#include "ext.hpp"
#include "certinfo.hpp"

CertExtension::CertExtension(CERT_EXTENSION *pext, CertInfo *p) throw(CSPException)
    : parent(p)
{
    LOG("CertExtension::CertExtension(%p)\n", pext);
    if (parent)
        parent->ref();
    memcpy(&data, pext, sizeof(CERT_EXTENSION));
}

CertExtension::~CertExtension()
{
    LOG("CertExtension::~CertExtension(%p)\n", this);
    if (parent)
        parent->unref();
}


void CertExtension::oid(BYTE **s, DWORD *slen) {
    LOG("CertExtension::oid() = %p\n", data.pszObjId);
    *slen = strlen(data.pszObjId) + 1;
    *s = (BYTE *)malloc(*slen);
    strncpy((char *)*s, data.pszObjId, *slen);
    (*s)[*slen - 1] = 0;
}
