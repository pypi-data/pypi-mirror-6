/* vim: ft=swig
*/

/**/
/* Algorithm IDs and Flags*/
/**/

/* ALG_ID crackers*/
/*#define GET_ALG_CLASS(x)                (x & (7 << 13))*/
/*#define GET_ALG_TYPE(x)                 (x & (15 << 9))*/
/*#define GET_ALG_SID(x)                  (x & (511))*/

/* Algorithm classes*/
#define ALG_CLASS_ANY                   (0)
#define ALG_CLASS_SIGNATURE             (1 << 13)
#define ALG_CLASS_MSG_ENCRYPT           (2 << 13)
#define ALG_CLASS_DATA_ENCRYPT          (3 << 13)
#define ALG_CLASS_HASH                  (4 << 13)
#define ALG_CLASS_KEY_EXCHANGE          (5 << 13)
#define ALG_CLASS_ALL                   (7 << 13)

/* Algorithm types*/
#define ALG_TYPE_ANY                    (0)
#define ALG_TYPE_DSS                    (1 << 9)
#define ALG_TYPE_RSA                    (2 << 9)
#define ALG_TYPE_BLOCK                  (3 << 9)
#define ALG_TYPE_STREAM                 (4 << 9)
#define ALG_TYPE_DH                     (5 << 9)
#define ALG_TYPE_SECURECHANNEL          (6 << 9)

/* Generic sub-ids*/
#define ALG_SID_ANY                     (0)

/* Some RSA sub-ids*/
#define ALG_SID_RSA_ANY                 0
#define ALG_SID_RSA_PKCS                1
#define ALG_SID_RSA_MSATWORK            2
#define ALG_SID_RSA_ENTRUST             3
#define ALG_SID_RSA_PGP                 4

/* Some DSS sub-ids*/
/**/
#define ALG_SID_DSS_ANY                 0
#define ALG_SID_DSS_PKCS                1
#define ALG_SID_DSS_DMS                 2

/* Block cipher sub ids*/
/* DES sub_ids */
#define ALG_SID_DES                     1
#define ALG_SID_3DES                    3
#define ALG_SID_DESX                    4
#define ALG_SID_IDEA                    5
#define ALG_SID_CAST                    6
#define ALG_SID_SAFERSK64               7
#define ALG_SID_SAFERSK128              8
#define ALG_SID_3DES_112                9
#define ALG_SID_CYLINK_MEK              12
#define ALG_SID_RC5                     13
#define ALG_SID_AES_128                 14
#define ALG_SID_AES_192                 15
#define ALG_SID_AES_256                 16
#define ALG_SID_AES                     17

/* Fortezza sub-ids */
#define ALG_SID_SKIPJACK                10
#define ALG_SID_TEK                     11

/* KP_MODE*/
#define CRYPT_MODE_CBCI                 6       /* ANSI CBC Interleaved*/
#define CRYPT_MODE_CFBP                 7       /* ANSI CFB Pipelined*/
#define CRYPT_MODE_OFBP                 8       /* ANSI OFB Pipelined*/
#define CRYPT_MODE_CBCOFM               9       /* ANSI CBC + OF Masking*/
#define CRYPT_MODE_CBCOFMI              10      /* ANSI CBC + OFM Interleaved*/

// RC2 sub-ids
#define ALG_SID_RC2                     2

// Stream cipher sub-ids
#define ALG_SID_RC4                     1
#define ALG_SID_SEAL                    2

/* Diffie-Hellman sub-ids*/
#define ALG_SID_DH_SANDF                1
#define ALG_SID_DH_EPHEM                2
#define ALG_SID_AGREED_KEY_ANY          3
#define ALG_SID_KEA                     4

/* Hash sub ids*/
#define ALG_SID_MD2                     1
#define ALG_SID_MD4                     2
#define ALG_SID_MD5                     3
#define ALG_SID_SHA                     4
#define ALG_SID_SHA1                    4
#define ALG_SID_MAC                     5
#define ALG_SID_RIPEMD                  6
#define ALG_SID_RIPEMD160               7
#define ALG_SID_SSL3SHAMD5              8
#define ALG_SID_HMAC                    9
#define	ALG_SID_TLS1PRF					10

/* secure channel sub ids*/
#define ALG_SID_SSL3_MASTER             1
#define ALG_SID_SCHANNEL_MASTER_HASH    2
#define ALG_SID_SCHANNEL_MAC_KEY        3
#define ALG_SID_PCT1_MASTER             4
#define ALG_SID_SSL2_MASTER             5
#define ALG_SID_TLS1_MASTER             6
#define ALG_SID_SCHANNEL_ENC_KEY        7

/* Our silly example sub-id*/
#define ALG_SID_EXAMPLE                 80

/* algorithm identifier definitions*/
#define CALG_MD2                (ALG_CLASS_HASH | ALG_TYPE_ANY | ALG_SID_MD2)
#define CALG_MD4                (ALG_CLASS_HASH | ALG_TYPE_ANY | ALG_SID_MD4)
#define CALG_MD5                (ALG_CLASS_HASH | ALG_TYPE_ANY | ALG_SID_MD5)
#define CALG_SHA                (ALG_CLASS_HASH | ALG_TYPE_ANY | ALG_SID_SHA)
#define CALG_SHA1               (ALG_CLASS_HASH | ALG_TYPE_ANY | ALG_SID_SHA1)
#define CALG_MAC                (ALG_CLASS_HASH | ALG_TYPE_ANY | ALG_SID_MAC)
#define CALG_RSA_SIGN           (ALG_CLASS_SIGNATURE | ALG_TYPE_RSA | ALG_SID_RSA_ANY)
#define CALG_DSS_SIGN           (ALG_CLASS_SIGNATURE | ALG_TYPE_DSS | ALG_SID_DSS_ANY)
#define CALG_RSA_KEYX           (ALG_CLASS_KEY_EXCHANGE|ALG_TYPE_RSA|ALG_SID_RSA_ANY)
#define CALG_DES                (ALG_CLASS_DATA_ENCRYPT|ALG_TYPE_BLOCK|ALG_SID_DES)
#define CALG_3DES_112           (ALG_CLASS_DATA_ENCRYPT|ALG_TYPE_BLOCK|ALG_SID_3DES_112)
#define CALG_3DES               (ALG_CLASS_DATA_ENCRYPT|ALG_TYPE_BLOCK|ALG_SID_3DES)
#define CALG_DESX               (ALG_CLASS_DATA_ENCRYPT|ALG_TYPE_BLOCK|ALG_SID_DESX)
#define CALG_RC2				(ALG_CLASS_DATA_ENCRYPT|ALG_TYPE_BLOCK|ALG_SID_RC2)
#define CALG_RC4				(ALG_CLASS_DATA_ENCRYPT|ALG_TYPE_STREAM|ALG_SID_RC4)
#define CALG_SEAL				(ALG_CLASS_DATA_ENCRYPT|ALG_TYPE_STREAM|ALG_SID_SEAL)
#define CALG_DH_SF              (ALG_CLASS_KEY_EXCHANGE|ALG_TYPE_DH|ALG_SID_DH_SANDF)
#define CALG_DH_EPHEM			(ALG_CLASS_KEY_EXCHANGE|ALG_TYPE_DH|ALG_SID_DH_EPHEM)
#define CALG_AGREEDKEY_ANY		(ALG_CLASS_KEY_EXCHANGE|ALG_TYPE_DH|ALG_SID_AGREED_KEY_ANY)
#define CALG_KEA_KEYX			(ALG_CLASS_KEY_EXCHANGE|ALG_TYPE_DH|ALG_SID_KEA)
#define CALG_HUGHES_MD5         (ALG_CLASS_KEY_EXCHANGE|ALG_TYPE_ANY|ALG_SID_MD5)
#define CALG_SKIPJACK			(ALG_CLASS_DATA_ENCRYPT|ALG_TYPE_BLOCK|ALG_SID_SKIPJACK)
#define CALG_TEK				(ALG_CLASS_DATA_ENCRYPT|ALG_TYPE_BLOCK|ALG_SID_TEK)
#define CALG_CYLINK_MEK         (ALG_CLASS_DATA_ENCRYPT|ALG_TYPE_BLOCK|ALG_SID_CYLINK_MEK)
#define CALG_SSL3_SHAMD5        (ALG_CLASS_HASH | ALG_TYPE_ANY | ALG_SID_SSL3SHAMD5)
#define CALG_SSL3_MASTER        (ALG_CLASS_MSG_ENCRYPT|ALG_TYPE_SECURECHANNEL|ALG_SID_SSL3_MASTER)
#define CALG_SCHANNEL_MASTER_HASH   (ALG_CLASS_MSG_ENCRYPT|ALG_TYPE_SECURECHANNEL|ALG_SID_SCHANNEL_MASTER_HASH)
#define CALG_SCHANNEL_MAC_KEY   (ALG_CLASS_MSG_ENCRYPT|ALG_TYPE_SECURECHANNEL|ALG_SID_SCHANNEL_MAC_KEY)
#define CALG_SCHANNEL_ENC_KEY   (ALG_CLASS_MSG_ENCRYPT|ALG_TYPE_SECURECHANNEL|ALG_SID_SCHANNEL_ENC_KEY)
#define CALG_PCT1_MASTER        (ALG_CLASS_MSG_ENCRYPT|ALG_TYPE_SECURECHANNEL|ALG_SID_PCT1_MASTER)
#define CALG_SSL2_MASTER        (ALG_CLASS_MSG_ENCRYPT|ALG_TYPE_SECURECHANNEL|ALG_SID_SSL2_MASTER)
#define CALG_TLS1_MASTER        (ALG_CLASS_MSG_ENCRYPT|ALG_TYPE_SECURECHANNEL|ALG_SID_TLS1_MASTER)
#define CALG_RC5                (ALG_CLASS_DATA_ENCRYPT|ALG_TYPE_BLOCK|ALG_SID_RC5)
#define CALG_HMAC				(ALG_CLASS_HASH | ALG_TYPE_ANY | ALG_SID_HMAC)
#define CALG_TLS1PRF			(ALG_CLASS_HASH | ALG_TYPE_ANY | ALG_SID_TLS1PRF)

/* resource number for signatures in the CSP*/
#define	SIGNATURE_RESOURCE_NUMBER	0x29A

/* dwFlags definitions for CryptAcquireContext*/
#define CRYPT_VERIFYCONTEXT     0xF0000000u
#define CRYPT_NEWKEYSET         0x00000008
#define CRYPT_DELETEKEYSET      0x00000010
#define CRYPT_MACHINE_KEYSET    0x00000020
#define CRYPT_SILENT            0x00000040

/* dwFlag definitions for CryptGenKey*/
#define CRYPT_EXPORTABLE        0x00000001
#define CRYPT_USER_PROTECTED    0x00000002
#define CRYPT_CREATE_SALT       0x00000004
#define CRYPT_UPDATE_KEY        0x00000008
#define CRYPT_NO_SALT           0x00000010
#define CRYPT_PREGEN            0x00000040
#define CRYPT_RECIPIENT         0x00000010
#define CRYPT_INITIATOR         0x00000040
#define CRYPT_ONLINE            0x00000080
#define CRYPT_SF                0x00000100
#define CRYPT_CREATE_IV         0x00000200
#define CRYPT_KEK               0x00000400
#define CRYPT_DATA_KEY          0x00000800
#define	CRYPT_VOLATILE          0x00001000
#define	CRYPT_SGCKEY            0x00002000
#define CRYPT_ARCHIVABLE        0x00004000

/* dwFlags definitions for CryptDeriveKey*/
#define	CRYPT_SERVER			0x00000400

#define KEY_LENGTH_MASK         0xFFFF0000u

/* dwFlag definitions for CryptExportKey*/
#define CRYPT_Y_ONLY            0x00000001
#define CRYPT_SSL2_FALLBACK     0x00000002
#define CRYPT_DESTROYKEY        0x00000004
#define CRYPT_OAEP              0x00000040  /* used with RSA encryptions/decryptions*/
                                            /* CryptExportKey, CryptImportKey,*/
                                            /* CryptEncrypt and CryptDecrypt*/

#define CRYPT_BLOB_VER3         0x00000080  /* export version 3 of a blob type*/

/* dwFlags definitions for CryptCreateHash*/
#define CRYPT_SECRETDIGEST      0x00000001

/* dwFlags definitions for CryptHashSessionKey*/
#define CRYPT_LITTLE_ENDIAN     0x00000001

/* dwFlags definitions for CryptSignHash and CryptVerifySignature*/
#define	CRYPT_NOHASHOID         0x00000001
#define	CRYPT_TYPE2_FORMAT      0x00000002
#define	CRYPT_X931_FORMAT       0x00000004

/* dwFlag definitions for CryptSetProviderEx and CryptGetDefaultProvider*/
#define CRYPT_MACHINE_DEFAULT   0x00000001
#define CRYPT_USER_DEFAULT      0x00000002
#define CRYPT_DELETE_DEFAULT    0x00000004

/* exported key blob definitions*/
#define SIMPLEBLOB              0x1
#define PUBLICKEYBLOB           0x6
#define PRIVATEKEYBLOB          0x7
#define PLAINTEXTKEYBLOB        0x8
#define OPAQUEKEYBLOB           0x9
#define PUBLICKEYBLOBEX         0xA
#define SYMMETRICWRAPKEYBLOB    0xB

#define AT_KEYEXCHANGE          1
#define AT_SIGNATURE            2

#define CRYPT_USERDATA          1

/* dwParam*/
#define KP_IV                   1       /* Initialization vector*/
#define KP_SALT                 2       /* Salt value*/
#define KP_PADDING              3       /* Padding values*/
#define KP_MODE                 4       /* Mode of the cipher*/
#define KP_MODE_BITS            5       /* Number of bits to feedback*/
#define KP_PERMISSIONS          6       /* Key permissions DWORD*/
#define KP_ALGID                7       /* Key algorithm*/
#define KP_BLOCKLEN             8       /* Block size of the cipher*/
#define KP_KEYLEN               9       /* Length of key in bits*/
#define KP_SALT_EX              10      /* Length of salt in bytes*/
#define KP_P                    11      /* DSS/Diffie-Hellman P value*/
#define KP_G                    12      /* DSS/Diffie-Hellman G value*/
#define KP_Q                    13      /* DSS Q value*/
#define KP_X                    14      /* Diffie-Hellman X value*/
#define KP_Y                    15      /* Y value*/
#define KP_RA                   16      /* Fortezza RA value*/
#define KP_RB                   17      /* Fortezza RB value*/
#define KP_INFO                 18      /* for putting information into an RSA envelope*/
#define KP_EFFECTIVE_KEYLEN     19      /* setting and getting RC2 effective key length*/
#define KP_SCHANNEL_ALG	        20      /* for setting the Secure Channel algorithms*/
#define KP_CLIENT_RANDOM		21      /* for setting the Secure Channel client random data*/
#define KP_SERVER_RANDOM		22      /* for setting the Secure Channel server random data*/
#define	KP_RP					23
#define	KP_PRECOMP_MD5			24
#define	KP_PRECOMP_SHA			25
#define KP_CERTIFICATE          26      /* for setting Secure Channel certificate data (PCT1)*/
#define KP_CLEAR_KEY            27      /* for setting Secure Channel clear key data (PCT1)*/
#define KP_PUB_EX_LEN           28
#define KP_PUB_EX_VAL           29
#define KP_KEYVAL				30
#define KP_ADMIN_PIN            31
#define KP_KEYEXCHANGE_PIN      32
#define KP_SIGNATURE_PIN        33
#define	KP_PREHASH              34

#define	KP_OAEP_PARAMS          36      /* for setting OAEP params on RSA keys*/
#define	KP_CMS_KEY_INFO			37
#define	KP_CMS_DH_KEY_INFO      38
#define KP_PUB_PARAMS           39      /* for setting public parameters*/
#define KP_VERIFY_PARAMS        40      /* for verifying DSA and DH parameters*/
#define KP_HIGHEST_VERSION      41      /* for TLS protocol version setting*/

/* KP_PADDING*/
#define PKCS5_PADDING           1       /* PKCS 5 (sec 6.2) padding method*/
#define RANDOM_PADDING			2
#define	ZERO_PADDING			3

/* KP_MODE*/
#define CRYPT_MODE_CBC          1       /* Cipher block chaining*/
#define CRYPT_MODE_ECB          2       /* Electronic code book*/
#define CRYPT_MODE_CFB          4       /* Cipher feedback mode*/
#define CRYPT_MODE_CTS          5       /* Ciphertext stealing mode*/

/* KP_PERMISSIONS*/
#define CRYPT_ENCRYPT           0x0001  /* Allow encryption*/
#define CRYPT_DECRYPT           0x0002  /* Allow decryption*/
#define CRYPT_EXPORT            0x0004  /* Allow key to be exported*/
#define CRYPT_READ              0x0008  /* Allow parameters to be read*/
#define CRYPT_WRITE             0x0010  /* Allow parameters to be set*/
#define CRYPT_MAC               0x0020  /* Allow MACs to be used with key*/
#define CRYPT_EXPORT_KEY        0x0040  /* Allow key to be used for exporting keys*/
#define CRYPT_IMPORT_KEY        0x0080  /* Allow key to be used for importing keys*/

#define HP_ALGID                0x0001  /* Hash algorithm*/
#define HP_HASHVAL              0x0002  /* Hash value*/
#define HP_HASHSIZE             0x0004  /* Hash value size*/
#define HP_HMAC_INFO            0x0005  /* information for creating an HMAC*/
#define HP_TLS1PRF_LABEL        0x0006  /* label for TLS1 PRF*/
#define HP_TLS1PRF_SEED         0x0007  /* seed for TLS1 PRF*/

#define CRYPT_FAILED            FALSE
#define CRYPT_SUCCEED           TRUE

#define RCRYPT_SUCCEEDED(rt)     ((rt) == CRYPT_SUCCEED)
#define RCRYPT_FAILED(rt)        ((rt) == CRYPT_FAILED)

/**/
/* CryptGetProvParam*/
/**/
#define PP_ENUMALGS             1
#define PP_ENUMCONTAINERS       2
#define PP_IMPTYPE              3
#define PP_NAME                 4
#define PP_VERSION              5
#define PP_CONTAINER            6
#define PP_CHANGE_PASSWORD      7
#define PP_KEYSET_SEC_DESCR     8       /* get/set security descriptor of keyset*/
#define PP_CERTCHAIN            9       /* for retrieving certificates from tokens*/
#define PP_KEY_TYPE_SUBTYPE     10
#define PP_PROVTYPE             16
#define PP_KEYSTORAGE           17
#define PP_APPLI_CERT           18
#define PP_SYM_KEYSIZE          19
#define PP_SESSION_KEYSIZE      20
#define PP_UI_PROMPT            21
#define PP_ENUMALGS_EX          22
#define PP_ENUMMANDROOTS		25
#define PP_ENUMELECTROOTS		26
#define	PP_KEYSET_TYPE			27
#define PP_ADMIN_PIN            31
#define PP_KEYEXCHANGE_PIN      32
#define PP_SIGNATURE_PIN        33
#define PP_SIG_KEYSIZE_INC      34
#define PP_KEYX_KEYSIZE_INC     35
#define PP_UNIQUE_CONTAINER     36
#define PP_SGC_INFO             37
#define PP_USE_HARDWARE_RNG     38
#define	PP_KEYSPEC              39
#define	PP_ENUMEX_SIGNING_PROT  40
#define PP_CRYPT_COUNT_KEY_USE  41

#define PP_USER_CERTSTORE       42
#define PP_SMARTCARD_READER     43
#define PP_SMARTCARD_GUID       45
#define PP_ROOT_CERTSTORE       46

#define CRYPT_FIRST             1
#define CRYPT_NEXT              2
#define CRYPT_SGC_ENUM			4

#define CRYPT_IMPL_HARDWARE     1
#define CRYPT_IMPL_SOFTWARE     2
#define CRYPT_IMPL_MIXED        3
#define CRYPT_IMPL_UNKNOWN      4
#define CRYPT_IMPL_REMOVABLE    8

/* key storage flags*/
#define CRYPT_SEC_DESCR         0x00000001
#define CRYPT_PSTORE            0x00000002
#define CRYPT_UI_PROMPT         0x00000004

/* protocol flags*/
#define CRYPT_FLAG_PCT1         0x0001
#define CRYPT_FLAG_SSL2         0x0002
#define CRYPT_FLAG_SSL3         0x0004
#define CRYPT_FLAG_TLS1         0x0008
#define CRYPT_FLAG_IPSEC        0x0010
#define CRYPT_FLAG_SIGNING      0x0020

/* SGC flags*/
#define CRYPT_SGC               0x0001
#define CRYPT_FASTSGC           0x0002

/**/
/* CryptSetProvParam*/
/**/
#define PP_CLIENT_HWND          1
#define PP_CONTEXT_INFO			11
#define	PP_KEYEXCHANGE_KEYSIZE	12
#define	PP_SIGNATURE_KEYSIZE    13
#define PP_KEYEXCHANGE_ALG      14
#define PP_SIGNATURE_ALG        15
#define PP_DELETEKEY            24

#define PROV_RSA_FULL           1

//
// Provider friendly names
//
#define MS_DEF_PROV           "Microsoft Base Cryptographic Provider v1.0"
/*#define MS_DEF_PROV_A           "Microsoft Base Cryptographic Provider v1.0"*/
/*#define MS_DEF_PROV_W           L"Microsoft Base Cryptographic Provider v1.0"*/
/*#ifdef UNICODE*/
/*#define MS_DEF_PROV             MS_DEF_PROV_W*/
/*#else*/
/*#define MS_DEF_PROV             MS_DEF_PROV_A*/
/*#endif*/

#define MAXUIDLEN               64

/* Exponentiation Offload Reg Location*/
#define EXPO_OFFLOAD_REG_VALUE "ExpoOffload"
#define EXPO_OFFLOAD_FUNC_NAME "OffloadModExpo"

#define CUR_BLOB_VERSION        2

//+-------------------------------------------------------------------------
//  Enhanced Key Usage (Purpose) Object Identifiers
//--------------------------------------------------------------------------
#define szOID_PKIX_KP                   "1.3.6.1.5.5.7.3"

// Consistent key usage bits: DIGITAL_SIGNATURE, KEY_ENCIPHERMENT
// or KEY_AGREEMENT
#define szOID_PKIX_KP_SERVER_AUTH       "1.3.6.1.5.5.7.3.1"

// Consistent key usage bits: DIGITAL_SIGNATURE
#define szOID_PKIX_KP_CLIENT_AUTH       "1.3.6.1.5.5.7.3.2"

// Consistent key usage bits: DIGITAL_SIGNATURE
#define szOID_PKIX_KP_CODE_SIGNING      "1.3.6.1.5.5.7.3.3"

// Consistent key usage bits: DIGITAL_SIGNATURE, NON_REPUDIATION and/or
// (KEY_ENCIPHERMENT or KEY_AGREEMENT)
#define szOID_PKIX_KP_EMAIL_PROTECTION  "1.3.6.1.5.5.7.3.4"

// Consistent key usage bits: DIGITAL_SIGNATURE and/or
// (KEY_ENCIPHERMENT or KEY_AGREEMENT)
#define szOID_PKIX_KP_IPSEC_END_SYSTEM  "1.3.6.1.5.5.7.3.5"

// Consistent key usage bits: DIGITAL_SIGNATURE and/or
// (KEY_ENCIPHERMENT or KEY_AGREEMENT)
#define szOID_PKIX_KP_IPSEC_TUNNEL      "1.3.6.1.5.5.7.3.6"

// Consistent key usage bits: DIGITAL_SIGNATURE and/or
// (KEY_ENCIPHERMENT or KEY_AGREEMENT)
#define szOID_PKIX_KP_IPSEC_USER        "1.3.6.1.5.5.7.3.7"

// Consistent key usage bits: DIGITAL_SIGNATURE or NON_REPUDIATION
#define szOID_PKIX_KP_TIMESTAMP_SIGNING "1.3.6.1.5.5.7.3.8"


// IKE (Internet Key Exchange) Intermediate KP for an IPsec end entity.
// Defined in draft-ietf-ipsec-pki-req-04.txt, December 14, 1999.
#define szOID_IPSEC_KP_IKE_INTERMEDIATE "1.3.6.1.5.5.8.2.2"

//+-------------------------------------------------------------------------
//  Microsoft Enhanced Key Usage (Purpose) Object Identifiers
//+-------------------------------------------------------------------------

//  Signer of CTLs
#define szOID_KP_CTL_USAGE_SIGNING      "1.3.6.1.4.1.311.10.3.1"

//  Signer of TimeStamps
#define szOID_KP_TIME_STAMP_SIGNING     "1.3.6.1.4.1.311.10.3.2"

#ifndef szOID_SERVER_GATED_CRYPTO
#define szOID_SERVER_GATED_CRYPTO       "1.3.6.1.4.1.311.10.3.3"
#endif

#ifndef szOID_SGC_NETSCAPE
#define szOID_SGC_NETSCAPE              "2.16.840.1.113730.4.1"
#endif

#define szOID_KP_EFS                    "1.3.6.1.4.1.311.10.3.4"
#define szOID_EFS_RECOVERY              "1.3.6.1.4.1.311.10.3.4.1"

// Can use Windows Hardware Compatible (WHQL)
#define szOID_WHQL_CRYPTO               "1.3.6.1.4.1.311.10.3.5"

// Signed by the NT5 build lab
#define szOID_NT5_CRYPTO                "1.3.6.1.4.1.311.10.3.6"

// Signed by and OEM of WHQL
#define szOID_OEM_WHQL_CRYPTO           "1.3.6.1.4.1.311.10.3.7"

// Signed by the Embedded NT
#define szOID_EMBEDDED_NT_CRYPTO        "1.3.6.1.4.1.311.10.3.8"

// Signer of a CTL containing trusted roots
#define szOID_ROOT_LIST_SIGNER      "1.3.6.1.4.1.311.10.3.9"

// Can sign cross-cert and subordinate CA requests with qualified
// subordination (name constraints, policy mapping, etc.)
#define szOID_KP_QUALIFIED_SUBORDINATION    "1.3.6.1.4.1.311.10.3.10"

// Can be used to encrypt/recover escrowed keys
#define szOID_KP_KEY_RECOVERY               "1.3.6.1.4.1.311.10.3.11"

// Signer of documents
#define szOID_KP_DOCUMENT_SIGNING           "1.3.6.1.4.1.311.10.3.12"

// The default WinVerifyTrust Authenticode policy is to treat all time stamped
// signatures as being valid forever. This OID limits the valid lifetime of the
// signature to the lifetime of the certificate. This allows timestamped
// signatures to expire. Normally this OID will be used in conjunction with
// szOID_PKIX_KP_CODE_SIGNING to indicate new time stamp semantics should be
// used. Support for this OID was added in WXP.
#define szOID_KP_LIFETIME_SIGNING           "1.3.6.1.4.1.311.10.3.13"

#ifndef szOID_DRM
#define szOID_DRM                       "1.3.6.1.4.1.311.10.5.1"
#endif


// Microsoft DRM EKU
#ifndef szOID_DRM_INDIVIDUALIZATION
#define szOID_DRM_INDIVIDUALIZATION "1.3.6.1.4.1.311.10.5.2"
#endif


#ifndef szOID_LICENSES
#define szOID_LICENSES                  "1.3.6.1.4.1.311.10.6.1"
#endif

#ifndef szOID_LICENSE_SERVER
#define szOID_LICENSE_SERVER            "1.3.6.1.4.1.311.10.6.2"
#endif

#ifndef szOID_KP_SMARTCARD_LOGON
#define szOID_KP_SMARTCARD_LOGON        "1.3.6.1.4.1.311.20.2.2"
#endif

//+-------------------------------------------------------------------------
//  Microsoft Attribute Object Identifiers
//+-------------------------------------------------------------------------
#define szOID_YESNO_TRUST_ATTR          "1.3.6.1.4.1.311.10.4.1"

//+-------------------------------------------------------------------------
//  Qualifiers that may be part of the szOID_CERT_POLICIES and
//  szOID_CERT_POLICIES95 extensions
//+-------------------------------------------------------------------------
#define szOID_PKIX_POLICY_QUALIFIER_CPS               "1.3.6.1.5.5.7.2.1"
#define szOID_PKIX_POLICY_QUALIFIER_USERNOTICE        "1.3.6.1.5.5.7.2.2"

// OID for old qualifer
#define szOID_CERT_POLICIES_95_QUALIFIER1             "2.16.840.1.113733.1.7.1.1"

#define szOID_CERT_EXTENSIONS           "1.3.6.1.4.1.311.2.1.14"

//+-------------------------------------------------------------------------
//  Extension Object Identifiers
//--------------------------------------------------------------------------
#define szOID_AUTHORITY_KEY_IDENTIFIER  "2.5.29.1"
#define szOID_KEY_ATTRIBUTES            "2.5.29.2"
#define szOID_CERT_POLICIES_95          "2.5.29.3"
#define szOID_KEY_USAGE_RESTRICTION     "2.5.29.4"
#define szOID_SUBJECT_ALT_NAME          "2.5.29.7"
#define szOID_ISSUER_ALT_NAME           "2.5.29.8"
#define szOID_BASIC_CONSTRAINTS         "2.5.29.10"
#define szOID_KEY_USAGE                 "2.5.29.15"
#define szOID_PRIVATEKEY_USAGE_PERIOD   "2.5.29.16"
#define szOID_BASIC_CONSTRAINTS2        "2.5.29.19"

#define szOID_CERT_POLICIES             "2.5.29.32"
#define szOID_ANY_CERT_POLICY           "2.5.29.32.0"

#define szOID_AUTHORITY_KEY_IDENTIFIER2 "2.5.29.35"
#define szOID_SUBJECT_KEY_IDENTIFIER    "2.5.29.14"
#define szOID_SUBJECT_ALT_NAME2         "2.5.29.17"
#define szOID_ISSUER_ALT_NAME2          "2.5.29.18"
#define szOID_CRL_REASON_CODE           "2.5.29.21"
#define szOID_REASON_CODE_HOLD          "2.5.29.23"
#define szOID_CRL_DIST_POINTS           "2.5.29.31"
#define szOID_ENHANCED_KEY_USAGE        "2.5.29.37"

// Application Policies extension -- same encoding as szOID_CERT_POLICIES
#define szOID_APPLICATION_CERT_POLICIES     "1.3.6.1.4.1.311.21.10"

#define szOID_ANY_ENHANCED_KEY_USAGE    "2.5.29.37.0"

// szOID_CRL_NUMBER -- Base CRLs only.  Monotonically increasing sequence
// number for each CRL issued by a CA.
#define szOID_CRL_NUMBER                "2.5.29.20"
// szOID_DELTA_CRL_INDICATOR -- Delta CRLs only.  Marked critical.
// Contains the minimum base CRL Number that can be used with a delta CRL.
#define szOID_DELTA_CRL_INDICATOR       "2.5.29.27"
#define szOID_ISSUING_DIST_POINT        "2.5.29.28"
// szOID_FRESHEST_CRL -- Base CRLs only.  Formatted identically to a CDP
// extension that holds URLs to fetch the delta CRL.
#define szOID_FRESHEST_CRL              "2.5.29.46"
#define szOID_NAME_CONSTRAINTS          "2.5.29.30"

#ifndef szOID_CERTSRV_CA_VERSION
#define szOID_CERTSRV_CA_VERSION        "1.3.6.1.4.1.311.21.1"
#endif
#define szOID_CERTSRV_CROSSCA_VERSION          "1.3.6.1.4.1.311.21.22"

#define CRYPT_ASN_ENCODING          0x00000001
#define CRYPT_NDR_ENCODING          0x00000002
#define X509_ASN_ENCODING           0x00000001
#define X509_NDR_ENCODING           0x00000002
#define PKCS_7_ASN_ENCODING         0x00010000
#define PKCS_7_NDR_ENCODING         0x00020000

// Following are the definitions of various algorithm object identifiers
// RSA
#define szOID_RSA               "1.2.840.113549"
#define szOID_PKCS              "1.2.840.113549.1"
#define szOID_RSA_HASH          "1.2.840.113549.2"
#define szOID_RSA_ENCRYPT       "1.2.840.113549.3"

#define szOID_PKCS_1            "1.2.840.113549.1.1"
#define szOID_PKCS_2            "1.2.840.113549.1.2"
#define szOID_PKCS_3            "1.2.840.113549.1.3"
#define szOID_PKCS_4            "1.2.840.113549.1.4"
#define szOID_PKCS_5            "1.2.840.113549.1.5"
#define szOID_PKCS_6            "1.2.840.113549.1.6"
#define szOID_PKCS_7            "1.2.840.113549.1.7"
#define szOID_PKCS_8            "1.2.840.113549.1.8"
#define szOID_PKCS_9            "1.2.840.113549.1.9"
#define szOID_PKCS_10           "1.2.840.113549.1.10"
#define szOID_PKCS_12           "1.2.840.113549.1.12"

#define szOID_RSA_RSA           "1.2.840.113549.1.1.1"
#define szOID_RSA_MD2RSA        "1.2.840.113549.1.1.2"
#define szOID_RSA_MD4RSA        "1.2.840.113549.1.1.3"
#define szOID_RSA_MD5RSA        "1.2.840.113549.1.1.4"
#define szOID_RSA_SHA1RSA       "1.2.840.113549.1.1.5"
#define szOID_RSA_SETOAEP_RSA   "1.2.840.113549.1.1.6"

#define szOID_RSA_DH            "1.2.840.113549.1.3.1"

#define szOID_RSA_data          "1.2.840.113549.1.7.1"
#define szOID_RSA_signedData    "1.2.840.113549.1.7.2"
#define szOID_RSA_envelopedData "1.2.840.113549.1.7.3"
#define szOID_RSA_signEnvData   "1.2.840.113549.1.7.4"
#define szOID_RSA_digestedData  "1.2.840.113549.1.7.5"
#define szOID_RSA_hashedData    "1.2.840.113549.1.7.5"
#define szOID_RSA_encryptedData "1.2.840.113549.1.7.6"

#define szOID_RSA_emailAddr     "1.2.840.113549.1.9.1"
#define szOID_RSA_unstructName  "1.2.840.113549.1.9.2"
#define szOID_RSA_contentType   "1.2.840.113549.1.9.3"
#define szOID_RSA_messageDigest "1.2.840.113549.1.9.4"
#define szOID_RSA_signingTime   "1.2.840.113549.1.9.5"
#define szOID_RSA_counterSign   "1.2.840.113549.1.9.6"
#define szOID_RSA_challengePwd  "1.2.840.113549.1.9.7"
#define szOID_RSA_unstructAddr  "1.2.840.113549.1.9.8"
#define szOID_RSA_extCertAttrs  "1.2.840.113549.1.9.9"
#define szOID_RSA_certExtensions "1.2.840.113549.1.9.14"
#define szOID_RSA_SMIMECapabilities "1.2.840.113549.1.9.15"
#define szOID_RSA_preferSignedData "1.2.840.113549.1.9.15.1"

#define szOID_RSA_SMIMEalg              "1.2.840.113549.1.9.16.3"
#define szOID_RSA_SMIMEalgESDH          "1.2.840.113549.1.9.16.3.5"
#define szOID_RSA_SMIMEalgCMS3DESwrap   "1.2.840.113549.1.9.16.3.6"
#define szOID_RSA_SMIMEalgCMSRC2wrap    "1.2.840.113549.1.9.16.3.7"

#define szOID_RSA_MD2           "1.2.840.113549.2.2"
#define szOID_RSA_MD4           "1.2.840.113549.2.4"
#define szOID_RSA_MD5           "1.2.840.113549.2.5"

#define szOID_RSA_RC2CBC        "1.2.840.113549.3.2"
#define szOID_RSA_RC4           "1.2.840.113549.3.4"
#define szOID_RSA_DES_EDE3_CBC  "1.2.840.113549.3.7"
#define szOID_RSA_RC5_CBCPad    "1.2.840.113549.3.9"


#define szOID_ANSI_X942         "1.2.840.10046"
#define szOID_ANSI_X942_DH      "1.2.840.10046.2.1"

#define szOID_X957              "1.2.840.10040"
#define szOID_X957_DSA          "1.2.840.10040.4.1"
#define szOID_X957_SHA1DSA      "1.2.840.10040.4.3"

// ITU-T UsefulDefinitions
#define szOID_DS                "2.5"
#define szOID_DSALG             "2.5.8"
#define szOID_DSALG_CRPT        "2.5.8.1"
#define szOID_DSALG_HASH        "2.5.8.2"
#define szOID_DSALG_SIGN        "2.5.8.3"
#define szOID_DSALG_RSA         "2.5.8.1.1"
// NIST OSE Implementors' Workshop (OIW)
// http://nemo.ncsl.nist.gov/oiw/agreements/stable/OSI/12s_9506.w51
// http://nemo.ncsl.nist.gov/oiw/agreements/working/OSI/12w_9503.w51
#define szOID_OIW               "1.3.14"
// NIST OSE Implementors' Workshop (OIW) Security SIG algorithm identifiers
#define szOID_OIWSEC            "1.3.14.3.2"
#define szOID_OIWSEC_md4RSA     "1.3.14.3.2.2"
#define szOID_OIWSEC_md5RSA     "1.3.14.3.2.3"
#define szOID_OIWSEC_md4RSA2    "1.3.14.3.2.4"
#define szOID_OIWSEC_desECB     "1.3.14.3.2.6"
#define szOID_OIWSEC_desCBC     "1.3.14.3.2.7"
#define szOID_OIWSEC_desOFB     "1.3.14.3.2.8"
#define szOID_OIWSEC_desCFB     "1.3.14.3.2.9"
#define szOID_OIWSEC_desMAC     "1.3.14.3.2.10"
#define szOID_OIWSEC_rsaSign    "1.3.14.3.2.11"
#define szOID_OIWSEC_dsa        "1.3.14.3.2.12"
#define szOID_OIWSEC_shaDSA     "1.3.14.3.2.13"
#define szOID_OIWSEC_mdc2RSA    "1.3.14.3.2.14"
#define szOID_OIWSEC_shaRSA     "1.3.14.3.2.15"
#define szOID_OIWSEC_dhCommMod  "1.3.14.3.2.16"
#define szOID_OIWSEC_desEDE     "1.3.14.3.2.17"
#define szOID_OIWSEC_sha        "1.3.14.3.2.18"
#define szOID_OIWSEC_mdc2       "1.3.14.3.2.19"
#define szOID_OIWSEC_dsaComm    "1.3.14.3.2.20"
#define szOID_OIWSEC_dsaCommSHA "1.3.14.3.2.21"
#define szOID_OIWSEC_rsaXchg    "1.3.14.3.2.22"
#define szOID_OIWSEC_keyHashSeal "1.3.14.3.2.23"
#define szOID_OIWSEC_md2RSASign "1.3.14.3.2.24"
#define szOID_OIWSEC_md5RSASign "1.3.14.3.2.25"
#define szOID_OIWSEC_sha1       "1.3.14.3.2.26"
#define szOID_OIWSEC_dsaSHA1    "1.3.14.3.2.27"
#define szOID_OIWSEC_dsaCommSHA1 "1.3.14.3.2.28"
#define szOID_OIWSEC_sha1RSASign "1.3.14.3.2.29"
// NIST OSE Implementors' Workshop (OIW) Directory SIG algorithm identifiers
#define szOID_OIWDIR            "1.3.14.7.2"
#define szOID_OIWDIR_CRPT       "1.3.14.7.2.1"
#define szOID_OIWDIR_HASH       "1.3.14.7.2.2"
#define szOID_OIWDIR_SIGN       "1.3.14.7.2.3"
#define szOID_OIWDIR_md2        "1.3.14.7.2.2.1"
#define szOID_OIWDIR_md2RSA     "1.3.14.7.2.3.1"


// INFOSEC Algorithms
// joint-iso-ccitt(2) country(16) us(840) organization(1) us-government(101) dod(2) id-infosec(1)
#define szOID_INFOSEC                       "2.16.840.1.101.2.1"
#define szOID_INFOSEC_sdnsSignature         "2.16.840.1.101.2.1.1.1"
#define szOID_INFOSEC_mosaicSignature       "2.16.840.1.101.2.1.1.2"
#define szOID_INFOSEC_sdnsConfidentiality   "2.16.840.1.101.2.1.1.3"
#define szOID_INFOSEC_mosaicConfidentiality "2.16.840.1.101.2.1.1.4"
#define szOID_INFOSEC_sdnsIntegrity         "2.16.840.1.101.2.1.1.5"
#define szOID_INFOSEC_mosaicIntegrity       "2.16.840.1.101.2.1.1.6"
#define szOID_INFOSEC_sdnsTokenProtection   "2.16.840.1.101.2.1.1.7"
#define szOID_INFOSEC_mosaicTokenProtection "2.16.840.1.101.2.1.1.8"
#define szOID_INFOSEC_sdnsKeyManagement     "2.16.840.1.101.2.1.1.9"
#define szOID_INFOSEC_mosaicKeyManagement   "2.16.840.1.101.2.1.1.10"
#define szOID_INFOSEC_sdnsKMandSig          "2.16.840.1.101.2.1.1.11"
#define szOID_INFOSEC_mosaicKMandSig        "2.16.840.1.101.2.1.1.12"
#define szOID_INFOSEC_SuiteASignature       "2.16.840.1.101.2.1.1.13"
#define szOID_INFOSEC_SuiteAConfidentiality "2.16.840.1.101.2.1.1.14"
#define szOID_INFOSEC_SuiteAIntegrity       "2.16.840.1.101.2.1.1.15"
#define szOID_INFOSEC_SuiteATokenProtection "2.16.840.1.101.2.1.1.16"
#define szOID_INFOSEC_SuiteAKeyManagement   "2.16.840.1.101.2.1.1.17"
#define szOID_INFOSEC_SuiteAKMandSig        "2.16.840.1.101.2.1.1.18"
#define szOID_INFOSEC_mosaicUpdatedSig      "2.16.840.1.101.2.1.1.19"
#define szOID_INFOSEC_mosaicKMandUpdSig     "2.16.840.1.101.2.1.1.20"
#define szOID_INFOSEC_mosaicUpdatedInteg    "2.16.840.1.101.2.1.1.21"

// NIST Hash Algorithms
// joint-iso-itu-t(2) country(16) us(840) organization(1) gov(101) csor(3) nistalgorithm(4) hashalgs(2)

#define szOID_NIST_sha256                   "2.16.840.1.101.3.4.2.1"
#define szOID_NIST_sha384                   "2.16.840.1.101.3.4.2.2"
#define szOID_NIST_sha512                   "2.16.840.1.101.3.4.2.3"

// iso(1) member-body(2) us(840) 10045 signatures(4) sha1(1)
#define szOID_ECDSA_SHA1        "1.2.840.10045.4.1"

//+-------------------------------------------------------------------------
//  Object Identifiers for use with Auto Enrollment
//--------------------------------------------------------------------------
#define szOID_AUTO_ENROLL_CTL_USAGE     "1.3.6.1.4.1.311.20.1"

// Extension contain certificate type
#define szOID_ENROLL_CERTTYPE_EXTENSION "1.3.6.1.4.1.311.20.2"


#define szOID_CERT_MANIFOLD             "1.3.6.1.4.1.311.20.3"


//+-------------------------------------------------------------------------
//  Certificate versions
//--------------------------------------------------------------------------
#define CERT_V1     0
#define CERT_V2     1
#define CERT_V3     2

//  Certificate Information Flags
//--------------------------------------------------------------------------
#define CERT_INFO_VERSION_FLAG                      1
#define CERT_INFO_SERIAL_NUMBER_FLAG                2
#define CERT_INFO_SIGNATURE_ALGORITHM_FLAG          3
#define CERT_INFO_ISSUER_FLAG                       4
#define CERT_INFO_NOT_BEFORE_FLAG                   5
#define CERT_INFO_NOT_AFTER_FLAG                    6
#define CERT_INFO_SUBJECT_FLAG                      7
#define CERT_INFO_SUBJECT_PUBLIC_KEY_INFO_FLAG      8
#define CERT_INFO_ISSUER_UNIQUE_ID_FLAG             9
#define CERT_INFO_SUBJECT_UNIQUE_ID_FLAG            10
#define CERT_INFO_EXTENSION_FLAG                    11

#define CRYPT_ACQUIRE_CACHE_FLAG                0x00000001
#define CRYPT_ACQUIRE_USE_PROV_INFO_FLAG        0x00000002
#define CRYPT_ACQUIRE_COMPARE_KEY_FLAG          0x00000004

#define CRYPT_ACQUIRE_SILENT_FLAG               0x00000040

//+-------------------------------------------------------------------------
//  Certificate Request versions
//--------------------------------------------------------------------------
#define CERT_REQUEST_V1     0


//+-------------------------------------------------------------------------
// Certificate comparison functions
//--------------------------------------------------------------------------
#define CERT_COMPARE_MASK           0xFFFF
#define CERT_COMPARE_SHIFT          16
#define CERT_COMPARE_ANY            0
#define CERT_COMPARE_SHA1_HASH      1
#define CERT_COMPARE_NAME           2
#define CERT_COMPARE_ATTR           3
#define CERT_COMPARE_MD5_HASH       4
#define CERT_COMPARE_PROPERTY       5
#define CERT_COMPARE_PUBLIC_KEY     6
#define CERT_COMPARE_HASH           CERT_COMPARE_SHA1_HASH
#define CERT_COMPARE_NAME_STR_A     7
#define CERT_COMPARE_NAME_STR_W     8
#define CERT_COMPARE_KEY_SPEC       9
#define CERT_COMPARE_ENHKEY_USAGE   10
#define CERT_COMPARE_CTL_USAGE      CERT_COMPARE_ENHKEY_USAGE
#define CERT_COMPARE_SUBJECT_CERT   11
#define CERT_COMPARE_ISSUER_OF      12
#define CERT_COMPARE_EXISTING       13
#define CERT_COMPARE_SIGNATURE_HASH 14
#define CERT_COMPARE_KEY_IDENTIFIER 15
#define CERT_COMPARE_CERT_ID        16
#define CERT_COMPARE_CROSS_CERT_DIST_POINTS 17

#define CERT_COMPARE_PUBKEY_MD5_HASH 18

//+-------------------------------------------------------------------------
//  dwFindType
//
//  The dwFindType definition consists of two components:
//   - comparison function
//   - certificate information flag
//--------------------------------------------------------------------------
#define CERT_FIND_ANY           (CERT_COMPARE_ANY << CERT_COMPARE_SHIFT)
#define CERT_FIND_SHA1_HASH     (CERT_COMPARE_SHA1_HASH << CERT_COMPARE_SHIFT)
#define CERT_FIND_MD5_HASH      (CERT_COMPARE_MD5_HASH << CERT_COMPARE_SHIFT)
#define CERT_FIND_SIGNATURE_HASH (CERT_COMPARE_SIGNATURE_HASH << CERT_COMPARE_SHIFT)
#define CERT_FIND_KEY_IDENTIFIER (CERT_COMPARE_KEY_IDENTIFIER << CERT_COMPARE_SHIFT)
#define CERT_FIND_HASH          CERT_FIND_SHA1_HASH
#define CERT_FIND_PROPERTY      (CERT_COMPARE_PROPERTY << CERT_COMPARE_SHIFT)
#define CERT_FIND_PUBLIC_KEY    (CERT_COMPARE_PUBLIC_KEY << CERT_COMPARE_SHIFT)
#define CERT_FIND_SUBJECT_NAME  (CERT_COMPARE_NAME << CERT_COMPARE_SHIFT | \
                                 CERT_INFO_SUBJECT_FLAG)
#define CERT_FIND_SUBJECT_ATTR  (CERT_COMPARE_ATTR << CERT_COMPARE_SHIFT | \
                                 CERT_INFO_SUBJECT_FLAG)
#define CERT_FIND_ISSUER_NAME   (CERT_COMPARE_NAME << CERT_COMPARE_SHIFT | \
                                 CERT_INFO_ISSUER_FLAG)
#define CERT_FIND_ISSUER_ATTR   (CERT_COMPARE_ATTR << CERT_COMPARE_SHIFT | \
                                 CERT_INFO_ISSUER_FLAG)
#define CERT_FIND_SUBJECT_STR_A (CERT_COMPARE_NAME_STR_A << CERT_COMPARE_SHIFT | \
                                 CERT_INFO_SUBJECT_FLAG)
#define CERT_FIND_SUBJECT_STR_W (CERT_COMPARE_NAME_STR_W << CERT_COMPARE_SHIFT | \
                                 CERT_INFO_SUBJECT_FLAG)
#define CERT_FIND_SUBJECT_STR   CERT_FIND_SUBJECT_STR_W
#define CERT_FIND_ISSUER_STR_A  (CERT_COMPARE_NAME_STR_A << CERT_COMPARE_SHIFT | \
                                 CERT_INFO_ISSUER_FLAG)
#define CERT_FIND_ISSUER_STR_W  (CERT_COMPARE_NAME_STR_W << CERT_COMPARE_SHIFT | \
                                 CERT_INFO_ISSUER_FLAG)
#define CERT_FIND_ISSUER_STR    CERT_FIND_ISSUER_STR_W
#define CERT_FIND_KEY_SPEC      (CERT_COMPARE_KEY_SPEC << CERT_COMPARE_SHIFT)
#define CERT_FIND_ENHKEY_USAGE  (CERT_COMPARE_ENHKEY_USAGE << CERT_COMPARE_SHIFT)
#define CERT_FIND_CTL_USAGE     CERT_FIND_ENHKEY_USAGE

#define CERT_FIND_SUBJECT_CERT  (CERT_COMPARE_SUBJECT_CERT << CERT_COMPARE_SHIFT)
#define CERT_FIND_ISSUER_OF     (CERT_COMPARE_ISSUER_OF << CERT_COMPARE_SHIFT)
#define CERT_FIND_EXISTING      (CERT_COMPARE_EXISTING << CERT_COMPARE_SHIFT)
#define CERT_FIND_CERT_ID       (CERT_COMPARE_CERT_ID << CERT_COMPARE_SHIFT)
#define CERT_FIND_CROSS_CERT_DIST_POINTS \
                    (CERT_COMPARE_CROSS_CERT_DIST_POINTS << CERT_COMPARE_SHIFT)


#define CERT_FIND_PUBKEY_MD5_HASH \
                    (CERT_COMPARE_PUBKEY_MD5_HASH << CERT_COMPARE_SHIFT)

#define CERT_DIGITAL_SIGNATURE_KEY_USAGE     0x80
#define CERT_NON_REPUDIATION_KEY_USAGE       0x40
#define CERT_KEY_ENCIPHERMENT_KEY_USAGE      0x20
#define CERT_DATA_ENCIPHERMENT_KEY_USAGE     0x10
#define CERT_KEY_AGREEMENT_KEY_USAGE         0x08
#define CERT_KEY_CERT_SIGN_KEY_USAGE         0x04
#define CERT_OFFLINE_CRL_SIGN_KEY_USAGE      0x02
#define CERT_CRL_SIGN_KEY_USAGE              0x02
#define CERT_ENCIPHER_ONLY_KEY_USAGE         0x01
