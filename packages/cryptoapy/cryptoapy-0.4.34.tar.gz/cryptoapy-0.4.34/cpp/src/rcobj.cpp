#include "common.hpp"
#include "rcobj.hpp"

int RCObj::ref()
{
    refcount ++;
    LOG("    ref %p: %i\n", this, refcount);
    return refcount;
}

int RCObj::unref()
{
    refcount --;
    if (refcount <= 0) {
        LOG("    delete %p\n", this);
        delete this;
        return 0;
    }
    LOG("    unref %p: %i\n", this, refcount);
    return refcount;
}
