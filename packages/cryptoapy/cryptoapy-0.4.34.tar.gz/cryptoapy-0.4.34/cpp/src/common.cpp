#include "common.hpp"

void debug_log(char *s, ...) {
    va_list ap;
    va_start(ap, s);
    FILE *fp = fopen("debug.log", "a");
    vfprintf(fp, s, ap);
    va_end(ap);
    fclose(fp);
}

