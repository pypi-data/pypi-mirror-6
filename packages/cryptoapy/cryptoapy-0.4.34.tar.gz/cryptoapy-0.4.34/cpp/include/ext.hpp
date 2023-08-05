#ifndef EXT_HPP_INCLUDED
#define EXT_HPP_INCLUDED
#include "common.hpp"
#include "except.hpp"
#include <vector>

class CertInfo;
class CertExtension
{
private:
    CERT_EXTENSION data;
    CertInfo *parent;
public:
    CertExtension(CERT_EXTENSION *pext, CertInfo *p) throw(CSPException);
    virtual ~CertExtension();
    void oid(BYTE **s, DWORD *slen);
};

#endif //EXT_HPP_INCLUDED
