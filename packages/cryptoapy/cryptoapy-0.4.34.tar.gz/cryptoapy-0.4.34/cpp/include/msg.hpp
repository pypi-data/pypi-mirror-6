#ifndef MSG_HPP_INCLUDED
#define MSG_HPP_INCLUDED

#include "context.hpp"
#include "except.hpp"
#include "cert.hpp"
#include <vector>

class SignerIter;
class CertInfo;
class CryptMsg : public RCObj
{
private:
    std::vector<Cert *> signers;
    std::vector<Cert *> recipients;
    void init(Crypt *ctx) throw(CSPException);
    HCRYPTMSG hmsg;
protected:
    Crypt *cprov;
    BYTE *data;
    DWORD data_length;
    HCRYPTMSG get_handle() throw (CSPException);
public:
    // инициализация сообщения для декодирования
    CryptMsg(BYTE *STRING, DWORD LENGTH, Crypt *ctx=NULL) throw(CSPException);

    // инициализация сообщения для кодирования
    CryptMsg(Crypt *ctx=NULL) throw(CSPException);
    void decrypt_by_cert(Cert *crt) throw(CSPException, CSPNotFound);

    virtual ~CryptMsg() throw(CSPException);
    int num_signers() throw(CSPException);
    void get_data(BYTE **s, DWORD *slen) throw(CSPException);
    bool verify_cert(Cert *c) throw(CSPException);
    DWORD get_type() throw(CSPException);
    void add_recipient(Cert *c) throw(CSPException);
    void encrypt_data(BYTE *STRING, DWORD LENGTH, BYTE **s, DWORD *slen) throw(CSPException);
    void decrypt(BYTE **s, DWORD *slen, CertStore *store) throw(CSPException, CSPNotFound);
    virtual void sign_data(BYTE *STRING, DWORD LENGTH, BYTE **s, DWORD *slen,
            Cert *signer, bool detach=0) throw(CSPException);
    bool verify(DWORD n) throw(CSPException);

    friend class CertStore;
    friend class CertInfo;
};

#endif
