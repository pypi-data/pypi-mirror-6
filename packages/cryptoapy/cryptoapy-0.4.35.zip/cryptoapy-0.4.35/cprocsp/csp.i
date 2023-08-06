/* vim: ft=swig
*/
%module csp;
/*%include "typemaps.i"*/
%include "exception.i"
/*%include "cstring.i"*/
%include "bytes.i"
%feature("autodoc", "2");

%typemap(throws) Stop_Iteration %{
  PyErr_SetNone(PyExc_StopIteration);
  SWIG_fail;
%}

%{
#include "common.hpp"
#include "cert.hpp"
#include "certinfo.hpp"
#include "context.hpp"
#include "except.hpp"
#include "key.hpp"
#include "msg.hpp"
#include "rcobj.hpp"
#include "sign.hpp"
#include "request.hpp"
%}

%include "wintypes.i"
%include "defines.i"
%include "extra_defs.i"
%include "common.i"
%include "errors.i"
%include "context.i"
%include "key.i"
%include "cert.i"
%include "certinfo.i"
%include "msg.i"
%include "ext.i"
%include "sign.i"
%include "request.i"
