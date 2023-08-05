/* vim: ft=swig
*/

%typemap(in, noblock=1) DWORD {    
%#if PY_VERSION_HEX >= 0x03000000
    $1 = PyLong_AsUnsignedLong($input);
%#else
    $1 = PyInt_AsUnsignedLongMask($input);
%#endif
}                                      

%typemap(typecheck, precedence=SWIG_TYPECHECK_UINT32) DWORD {
%#if PY_VERSION_HEX >= 0x03000000
    $1 = PyLong_Check($input) ? 1 : 0;
%#else
    int res = SWIG_AsVal_unsigned_SS_int($input, NULL);
    $1 = SWIG_CheckState(res);
%#endif
}

%typemap(in, noblock=1, numinputs=0) (BYTE **s, DWORD *slen)
(BYTE *carray = 0, DWORD size = 0) {    
  $1 = &carray;
  $2 = &size;
}                                      

%typemap(freearg, match="in") (BYTE **s, DWORD *slen) "";

%typemap(argout, noblock=1) (BYTE **s, DWORD *slen) 
(PyObject *res = NULL) { 
    if (*$1) {
        if (*$2 > INT_MAX) {
            swig_type_info* pchar_descriptor = SWIG_pchar_descriptor();
            res = pchar_descriptor ? 
                SWIG_InternalNewPointerObj(%const_cast(*$1,BYTE *), pchar_descriptor, 0) : SWIG_Py_Void();
        } else {
    %#if PY_VERSION_HEX >= 0x03000000
            res = PyBytes_FromStringAndSize((char *)*$1, %numeric_cast(*$2,int));
    %#else
            res = PyString_FromStringAndSize((char *)*$1, %numeric_cast(*$2,int));
    %#endif
        }
        %append_output(res);
        free(*$1);
    } else {
        %append_output(SWIG_Py_Void());
    }
}

%typemap(typecheck, precedence=SWIG_TYPECHECK_STRING) char * {
    int res = (PyString_Check($input) || Py_None == $input) ? 1 : 0;
    $1 = SWIG_CheckState(res);
}


%typemap(typecheck, precedence=SWIG_TYPECHECK_STRING) (BYTE *STRING, DWORD LENGTH) {
%#if py_version_hex>=0x03000000
   $1 = PyBytes_Check($input) ? 1 : 0;
%#else  
   $1 = PyString_Check($input) ? 1 : 0;
%#endif
}

%typemap(in, numinputs=1, noblock=1) (BYTE *STRING, DWORD LENGTH)
(char *cstr=NULL, Py_ssize_t len=0, int res=1) {
%#if py_version_hex>=0x03000000
  if (PyBytes_Check($input))
%#else  
  if (PyString_Check($input))
%#endif
  {
%#if PY_VERSION_HEX>=0x03000000
    res = PyBytes_AsStringAndSize($input, &cstr, &len);
%#else
    res = PyString_AsStringAndSize($input, &cstr, &len);
%#endif
    if (!cstr) {
        res = 1;
    }
/*%#if PY_VERSION_HEX>=0x03000000*/
    /*Py_XDECREF($input);*/
/*%#endif*/
  } 
  
  if(res){
    %argument_fail(SWIG_TypeError, "$type", $symname, $argnum);
  } else {
    $1 = (BYTE *) cstr;
    $2 = (DWORD) len;
  }
};

