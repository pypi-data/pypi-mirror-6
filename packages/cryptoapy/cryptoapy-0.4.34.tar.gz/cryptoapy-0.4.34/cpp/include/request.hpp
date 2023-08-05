#ifndef REQUEST_HPP_INCLUDED
#define REQUEST_HPP_INCLUDED

#include "except.hpp"
#include "rcobj.hpp"

class Crypt;

class CertExtensions;
class ExtKeyUsage;
class KeyUsage;
class CertRequest
{
    DWORD            cbNameEncoded;
    BYTE*            pbNameEncoded;
    CERT_REQUEST_INFO   CertReqInfo;
    CRYPT_ALGORITHM_IDENTIFIER SigAlg;
    CERT_PUBLIC_KEY_INFO *pbPublicKeyInfo;
    DWORD cbPublicKeyInfo;
    Crypt *ctx;
    public:
        CertRequest(Crypt *ctx) throw (CSPException);
        void set_subject(BYTE *STRING, DWORD LENGTH) throw (CSPException);
        void get_data(BYTE **s, DWORD *slen) throw (CSPException);
        ~CertRequest() throw (CSPException);
        int add_attribute(BYTE *STRING, DWORD LENGTH) throw (CSPException);
        void add_attribute_value(int n, BYTE *STRING, DWORD LENGTH) throw (CSPException);
};

#endif
