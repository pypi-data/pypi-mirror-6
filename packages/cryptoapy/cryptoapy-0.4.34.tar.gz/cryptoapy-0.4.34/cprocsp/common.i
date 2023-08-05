/* vim: ft=swig
*/

%include "rcobj.hpp"

typedef ULONG_PTR HCRYPTPROV;
typedef ULONG_PTR HCRYPTKEY;
typedef ULONG_PTR HCRYPTHASH;

typedef unsigned int ALG_ID;

/*+-------------------------------------------------------------------------*/
/*  CRYPTOAPI BLOB definitions*/
/*--------------------------------------------------------------------------*/
/*typedef struct _CRYPTOAPI_BLOB {*/
    /*DWORD   cbData;*/
    /*BYTE    *pbData;*/
/*} CRYPT_INTEGER_BLOB, *PCRYPT_INTEGER_BLOB,*/
/*CRYPT_UINT_BLOB, *PCRYPT_UINT_BLOB,*/
/*CRYPT_OBJID_BLOB, *PCRYPT_OBJID_BLOB,*/
/*CERT_NAME_BLOB, *PCERT_NAME_BLOB,*/
/*CERT_RDN_VALUE_BLOB, *PCERT_RDN_VALUE_BLOB,*/
/*CERT_BLOB, *PCERT_BLOB,*/
/*CRL_BLOB, *PCRL_BLOB,*/
/*DATA_BLOB, *PDATA_BLOB,*/
/*CRYPT_DATA_BLOB, *PCRYPT_DATA_BLOB,*/
/*CRYPT_HASH_BLOB, *PCRYPT_HASH_BLOB,*/
/*CRYPT_DIGEST_BLOB, *PCRYPT_DIGEST_BLOB,*/
/*CRYPT_DER_BLOB, *PCRYPT_DER_BLOB,*/
/*CRYPT_ATTR_BLOB, *PCRYPT_ATTR_BLOB;*/
typedef struct _CRYPTOAPI_BLOB {
    DWORD   cbData;
    BYTE    *pbData;
} CRYPTOAPI_BLOB, *PCRYPTOAPI_BLOB, CRYPT_UINT_BLOB, *PCRYPT_UINT_BLOB, CRYPT_OBJID_BLOB, *PCRYPT_OBJID_BLOB, CERT_NAME_BLOB, *PCERT_NAME_BLOB, CERT_RDN_VALUE_BLOB, *PCERT_RDN_VALUE_BLOB, CERT_BLOB, *PCERT_BLOB, CRL_BLOB, *PCRL_BLOB, DATA_BLOB, *PDATA_BLOB, CRYPT_DATA_BLOB, *PCRYPT_DATA_BLOB, CRYPT_HASH_BLOB, *PCRYPT_HASH_BLOB, CRYPT_DIGEST_BLOB, *PCRYPT_DIGEST_BLOB, CRYPT_DER_BLOB, *PCRYPT_DER_BLOB, CRYPT_ATTR_BLOB, *PCRYPT_ATTR_BLOB; 
/* structure for use with CryptSetKeyParam for CMS keys*/
typedef struct _CMS_DH_KEY_INFO {
    DWORD	        dwVersion;			/* sizeof(CMS_DH_KEY_INFO)*/
    ALG_ID          Algid;				/* algorithmm id for the key to be converted*/
    LPSTR           pszContentEncObjId; /* pointer to OID to hash in with Z*/
    CRYPT_DATA_BLOB PubInfo;            /* OPTIONAL - public information*/
    void            *pReserved;         /* reserved - should be NULL*/
} CMS_DH_KEY_INFO, *PCMS_DH_KEY_INFO;

//+-------------------------------------------------------------------------
//  In a CRYPT_BIT_BLOB the last byte may contain 0-7 unused bits. Therefore, the
//  overall bit length is cbData * 8 - cUnusedBits.
//--------------------------------------------------------------------------
typedef struct _CRYPT_BIT_BLOB {
    DWORD   cbData;
    BYTE    *pbData;
    DWORD   cUnusedBits;
} CRYPT_BIT_BLOB, *PCRYPT_BIT_BLOB;

//+-------------------------------------------------------------------------
//  Type used for any algorithm
//
//  Where the Parameters CRYPT_OBJID_BLOB is in its encoded representation. For most
//  algorithm types, the Parameters CRYPT_OBJID_BLOB is NULL (Parameters.cbData = 0).
//--------------------------------------------------------------------------
typedef struct _CRYPT_ALGORITHM_IDENTIFIER {
    LPSTR               pszObjId;
    CRYPT_OBJID_BLOB    Parameters;
} CRYPT_ALGORITHM_IDENTIFIER, *PCRYPT_ALGORITHM_IDENTIFIER;
