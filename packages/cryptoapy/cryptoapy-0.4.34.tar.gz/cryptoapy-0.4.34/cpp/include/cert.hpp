#ifndef CERT_HPP_INCLUDED
#define CERT_HPP_INCLUDED

#include "except.hpp"
#include "rcobj.hpp"

class CertStore;
class Crypt;
class CryptMsg;
class CertInfo;
class EKUIter;
class Key;

class Cert : public RCObj
{
private:
    PCCERT_CONTEXT pcert;
    CertStore *parent;

    void init() {
        parent = NULL;
    }

public:
    Cert* duplicate() throw(CSPException);

    void remove_from_store() throw(CSPException);

    Cert(PCCERT_CONTEXT pc, CertStore *parent=NULL) throw(CSPException);

    Cert(BYTE* STRING, DWORD LENGTH) throw(CSPException);

    static Cert *self_sign(Crypt *ctx, BYTE *STRING, DWORD LENGTH)  throw(CSPException);

    ~Cert() throw(CSPException);

    void extract(BYTE **s, DWORD *slen) throw(CSPException);

    void thumbprint(BYTE **s, DWORD *slen) throw(CSPException);

    void bind(Crypt *ctx, DWORD keyspec=AT_KEYEXCHANGE);

    void set_pin(char *pin) throw(CSPException);

    EKUIter *eku() throw(CSPException);

    friend class CryptMsg;
    friend class CertStore;
    friend class CertInfo;
    friend class EKUIter;
    friend class Key;
};

class CertIter
{
public:
    CertStore *parent;
    bool iter;
    PCCERT_CONTEXT pcert;

    CertIter(CertStore *p) throw (CSPException);

    CertIter *__iter__() {
        return new CertIter(parent);
    }

    virtual ~CertIter() throw (CSPException);

    virtual Cert *next() throw (Stop_Iteration, CSPException);
};

class CertFind : public CertIter
{
public:
    CRYPT_HASH_BLOB chb;
    CRYPT_HASH_BLOB *param;
    DWORD enctype, findtype;

    CertFind(CertStore *p, DWORD et, DWORD ft, BYTE *STRING, DWORD LENGTH);

    virtual ~CertFind() throw (CSPException);

    CertFind(CertStore *p, DWORD et, BYTE *STRING, DWORD LENGTH);

    Cert *next() throw (Stop_Iteration, CSPException);

    CertFind *__iter__() {
        if (findtype == CERT_FIND_SUBJECT_STR) {
            return new CertFind(parent, enctype, (BYTE *)param, strlen((char *)param));
        } else {
            return new CertFind(parent, enctype, findtype, param->pbData, param->cbData);
        }
    }
};


class CertStore : public RCObj
{
private:
    Crypt *ctx;
    CryptMsg *msg;
    HCERTSTORE hstore;
    char *proto;

    void init();
public:

    CertStore(CryptMsg *parent) throw(CSPException);

    CertStore() throw(CSPException);

    CertStore(Crypt *parent, BYTE *STRING, DWORD LENGTH) throw(CSPException);

    ~CertStore() throw(CSPException);

    CertIter *__iter__() throw(CSPException);

    CertFind *find_by_thumb(BYTE *STRING, DWORD LENGTH) throw(CSPException);

    CertFind *find_by_name(BYTE *STRING, DWORD LENGTH) throw(CSPException);

    Cert *get_cert_by_info(CertInfo *ci) throw(CSPException, CSPNotFound);

    Cert *add_cert(Cert *c) throw(CSPException);


    friend class CryptMsg;
    friend class CertIter;
    friend class CertFind;
};

class EKUIter
{
public:
    EKUIter (Cert *c);
    virtual ~EKUIter ();
    EKUIter *__iter__() {
        return new EKUIter(parent);
    }
    void next (BYTE **s, DWORD *slen) throw (CSPException, Stop_Iteration);

private:
    Cert *parent;
    CERT_ENHKEY_USAGE *pekus;
    DWORD cbsize;
    friend class Cert;
    DWORD i;
};

#endif
