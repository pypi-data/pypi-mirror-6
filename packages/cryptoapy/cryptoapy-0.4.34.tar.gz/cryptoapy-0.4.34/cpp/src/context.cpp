#include "common.hpp"
#include "context.hpp"
#include "key.hpp"

Crypt::~Crypt() throw(CSPException) {
    LOG("Crypt::~Crypt(%p)\n", this);
    if (hprov) {
        LOG("    begin close %x\n", hprov);
        bool res = CryptReleaseContext(hprov, 0);
        if (!res) {
            DWORD err = GetLastError();
            LOG("     error closing context %x\n", err);
            throw CSPException("~Crypt: Couldn't release context", err);
        }
    }
    if (cont_name) {
        LOG("freeing cont_name(%p)\n", cont_name);
        delete[] cont_name;
    }
    if (pr_name) {
        LOG("freeing pr_name(%p)\n", pr_name);
        delete[] pr_name;
    }
    LOG("    Freed ctx %p (%x)\n", this, hprov);
}

DWORD Crypt::prov_type() {
    DWORD slen, type;
    if(!CryptGetProvParam( hprov, PP_PROVTYPE, NULL, &slen, 0)) {
        throw CSPException("Crypt.prov_type: Couldn't determine provider type data length");
    }

    if(slen != sizeof(DWORD)) {
        throw CSPException("Crypt.prov_type: Wrong size for binary data", -1);
    }

    if(!CryptGetProvParam( hprov, PP_PROVTYPE, (BYTE *)&type, &slen, 0)) {
        throw CSPException("Crypt.prov_type: Couldn't get provider type");
    }
    return type;
}

char *Crypt::prov_name() {
    char *s;
    DWORD slen;
    if(!CryptGetProvParam( hprov, PP_NAME, NULL, &slen, 0)) {
        throw CSPException("Crypt.prov_name: Couldn't determine provider name length");
    }

    s=new char[slen];

    if(!CryptGetProvParam( hprov, PP_NAME, (BYTE *)s, &slen, 0)) {
        delete[] s;
        throw CSPException("Crypt.prov_name: Couldn't get provider name");
    }
    return s;
}

char *Crypt::name() {
    char *s;
    DWORD slen;
    if(!CryptGetProvParam( hprov, PP_CONTAINER, NULL, &slen, 0)) {
        throw CSPException("Crypt.name: Couldn't determine container name length");
    }

    s=new char[slen];

    if(!CryptGetProvParam( hprov, PP_CONTAINER, (BYTE *)s, &slen, 0)) {
        delete[] s;
        throw CSPException("Crypt.name: Couldn't get container name");
    }
    return s;
}

char *Crypt::uniq_name() {
    char *s;
    DWORD slen;
    if(!CryptGetProvParam( hprov, PP_UNIQUE_CONTAINER, NULL, &slen, 0)) {
        throw CSPException("Crypt.uniq_name: Couldn't determine container unique name length");
    }

    s=new char[slen];

    if(!CryptGetProvParam( hprov, PP_UNIQUE_CONTAINER, (BYTE *)s, &slen, 0)) {
        delete[] s;
        throw CSPException("Crypt.uniq_name: Couldn't get container unique name");
    }
    return s;
}

void Crypt::set_password(char *pin, DWORD keyspec) throw (CSPException) {
    DWORD param;

    if (keyspec == AT_SIGNATURE) {
        param = PP_SIGNATURE_PIN;
    } else {
        param = PP_KEYEXCHANGE_PIN;
    }

    if(!CryptSetProvParam( hprov, param, (const BYTE *)pin, 0)) {
        throw CSPException("Crypt.set_password: Couldn't set password");
    }
}

void Crypt::change_password(char *pin) throw (CSPException) {
    CRYPT_PIN_PARAM param;
    param.type = CRYPT_PIN_PASSWD;
    param.dest.passwd = pin;
    if(!CryptSetProvParam( hprov, PP_CHANGE_PIN, (const BYTE *)&param, 0)) {
        throw CSPException("Crypt.change_password: Couldn't change password");
    }
}

Crypt::Crypt (BYTE *STRING, DWORD LENGTH, DWORD type, DWORD flags, char *name) throw(CSPException, CSPNotFound)
{
    LOG("Crypt::Crypt(%s, %u, %x, %s)\n", container, type, flags, name);
    cont_name = NULL;
    if (STRING) {
        cont_name = new char[LENGTH + 1];
        strncpy(cont_name, (const char *)STRING, LENGTH);
        cont_name[LENGTH] = 0;
    }
 
    pr_name = NULL;
    if (name) {
        pr_name = new char[strlen(name) + 1];
        strcpy(pr_name, name);
    }

    if (flags & CRYPT_DELETEKEYSET) {
        throw CSPException("Crypt: Delete flag not allowed in Crypt::Crypt()", -1);
    }
    if (!CryptAcquireContext(&hprov, cont_name, pr_name, type, flags)) {
        DWORD err = GetLastError();
        switch (err) {
        case NTE_KEYSET_NOT_DEF:
            throw CSPNotFound("Keyset not defined", err);
        case NTE_BAD_KEYSET:
            throw CSPNotFound("Keyset does not exist", err);
        case NTE_BAD_KEYSET_PARAM:
            throw CSPNotFound("Bad keyset parameters or container not found", err);
        default:
            throw CSPException("Crypt: Couldn't acquire context", err);
        }
    }
}

Key *Crypt::get_key(DWORD keyspec) throw(CSPException, CSPNotFound)
{
    HCRYPTKEY hkey = 0;

    LOG("Crypt::get_key(%u)\n", keyspec);
    if(!CryptGetUserKey(hprov, keyspec, &hkey)) {
        DWORD err = GetLastError();
        if (err == (DWORD)NTE_NO_KEY) {
            throw CSPNotFound("Key not found for container", err);
        } else {
            throw CSPException("Crypt.get_key: Couldn't acquire user public key", err);
        }
    }
    LOG("Crypt::get_key: acquired key %u\n", hkey);
    return new Key(this, hkey);
}

Key *Crypt::create_key(DWORD flags, DWORD keyspec) throw(CSPException)
{
    HCRYPTKEY hkey = 0;
    if(!CryptGenKey(hprov, keyspec, flags, &hkey)) {
        throw CSPException("Crypt.create_key: Couldn't create key pair");
    }
    return new Key(this, hkey);
}

Key *Crypt::import_key(BYTE *STRING, DWORD LENGTH, Key *decrypt) throw(CSPException)
{
    HCRYPTKEY hkey = 0;
    HCRYPTKEY decrkey = decrypt? decrypt->hkey : 0;

    if(!CryptImportKey(hprov, STRING, LENGTH, decrkey, 0, &hkey)) {
        throw CSPException("Crypt.import_key: Couldn't import public key blob");
    }
    return new Key(this, hkey);
}

void Crypt::remove(char *container, DWORD type, char *name) throw(CSPException, CSPNotFound) {
    HCRYPTPROV dummy;
    if (!CryptAcquireContext(&dummy, container, name, type, CRYPT_DELETEKEYSET)) {
        DWORD err = GetLastError();
        switch (err) {
        case NTE_KEYSET_NOT_DEF:
            throw CSPNotFound("Keyset not defined", err);
        case NTE_BAD_KEYSET_PARAM:
            throw CSPNotFound("Bad keyset parameters or container not found", err);
        default:
            throw CSPException("Crypt.remove: Couldn't delete container", err);
        }
    }
}

CryptIter *Crypt::enumerate() throw(CSPException) {
    return new CryptIter();
}

CryptIter::CryptIter() throw(CSPException) {
    index = 0;
}

CryptDesc *CryptIter::next() throw (Stop_Iteration, CSPException) {
    DWORD slen, provtype;
    if (CryptEnumProviders(index, NULL, 0, &provtype, NULL, &slen)) {
        CryptDesc *cd = new CryptDesc();
        cd->name = new char[slen];
        cd->type = provtype;
        if (!CryptEnumProviders(index, NULL, 0, &provtype, cd->name, &slen)) {
            DWORD err = GetLastError();
            delete cd;
            throw CSPException("CryptIter.next: error getting provider name", err);
        }
        index ++;
        return cd;
    }
    throw Stop_Iteration();
}
