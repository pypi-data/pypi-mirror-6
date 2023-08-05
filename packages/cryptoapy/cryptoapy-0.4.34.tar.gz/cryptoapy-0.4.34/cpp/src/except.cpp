#include "common.hpp"
#include "except.hpp"

GenericException::GenericException(const char *m, DWORD code) {
    if (!code)
        code = GetLastError();
    snprintf(msg, 256, "%s (0x%x)", m, (unsigned) code);
}
