/* vim: ft=swig
*/
/*%newobject CertInfo::name;*/
/*%newobject CertInfo::issuer;*/
/*%newobject CertInfo::serial;*/
/*%newobject CertInfo::not_before;*/
/*%newobject CertInfo::not_after;*/
%newobject CertInfo::extensions;
%newobject ExtIter::next;
%newobject ExtIter::__iter__;
%feature("ref") CertInfo "$this->ref();"
%feature("unref") CertInfo "$this->unref();"
%feature("python:slot", "tp_iter", functype="getiterfunc") ExtIter::__iter__;
%feature("python:slot", "tp_iternext", functype="iternextfunc") ExtIter::next;

%include "certinfo.hpp"
