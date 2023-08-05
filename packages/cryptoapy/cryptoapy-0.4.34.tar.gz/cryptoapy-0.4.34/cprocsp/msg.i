// vim: ft=swig

%newobject CryptMsg::get_nth_signer_info;
%newobject CryptMsg::signer_certs;
%newobject SignerIter::next;

%feature("python:slot", "tp_iter", functype="getiterfunc") SignerIter::__iter__;
%feature("python:slot", "tp_iternext", functype="iternextfunc") SignerIter::next;
%feature("ref") CryptMsg "$this->ref();"
%feature("unref") CryptMsg "$this->unref();"

%include "msg.hpp"

typedef struct _CERT_INFO {
    DWORD                       dwVersion;
    CRYPT_INTEGER_BLOB          SerialNumber;
    CRYPT_ALGORITHM_IDENTIFIER  SignatureAlgorithm;
    CERT_NAME_BLOB              Issuer;
    FILETIME                    NotBefore;
    FILETIME                    NotAfter;
    CERT_NAME_BLOB              Subject;
    CERT_PUBLIC_KEY_INFO        SubjectPublicKeyInfo;
    CRYPT_BIT_BLOB              IssuerUniqueId;
    CRYPT_BIT_BLOB              SubjectUniqueId;
    DWORD                       cExtension;
    PCERT_EXTENSION             rgExtension;
} CERT_INFO, *PCERT_INFO;

%extend _CERT_INFO {
    ~_CERT_INFO() {
        free($self);
    }
}
