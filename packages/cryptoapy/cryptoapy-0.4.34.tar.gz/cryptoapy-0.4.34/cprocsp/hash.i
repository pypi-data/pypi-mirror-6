/* vim: ft=swig
*/

WINADVAPI
BOOL
WINAPI
CryptCreateHash(
    HCRYPTPROV hProv,
    ALG_ID Algid,
    HCRYPTKEY hKey,
    DWORD dwFlags,
    HCRYPTHASH *OUTPUT
    );


WINADVAPI
BOOL
WINAPI
CryptHashData(
    HCRYPTHASH hHash,
    CONST BYTE *pbData,
    DWORD dwDataLen,
    DWORD dwFlags
    );


WINADVAPI
BOOL
WINAPI
CryptDestroyHash(
    HCRYPTHASH hHash
    );


WINADVAPI
BOOL
WINAPI
CryptSetHashParam(
    HCRYPTHASH hHash,
    DWORD dwParam,
    CONST BYTE *pbData,
    DWORD dwFlags
    );


WINADVAPI
BOOL
WINAPI
CryptGetHashParam(
    HCRYPTHASH hHash,
    DWORD dwParam,
    BYTE *pbData,
    DWORD *pdwDataLen,
    DWORD dwFlags
    );
