/* vim: ft=swig
*/

%typemap(throws) CSPNotFound %{
  PyErr_SetString(PyExc_ValueError, $1.msg);
  SWIG_fail;
%}

%typemap(throws) CSPException %{
  PyErr_SetString(PyExc_SystemError, $1.msg);
  SWIG_fail;
%}
