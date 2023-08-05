
#include <Python.h>
#include <stddef.h>

#ifdef MS_WIN32
#include <malloc.h>   /* for alloca() */
typedef __int8 int8_t;
typedef __int16 int16_t;
typedef __int32 int32_t;
typedef __int64 int64_t;
typedef unsigned __int8 uint8_t;
typedef unsigned __int16 uint16_t;
typedef unsigned __int32 uint32_t;
typedef unsigned __int64 uint64_t;
typedef unsigned char _Bool;
#endif

#if PY_MAJOR_VERSION < 3
# undef PyCapsule_CheckExact
# undef PyCapsule_GetPointer
# define PyCapsule_CheckExact(capsule) (PyCObject_Check(capsule))
# define PyCapsule_GetPointer(capsule, name) \
    (PyCObject_AsVoidPtr(capsule))
#endif

#if PY_MAJOR_VERSION >= 3
# define PyInt_FromLong PyLong_FromLong
#endif

#define _cffi_from_c_double PyFloat_FromDouble
#define _cffi_from_c_float PyFloat_FromDouble
#define _cffi_from_c_long PyInt_FromLong
#define _cffi_from_c_ulong PyLong_FromUnsignedLong
#define _cffi_from_c_longlong PyLong_FromLongLong
#define _cffi_from_c_ulonglong PyLong_FromUnsignedLongLong

#define _cffi_to_c_double PyFloat_AsDouble
#define _cffi_to_c_float PyFloat_AsDouble

#define _cffi_from_c_SIGNED(x, type)                                     \
    (sizeof(type) <= sizeof(long) ? PyInt_FromLong(x) :                  \
                                    PyLong_FromLongLong(x))
#define _cffi_from_c_UNSIGNED(x, type)                                   \
    (sizeof(type) < sizeof(long) ? PyInt_FromLong(x) :                   \
     sizeof(type) == sizeof(long) ? PyLong_FromUnsignedLong(x) :         \
                                    PyLong_FromUnsignedLongLong(x))

#define _cffi_to_c_SIGNED(o, type)                                       \
    (sizeof(type) == 1 ? _cffi_to_c_i8(o) :                              \
     sizeof(type) == 2 ? _cffi_to_c_i16(o) :                             \
     sizeof(type) == 4 ? _cffi_to_c_i32(o) :                             \
     sizeof(type) == 8 ? _cffi_to_c_i64(o) :                             \
     (Py_FatalError("unsupported size for type " #type), 0))
#define _cffi_to_c_UNSIGNED(o, type)                                     \
    (sizeof(type) == 1 ? _cffi_to_c_u8(o) :                              \
     sizeof(type) == 2 ? _cffi_to_c_u16(o) :                             \
     sizeof(type) == 4 ? _cffi_to_c_u32(o) :                             \
     sizeof(type) == 8 ? _cffi_to_c_u64(o) :                             \
     (Py_FatalError("unsupported size for type " #type), 0))

#define _cffi_to_c_i8                                                    \
                 ((int(*)(PyObject *))_cffi_exports[1])
#define _cffi_to_c_u8                                                    \
                 ((int(*)(PyObject *))_cffi_exports[2])
#define _cffi_to_c_i16                                                   \
                 ((int(*)(PyObject *))_cffi_exports[3])
#define _cffi_to_c_u16                                                   \
                 ((int(*)(PyObject *))_cffi_exports[4])
#define _cffi_to_c_i32                                                   \
                 ((int(*)(PyObject *))_cffi_exports[5])
#define _cffi_to_c_u32                                                   \
                 ((unsigned int(*)(PyObject *))_cffi_exports[6])
#define _cffi_to_c_i64                                                   \
                 ((long long(*)(PyObject *))_cffi_exports[7])
#define _cffi_to_c_u64                                                   \
                 ((unsigned long long(*)(PyObject *))_cffi_exports[8])
#define _cffi_to_c_char                                                  \
                 ((int(*)(PyObject *))_cffi_exports[9])
#define _cffi_from_c_pointer                                             \
    ((PyObject *(*)(char *, CTypeDescrObject *))_cffi_exports[10])
#define _cffi_to_c_pointer                                               \
    ((char *(*)(PyObject *, CTypeDescrObject *))_cffi_exports[11])
#define _cffi_get_struct_layout                                          \
    ((PyObject *(*)(Py_ssize_t[]))_cffi_exports[12])
#define _cffi_restore_errno                                              \
    ((void(*)(void))_cffi_exports[13])
#define _cffi_save_errno                                                 \
    ((void(*)(void))_cffi_exports[14])
#define _cffi_from_c_char                                                \
    ((PyObject *(*)(char))_cffi_exports[15])
#define _cffi_from_c_deref                                               \
    ((PyObject *(*)(char *, CTypeDescrObject *))_cffi_exports[16])
#define _cffi_to_c                                                       \
    ((int(*)(char *, CTypeDescrObject *, PyObject *))_cffi_exports[17])
#define _cffi_from_c_struct                                              \
    ((PyObject *(*)(char *, CTypeDescrObject *))_cffi_exports[18])
#define _cffi_to_c_wchar_t                                               \
    ((wchar_t(*)(PyObject *))_cffi_exports[19])
#define _cffi_from_c_wchar_t                                             \
    ((PyObject *(*)(wchar_t))_cffi_exports[20])
#define _cffi_to_c_long_double                                           \
    ((long double(*)(PyObject *))_cffi_exports[21])
#define _cffi_to_c__Bool                                                 \
    ((_Bool(*)(PyObject *))_cffi_exports[22])
#define _cffi_prepare_pointer_call_argument                              \
    ((Py_ssize_t(*)(CTypeDescrObject *, PyObject *, char **))_cffi_exports[23])
#define _cffi_convert_array_from_object                                  \
    ((int(*)(char *, CTypeDescrObject *, PyObject *))_cffi_exports[24])
#define _CFFI_NUM_EXPORTS 25

typedef struct _ctypedescr CTypeDescrObject;

static void *_cffi_exports[_CFFI_NUM_EXPORTS];
static PyObject *_cffi_types, *_cffi_VerificationError;

static int _cffi_setup_custom(PyObject *lib);   /* forward */

static PyObject *_cffi_setup(PyObject *self, PyObject *args)
{
    PyObject *library;
    int was_alive = (_cffi_types != NULL);
    if (!PyArg_ParseTuple(args, "OOO", &_cffi_types, &_cffi_VerificationError,
                                       &library))
        return NULL;
    Py_INCREF(_cffi_types);
    Py_INCREF(_cffi_VerificationError);
    if (_cffi_setup_custom(library) < 0)
        return NULL;
    return PyBool_FromLong(was_alive);
}

static void _cffi_init(void)
{
    PyObject *module = PyImport_ImportModule("_cffi_backend");
    PyObject *c_api_object;

    if (module == NULL)
        return;

    c_api_object = PyObject_GetAttrString(module, "_C_API");
    if (c_api_object == NULL)
        return;
    if (!PyCapsule_CheckExact(c_api_object)) {
        PyErr_SetNone(PyExc_ImportError);
        return;
    }
    memcpy(_cffi_exports, PyCapsule_GetPointer(c_api_object, "cffi"),
           _CFFI_NUM_EXPORTS * sizeof(void *));
}

#define _cffi_type(num) ((CTypeDescrObject *)PyList_GET_ITEM(_cffi_types, num))

/**********/



    #include <stdlib.h>
    #include "src/http_parser.h"
    #include "src/http_parser.c"

    unsigned char http_message_type(http_parser *p) { return p->type; }
    unsigned char http_errno(http_parser *p) { return p->http_errno; }
    unsigned char http_is_upgrade(http_parser *p) { return p->upgrade; }

    

static int _cffi_e_enum_http_errno(PyObject *lib)
{
  return 0;
}

static int _cffi_e_enum_http_method(PyObject *lib)
{
  return _cffi_e_enum_http_errno(lib);
}

static int _cffi_const_HTTP_REQUEST(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (HTTP_REQUEST) && (HTTP_REQUEST) <= LONG_MAX)
    o = PyInt_FromLong((long)(HTTP_REQUEST));
  else if ((HTTP_REQUEST) <= 0)
    o = PyLong_FromLongLong((long long)(HTTP_REQUEST));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(HTTP_REQUEST));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "HTTP_REQUEST", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return 0;
}

static int _cffi_const_HTTP_RESPONSE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (HTTP_RESPONSE) && (HTTP_RESPONSE) <= LONG_MAX)
    o = PyInt_FromLong((long)(HTTP_RESPONSE));
  else if ((HTTP_RESPONSE) <= 0)
    o = PyLong_FromLongLong((long long)(HTTP_RESPONSE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(HTTP_RESPONSE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "HTTP_RESPONSE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_HTTP_REQUEST(lib);
}

static int _cffi_const_HTTP_BOTH(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (HTTP_BOTH) && (HTTP_BOTH) <= LONG_MAX)
    o = PyInt_FromLong((long)(HTTP_BOTH));
  else if ((HTTP_BOTH) <= 0)
    o = PyLong_FromLongLong((long long)(HTTP_BOTH));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(HTTP_BOTH));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "HTTP_BOTH", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_HTTP_RESPONSE(lib);
}

static int _cffi_const_UF_SCHEMA(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (UF_SCHEMA) && (UF_SCHEMA) <= LONG_MAX)
    o = PyInt_FromLong((long)(UF_SCHEMA));
  else if ((UF_SCHEMA) <= 0)
    o = PyLong_FromLongLong((long long)(UF_SCHEMA));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(UF_SCHEMA));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "UF_SCHEMA", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_HTTP_BOTH(lib);
}

static int _cffi_const_UF_HOST(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (UF_HOST) && (UF_HOST) <= LONG_MAX)
    o = PyInt_FromLong((long)(UF_HOST));
  else if ((UF_HOST) <= 0)
    o = PyLong_FromLongLong((long long)(UF_HOST));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(UF_HOST));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "UF_HOST", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_UF_SCHEMA(lib);
}

static int _cffi_const_UF_PORT(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (UF_PORT) && (UF_PORT) <= LONG_MAX)
    o = PyInt_FromLong((long)(UF_PORT));
  else if ((UF_PORT) <= 0)
    o = PyLong_FromLongLong((long long)(UF_PORT));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(UF_PORT));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "UF_PORT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_UF_HOST(lib);
}

static int _cffi_const_UF_PATH(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (UF_PATH) && (UF_PATH) <= LONG_MAX)
    o = PyInt_FromLong((long)(UF_PATH));
  else if ((UF_PATH) <= 0)
    o = PyLong_FromLongLong((long long)(UF_PATH));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(UF_PATH));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "UF_PATH", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_UF_PORT(lib);
}

static int _cffi_const_UF_QUERY(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (UF_QUERY) && (UF_QUERY) <= LONG_MAX)
    o = PyInt_FromLong((long)(UF_QUERY));
  else if ((UF_QUERY) <= 0)
    o = PyLong_FromLongLong((long long)(UF_QUERY));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(UF_QUERY));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "UF_QUERY", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_UF_PATH(lib);
}

static int _cffi_const_UF_FRAGMENT(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (UF_FRAGMENT) && (UF_FRAGMENT) <= LONG_MAX)
    o = PyInt_FromLong((long)(UF_FRAGMENT));
  else if ((UF_FRAGMENT) <= 0)
    o = PyLong_FromLongLong((long long)(UF_FRAGMENT));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(UF_FRAGMENT));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "UF_FRAGMENT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_UF_QUERY(lib);
}

static int _cffi_const_UF_USERINFO(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (UF_USERINFO) && (UF_USERINFO) <= LONG_MAX)
    o = PyInt_FromLong((long)(UF_USERINFO));
  else if ((UF_USERINFO) <= 0)
    o = PyLong_FromLongLong((long long)(UF_USERINFO));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(UF_USERINFO));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "UF_USERINFO", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_UF_FRAGMENT(lib);
}

static PyObject *
_cffi_f_http_body_is_final(PyObject *self, PyObject *arg0)
{
  http_parser const * x0;
  Py_ssize_t datasize;
  int result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(0), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = http_body_is_final(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_http_errno(PyObject *self, PyObject *arg0)
{
  http_parser * x0;
  Py_ssize_t datasize;
  unsigned char result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(1), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = http_errno(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_UNSIGNED(result, unsigned char);
}

static PyObject *
_cffi_f_http_errno_description(PyObject *self, PyObject *arg0)
{
  enum http_errno x0;
  char const * result;

  if (_cffi_to_c((char *)&x0, _cffi_type(2), arg0) < 0)
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = http_errno_description(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(3));
}

static PyObject *
_cffi_f_http_errno_name(PyObject *self, PyObject *arg0)
{
  enum http_errno x0;
  char const * result;

  if (_cffi_to_c((char *)&x0, _cffi_type(2), arg0) < 0)
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = http_errno_name(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(3));
}

static PyObject *
_cffi_f_http_is_upgrade(PyObject *self, PyObject *arg0)
{
  http_parser * x0;
  Py_ssize_t datasize;
  unsigned char result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(1), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = http_is_upgrade(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_UNSIGNED(result, unsigned char);
}

static PyObject *
_cffi_f_http_message_type(PyObject *self, PyObject *arg0)
{
  http_parser * x0;
  Py_ssize_t datasize;
  unsigned char result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(1), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = http_message_type(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_UNSIGNED(result, unsigned char);
}

static PyObject *
_cffi_f_http_method_str(PyObject *self, PyObject *arg0)
{
  enum http_method x0;
  char const * result;

  if (_cffi_to_c((char *)&x0, _cffi_type(4), arg0) < 0)
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = http_method_str(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(3));
}

static PyObject *
_cffi_f_http_parser_execute(PyObject *self, PyObject *args)
{
  http_parser * x0;
  http_parser_settings const * x1;
  char const * x2;
  size_t x3;
  Py_ssize_t datasize;
  size_t result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:http_parser_execute", &arg0, &arg1, &arg2, &arg3))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(1), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(5), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(5), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(3), arg2) < 0)
      return NULL;
  }

  x3 = _cffi_to_c_UNSIGNED(arg3, size_t);
  if (x3 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = http_parser_execute(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_UNSIGNED(result, size_t);
}

static PyObject *
_cffi_f_http_parser_init(PyObject *self, PyObject *args)
{
  http_parser * x0;
  enum http_parser_type x1;
  Py_ssize_t datasize;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:http_parser_init", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(1), arg0) < 0)
      return NULL;
  }

  if (_cffi_to_c((char *)&x1, _cffi_type(6), arg1) < 0)
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { http_parser_init(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_http_parser_parse_url(PyObject *self, PyObject *args)
{
  char const * x0;
  size_t x1;
  int x2;
  struct http_parser_url * x3;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:http_parser_parse_url", &arg0, &arg1, &arg2, &arg3))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(3), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_UNSIGNED(arg1, size_t);
  if (x1 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  x2 = _cffi_to_c_SIGNED(arg2, int);
  if (x2 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(8), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca(datasize);
    memset((void *)x3, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(8), arg3) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = http_parser_parse_url(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_http_parser_pause(PyObject *self, PyObject *args)
{
  http_parser * x0;
  int x1;
  Py_ssize_t datasize;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:http_parser_pause", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(1), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_SIGNED(arg1, int);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { http_parser_pause(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_http_should_keep_alive(PyObject *self, PyObject *arg0)
{
  http_parser const * x0;
  Py_ssize_t datasize;
  int result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(0), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = http_should_keep_alive(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static void _cffi_check_struct_http_parser(struct http_parser *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->http_major) << 1);
  (void)((p->http_minor) << 1);
  (void)((p->status_code) << 1);
  (void)((p->method) << 1);
  { void * *tmp = &p->data; (void)tmp; }
}
static PyObject *
_cffi_layout_struct_http_parser(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct http_parser y; };
  static Py_ssize_t nums[] = {
    sizeof(struct http_parser),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct http_parser, http_major),
    sizeof(((struct http_parser *)0)->http_major),
    offsetof(struct http_parser, http_minor),
    sizeof(((struct http_parser *)0)->http_minor),
    offsetof(struct http_parser, status_code),
    sizeof(((struct http_parser *)0)->status_code),
    offsetof(struct http_parser, method),
    sizeof(((struct http_parser *)0)->method),
    offsetof(struct http_parser, data),
    sizeof(((struct http_parser *)0)->data),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_http_parser(0);
}

static void _cffi_check_struct_http_parser_settings(struct http_parser_settings *p)
{
  /* only to generate compile-time warnings or errors */
  { int(* *tmp)(http_parser *) = &p->on_message_begin; (void)tmp; }
  { int(* *tmp)(http_parser *, char const *, size_t) = &p->on_url; (void)tmp; }
  { int(* *tmp)(http_parser *) = &p->on_status_complete; (void)tmp; }
  { int(* *tmp)(http_parser *, char const *, size_t) = &p->on_header_field; (void)tmp; }
  { int(* *tmp)(http_parser *, char const *, size_t) = &p->on_header_value; (void)tmp; }
  { int(* *tmp)(http_parser *) = &p->on_headers_complete; (void)tmp; }
  { int(* *tmp)(http_parser *, char const *, size_t) = &p->on_body; (void)tmp; }
  { int(* *tmp)(http_parser *) = &p->on_message_complete; (void)tmp; }
}
static PyObject *
_cffi_layout_struct_http_parser_settings(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct http_parser_settings y; };
  static Py_ssize_t nums[] = {
    sizeof(struct http_parser_settings),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct http_parser_settings, on_message_begin),
    sizeof(((struct http_parser_settings *)0)->on_message_begin),
    offsetof(struct http_parser_settings, on_url),
    sizeof(((struct http_parser_settings *)0)->on_url),
    offsetof(struct http_parser_settings, on_status_complete),
    sizeof(((struct http_parser_settings *)0)->on_status_complete),
    offsetof(struct http_parser_settings, on_header_field),
    sizeof(((struct http_parser_settings *)0)->on_header_field),
    offsetof(struct http_parser_settings, on_header_value),
    sizeof(((struct http_parser_settings *)0)->on_header_value),
    offsetof(struct http_parser_settings, on_headers_complete),
    sizeof(((struct http_parser_settings *)0)->on_headers_complete),
    offsetof(struct http_parser_settings, on_body),
    sizeof(((struct http_parser_settings *)0)->on_body),
    offsetof(struct http_parser_settings, on_message_complete),
    sizeof(((struct http_parser_settings *)0)->on_message_complete),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_http_parser_settings(0);
}

static void _cffi_check_struct_http_parser_url(struct http_parser_url *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->field_set) << 1);
  (void)((p->port) << 1);
  /* cannot generate 'struct $1[]' in field 'field_data': unknown type name */
}
static PyObject *
_cffi_layout_struct_http_parser_url(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct http_parser_url y; };
  static Py_ssize_t nums[] = {
    sizeof(struct http_parser_url),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct http_parser_url, field_set),
    sizeof(((struct http_parser_url *)0)->field_set),
    offsetof(struct http_parser_url, port),
    sizeof(((struct http_parser_url *)0)->port),
    offsetof(struct http_parser_url, field_data),
    0,  /* struct $1[] */
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_http_parser_url(0);
}

static int _cffi_setup_custom(PyObject *lib)
{
  return _cffi_e_enum_http_method(lib);
}

static PyMethodDef _cffi_methods[] = {
  {"http_body_is_final", _cffi_f_http_body_is_final, METH_O},
  {"http_errno", _cffi_f_http_errno, METH_O},
  {"http_errno_description", _cffi_f_http_errno_description, METH_O},
  {"http_errno_name", _cffi_f_http_errno_name, METH_O},
  {"http_is_upgrade", _cffi_f_http_is_upgrade, METH_O},
  {"http_message_type", _cffi_f_http_message_type, METH_O},
  {"http_method_str", _cffi_f_http_method_str, METH_O},
  {"http_parser_execute", _cffi_f_http_parser_execute, METH_VARARGS},
  {"http_parser_init", _cffi_f_http_parser_init, METH_VARARGS},
  {"http_parser_parse_url", _cffi_f_http_parser_parse_url, METH_VARARGS},
  {"http_parser_pause", _cffi_f_http_parser_pause, METH_VARARGS},
  {"http_should_keep_alive", _cffi_f_http_should_keep_alive, METH_O},
  {"_cffi_layout_struct_http_parser", _cffi_layout_struct_http_parser, METH_NOARGS},
  {"_cffi_layout_struct_http_parser_settings", _cffi_layout_struct_http_parser_settings, METH_NOARGS},
  {"_cffi_layout_struct_http_parser_url", _cffi_layout_struct_http_parser_url, METH_NOARGS},
  {"_cffi_setup", _cffi_setup, METH_VARARGS},
  {NULL, NULL}    /* Sentinel */
};

static struct PyModuleDef _cffi_module_def = {
  PyModuleDef_HEAD_INIT,
  "http_cffi",
  NULL,
  -1,
  _cffi_methods,
  NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit_http_cffi(void)
{
  PyObject *lib;
  lib = PyModule_Create(&_cffi_module_def);
  if (lib == NULL || _cffi_const_UF_USERINFO(lib) < 0)
    return NULL;
  _cffi_init();
  return lib;
}
