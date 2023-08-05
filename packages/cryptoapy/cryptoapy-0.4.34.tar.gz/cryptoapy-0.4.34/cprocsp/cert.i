/* vim: ft=swig
*/
%newobject Cert::thumbprint;
%newobject Cert::duplicate;
%newobject Cert::extract;
%newobject Cert::self_sign;
%newobject Cert::eku;
%newobject CertStore::__iter__;
%newobject CertStore::add_cert;
%newobject CertStore::find_by_thumb;
%newobject CertStore::find_by_name;
%newobject CertStore::get_cert_by_info;
%newobject CertIter::next;
%newobject CertIter::__iter__;
%newobject CertFind::__iter__;
%newobject CertFind::next;
%newobject EKUIter::__iter__;

%feature("ref") Cert "$this->ref();"
%feature("unref") Cert "$this->unref();"
%feature("ref") CertStore "$this->ref();"
%feature("unref") CertStore "$this->unref();"
%feature("python:slot", "tp_iter", functype="getiterfunc") CertStore::__iter__;
%feature("python:slot", "tp_iter", functype="getiterfunc") CertIter::__iter__;
%feature("python:slot", "tp_iter", functype="getiterfunc") CertFind::__iter__;
%feature("python:slot", "tp_iternext", functype="iternextfunc") CertIter::next;
%feature("python:slot", "tp_iternext", functype="iternextfunc") CertFind::next;
%feature("python:slot", "tp_iter", functype="getiterfunc") Cert::eku;
%feature("python:slot", "tp_iter", functype="getiterfunc") EKUIter::__iter__;
%feature("python:slot", "tp_iternext", functype="iternextfunc") EKUIter::next;

%include "cert.hpp"
