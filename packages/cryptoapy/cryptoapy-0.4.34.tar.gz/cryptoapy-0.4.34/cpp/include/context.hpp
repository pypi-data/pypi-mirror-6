#ifndef CONTEXT_HPP_INCLUDED
#define CONTEXT_HPP_INCLUDED

#include "rcobj.hpp"
#include "except.hpp"

class Key;
class CryptIter;

class CryptDesc
{
public:
    DWORD type;
    char *name;
    virtual ~CryptDesc()
    {
        delete[] name;
    }
};

class CryptIter
{
    DWORD index;
public:
    CryptIter() throw (CSPException);

    CryptIter *__iter__() {
        return new CryptIter();
    }

    CryptDesc *next() throw (Stop_Iteration, CSPException);
};

class Crypt : public RCObj
{
    HCRYPTPROV hprov;
    char *cont_name;
    char *pr_name;

public:

    Crypt (BYTE *STRING, DWORD LENGTH, DWORD type, DWORD flags, char *name=NULL) throw(CSPException, CSPNotFound);
    ~Crypt() throw(CSPException);

    char *name();
    char *uniq_name();
    char *prov_name();
    DWORD prov_type();

    Key *create_key(DWORD flags, DWORD keyspec=AT_KEYEXCHANGE) throw(CSPException);

    Key *get_key(DWORD keyspec=AT_KEYEXCHANGE) throw(CSPException, CSPNotFound);

    Key *import_key(BYTE *STRING, DWORD LENGTH, Key *decrypt=NULL) throw(CSPException);

    void set_password(char *pin, DWORD keyspec=AT_KEYEXCHANGE) throw(CSPException);
    void change_password(char *pin) throw (CSPException);

    static void remove(char *container, DWORD type, char *name) throw(CSPException, CSPNotFound);

    static CryptIter *enumerate() throw(CSPException);

    friend class Cert;
    friend class CryptMsg;
    friend class Signature;
    friend class CertStore;
    friend class CertRequest;
};


#endif
