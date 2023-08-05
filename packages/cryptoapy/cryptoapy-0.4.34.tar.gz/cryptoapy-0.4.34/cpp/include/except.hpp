#ifndef EXCEPT_HPP_INCLUDED
#define EXCEPT_HPP_INCLUDED

class GenericException {
public:
    char msg[256];
    GenericException(const char *m, DWORD code=0);
};

class Stop_Iteration {
};

class CSPException : public GenericException {
    public:
        CSPException(const char *m, DWORD code=0) : GenericException(m, code) {};
};
class CSPNotFound : public GenericException {
    public:
        CSPNotFound(const char *m, DWORD code=0) : GenericException(m, code) {};
};

#endif
