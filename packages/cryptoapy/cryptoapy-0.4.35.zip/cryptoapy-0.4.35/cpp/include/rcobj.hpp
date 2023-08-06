#ifndef RCOBJ_HPP_INCLUDED
#define RCOBJ_HPP_INCLUDED

class RCObj
{
protected:
    signed int refcount;
public:
    RCObj() {
        refcount = 0;
    }

    virtual ~RCObj() {};

    int ref();

    int unref();
};

#endif
