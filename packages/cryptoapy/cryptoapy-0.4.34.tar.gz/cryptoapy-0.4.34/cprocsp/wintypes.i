/* vim: ft=swig
*/

#ifndef WINVER
#define WINVER 0x0500
#endif /* WINVER */

#define WINCRYPT32API

/*
 * BASETYPES is defined in ntdef.h if these types are already defined
 */

#ifndef BASETYPES
#define BASETYPES
typedef unsigned long ULONG;
typedef ULONG *PULONG;
typedef unsigned short USHORT;
typedef USHORT *PUSHORT;
typedef unsigned char UCHAR;
typedef UCHAR *PUCHAR;
typedef char *PSZ;
#endif  /* !BASETYPES */

#ifndef NULL
#ifdef __cplusplus
#define NULL    0
#else
#define NULL    ((void *)0)
#endif
#endif

#ifndef WINADVAPI
#define WINADVAPI
#endif

#ifndef FALSE
#define FALSE               0
#endif

#ifndef TRUE
#define TRUE                1
#endif

#ifndef IN
#define IN
#endif

#ifndef OUT
#define OUT
#endif

#ifndef OPTIONAL
#define OPTIONAL
#endif

#undef far
#undef near
#undef pascal

#define far
#define near

#if (!defined(_MAC)) && ((defined(_MSC_VER) && (_MSC_VER >= 800)) || defined(_STDCALL_SUPPORTED))
#define pascal __stdcall
#else
#define pascal
#endif

#if defined(DOSWIN32) || defined(_MAC)
#define cdecl _cdecl
#ifndef CDECL
#define CDECL _cdecl
#endif
#else
#define cdecl
#ifndef CDECL
#define CDECL
#endif
#endif

#ifdef _MAC
#define CALLBACK    PASCAL
#define WINAPI      CDECL
#define WINAPIV     CDECL
#define APIENTRY    WINAPI
#define APIPRIVATE  CDECL
#ifdef _68K_
#define PASCAL      __pascal
#else
#define PASCAL
#endif
#elif (defined(_MSC_VER) && (_MSC_VER >= 800)) || defined(_STDCALL_SUPPORTED)
#define CALLBACK    __stdcall
#define WINAPI      __stdcall
#define WINAPIV     __cdecl
#define APIENTRY    WINAPI
#define APIPRIVATE  __stdcall
#define PASCAL      __stdcall
#else
#define CALLBACK
#define WINAPI
#define WINAPIV
#define APIENTRY    WINAPI
#define APIPRIVATE
#define PASCAL      pascal
#endif

#undef FAR
#undef  NEAR
#define FAR                 far
#define NEAR                near
#ifndef CONST
#define CONST               const
#endif

/*Определения из WinNT.h */
/* Basics*/

#ifndef VOID
#define VOID void
typedef char CHAR;
typedef short SHORT;
#ifndef LONG
typedef int LONG;
#endif
typedef unsigned int       DWORD;	/* XXXX icc говорит, что с этим типом есть проблемы ???? */
#ifndef _HRESULT_DEFINED
#define _HRESULT_DEFINED
typedef LONG HRESULT;
#endif /* !_HRESULT_DEFINED */
#endif /* VOID*/

typedef int                 BOOL;
typedef unsigned char       BYTE;
typedef unsigned short      WORD;
typedef float               FLOAT;
typedef FLOAT               *PFLOAT;
typedef BOOL near           *PBOOL;
typedef BOOL far            *LPBOOL;
typedef BYTE near           *PBYTE;
typedef BYTE far            *LPBYTE;
typedef CONST BYTE far      *LPCBYTE;
typedef int near            *PINT;
typedef int far             *LPINT;
typedef WORD near           *PWORD;
typedef WORD far            *LPWORD;
typedef long far            *LPLONG;
typedef DWORD near          *PDWORD;
typedef DWORD far           *LPDWORD;
typedef void far            *LPVOID;
typedef CONST void far      *LPCVOID;
typedef void *PVOID;

typedef int                 INT;
typedef unsigned int        UINT;
typedef unsigned int        *PUINT;

#if defined WIN32
typedef unsigned __int64 ULONGLONG;
typedef __int64 LONGLONG;
#else
typedef unsigned long long ULONGLONG;
typedef long long LONGLONG;
#endif

#ifndef _DWORDLONG_
#define _DWORDLONG_
typedef ULONGLONG  DWORDLONG;
typedef DWORDLONG *PDWORDLONG;
#endif

#if (defined(_M_IX86) || defined(_M_ALPHA) || defined(_M_IA64) || defined(_M_AMD64)) && !defined(MIDL_PASS)
#define DECLSPEC_IMPORT     __declspec(dllimport)
#else
#define DECLSPEC_IMPORT
#endif

#if 0
#if defined (UNIX) || (defined (CSP_LITE) && defined (CSP_INTERNAL))
# if defined (UNIX) 
#  ifdef STDC_HEADERS
#    include <stdlib.h>
#    include <stddef.h>
#  else /* STDC_HEADERS */
#    ifdef HAVE_STDLIB_H
#      include <stdlib.h>
#    endif
#  endif /* STDC_HEADERS */
#  include <wchar.h>
# else /* (defined (CSP_LITE) && defined (CSP_INTERNAL)) */
#  include "csplitecrt.h"
# endif
  ...
#else
# if defined (CSP_LITE)
#  include "reader/ddk4.h"
# else /* !defined (CSP_LITE) */
#  include <WinDef.h>
# endif
#endif
#endif

#ifdef CSP_LITE
#ifndef CSP_DRIVER
# include "csplitecrt.h"
#endif
#else
# ifdef STDC_HEADERS
#   include <stdlib.h>
#   include <stddef.h>
# else /* STDC_HEADERS */
#   ifdef HAVE_STDLIB_H
#     include <stdlib.h>
#   endif
# endif /* STDC_HEADERS */
# include <wchar.h>
#endif /* CSP_LITE */

typedef wchar_t WCHAR;   /* wc,   16-bit UNICODE character */
typedef CONST wchar_t *LPCWSTR, *PCWSTR;

#ifndef __TCHAR_DEFINED
#define __TCHAR_DEFINED

#if defined( UNICODE )
typedef wchar_t TCHAR, *PTCHAR;
typedef wint_t _TINT;
#else
typedef char TCHAR, *PTCHAR;
typedef int _TINT;
#endif

#endif /* __TCHAR_DEFINED */

#ifndef GUID_DEFINED
#define GUID_DEFINED
typedef struct _GUID {
    unsigned long  Data1;
    unsigned short Data2;
    unsigned short Data3;
    unsigned char  Data4[ 8 ];
} GUID;
#endif

#ifdef STRICT
typedef void *HANDLE;
#define DECLARE_HANDLE(name) struct name##_ { int unused; }; typedef struct name##_ *name
#else
typedef PVOID HANDLE;
#define DECLARE_HANDLE(name) typedef HANDLE name
#endif
typedef HANDLE *PHANDLE;

/*typedef HANDLE       HWND;*/
DECLARE_HANDLE(HINSTANCE);
DECLARE_HANDLE(HWND);
typedef HINSTANCE HMODULE;      /* HMODULEs can be used in place of HINSTANCEs */
typedef HANDLE HLOCAL;

/*
#ifndef NT_INCLUDED
#include <winnt.h>
#endif  NT_INCLUDED */

/* Types use for passing & returning polymorphic values 
typedef UINT_PTR            WPARAM;
typedef LONG_PTR            LPARAM;
typedef LONG_PTR            LRESULT;
*/
/*Определения из BaseTsd.h*/
#if SIZEOF_VOID_P == 8 || defined(_WIN64)
typedef long long INT_PTR, *PINT_PTR;
typedef unsigned long long UINT_PTR, *PUINT_PTR;
typedef long long LONG_PTR, *PLONG_PTR;
typedef unsigned long long ULONG_PTR, *PULONG_PTR;
#elif !defined(UNIX) || SIZEOF_VOID_P == 4
typedef int INT_PTR, *PINT_PTR;
typedef unsigned int UINT_PTR, *PUINT_PTR;
typedef long LONG_PTR, *PLONG_PTR;
typedef unsigned long ULONG_PTR, *PULONG_PTR;
#else
#error "SIZEOF_VOID_P not defined"
#endif

typedef ULONG_PTR DWORD_PTR, *PDWORD_PTR;
/*Конец определений из BaseTsd.h*/


typedef int (CALLBACK *FARPROC)(void);
typedef int (CALLBACK *NEARPROC)(void);
typedef int (CALLBACK *PROC)(void);

/*
// ANSI (Multi-byte Character) types
*/
typedef CHAR *PCHAR;
typedef CHAR *LPCH, *PCH;

typedef CONST CHAR *LPCSTR, *PCSTR;
typedef CONST CHAR *LPCCH, *PCCH;
typedef CHAR *NPSTR;
typedef CHAR *LPSTR, *PSTR;

typedef WCHAR *LPWSTR, *PWSTR;

typedef TCHAR *LPTSTR;
typedef CONST TCHAR *LPCTSTR, *PCTSTR;
/*typedef CONST CHAR *LPCSTR, *PCSTR;*/


typedef WORD                ATOM;

/*Определения из WinNT.h*/
/*
typedef union _LARGE_INTEGER {
    struct {
        DWORD LowPart;
        LONG HighPart;
    };
    struct {
        DWORD LowPart;
        LONG HighPart;
    } u;
//    LONGLONG QuadPart;
} LARGE_INTEGER;
*/
typedef struct _LARGE_INTEGER {
        DWORD LowPart;
        LONG HighPart;
} LARGE_INTEGER;

//
// Locally Unique Identifier
//

typedef struct _LUID {
    DWORD LowPart;
    LONG HighPart;
} LUID, *PLUID;
