#ifndef KEY_HPP_INCLUDED
#define KEY_HPP_INCLUDED

#include "context.hpp"
#include "except.hpp"
#include "cert.hpp"

class Key
{
    HCRYPTKEY hkey;
    Crypt *parent;
public:
    Key(Crypt *pctx, HCRYPTKEY hk) throw(CSPException);

    ~Key() throw(CSPException);

    void encode(BYTE **s, DWORD *slen, Key *cryptkey=NULL) throw(CSPException);

    void store_cert(Cert *c) throw (CSPException);

    void extract_cert(BYTE **s, DWORD *slen) throw (CSPException);

    friend class Crypt;
};

#endif
