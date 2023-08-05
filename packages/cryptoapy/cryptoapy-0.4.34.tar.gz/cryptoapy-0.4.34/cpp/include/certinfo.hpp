#ifndef CERTINFO_HPP_INCLUDED
#define CERTINFO_HPP_INCLUDED

#include "common.hpp"
#include "rcobj.hpp"
#include "cert.hpp"
#include "msg.hpp"
#include "ext.hpp"

class ExtIter;
class CertInfo : public RCObj
{
public:
    CertInfo (Cert  *c) throw(CSPException);
    CertInfo(CryptMsg *m, DWORD idx) throw (CSPException);
    virtual ~CertInfo () throw(CSPException);

    DWORD version();
    void issuer(BYTE **s, DWORD *slen, bool decode=TRUE) throw(CSPException);
    void name(BYTE **s, DWORD *slen, bool decode=TRUE) throw(CSPException);
    void not_before(BYTE **s, DWORD *slen) throw(CSPException);
    void not_after(BYTE **s, DWORD *slen) throw(CSPException);
    BYTE usage() throw(CSPException);
    char *sign_algorithm();
    void serial(BYTE **s, DWORD *slen) throw(CSPException);
    ExtIter *extensions() throw(CSPException);


private:
    void decode_name_blob(PCERT_NAME_BLOB pNameBlob, BYTE **s, DWORD *slen);
    void init();
    CERT_INFO *psi;
    Cert *cert;
    CryptMsg *msg;

    friend class CertStore;
    friend class ExtIter;
};

class ExtIter
{
private:
    CertInfo *parent;
    int n, i;
    CERT_EXTENSION *ext;
public:

    ExtIter(CertInfo *p) throw (CSPException);

    ExtIter *__iter__() {
        return new ExtIter(parent);
    }

    virtual ~ExtIter() throw (CSPException);

    virtual CertExtension *next() throw (Stop_Iteration, CSPException);
};


#endif
