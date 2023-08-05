/* vim: ft=swig
*/
%feature("ref") Crypt "$this->ref();"
%feature("unref") Crypt "$this->unref();"
%feature("python:slot", "tp_iter", functype="getiterfunc") CryptIter::__iter__;
%feature("python:slot", "tp_iternext", functype="iternextfunc") CryptIter::next;
%newobject Crypt::get_key;
%newobject Crypt::import_key;
%newobject Crypt::create_key;
%newobject Crypt::name;
%newobject Crypt::prov_name;
%newobject Crypt::uniq_name;
%newobject Crypt::enumerate;
%newobject CryptIter::__iter__;
%newobject CryptIter::next;

%include "context.hpp"
