#ifndef SIGN_HPP_INCLUDED
#define SIGN_HPP_INCLUDED

#include "msg.hpp"

class Signature : public CryptMsg
{
public:
    Signature(Crypt *ctx=NULL) throw(CSPException) : CryptMsg(ctx) {}

    Signature(BYTE *STRING, DWORD LENGTH, Crypt *ctx=NULL) throw(CSPException)
        : CryptMsg(STRING, LENGTH, ctx) {}

    bool verify_data(BYTE *STRING, DWORD LENGTH, int n) throw(CSPException);

    void sign_data(BYTE *STRING, DWORD LENGTH, BYTE **s, DWORD *slen, Cert *signer, bool detach=1) throw(CSPException) {
        CryptMsg::sign_data(STRING, LENGTH, s, slen, signer, detach);
    }
};

#endif
