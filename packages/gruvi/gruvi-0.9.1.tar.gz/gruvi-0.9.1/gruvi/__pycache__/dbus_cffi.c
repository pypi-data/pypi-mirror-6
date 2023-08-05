
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


#include "src/dbus_splitter.c"

static PyObject *
_cffi_f_split(PyObject *self, PyObject *arg0)
{
  struct context * x0;
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
  { result = split(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static int _cffi_const_ERROR_ENDIAN(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (ERROR_ENDIAN) && (ERROR_ENDIAN) <= LONG_MAX)
    o = PyInt_FromLong((long)(ERROR_ENDIAN));
  else if ((ERROR_ENDIAN) <= 0)
    o = PyLong_FromLongLong((long long)(ERROR_ENDIAN));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(ERROR_ENDIAN));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "ERROR_ENDIAN", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return 0;
}

static int _cffi_const_ERROR_FLAGS(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (ERROR_FLAGS) && (ERROR_FLAGS) <= LONG_MAX)
    o = PyInt_FromLong((long)(ERROR_FLAGS));
  else if ((ERROR_FLAGS) <= 0)
    o = PyLong_FromLongLong((long long)(ERROR_FLAGS));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(ERROR_FLAGS));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "ERROR_FLAGS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_ERROR_ENDIAN(lib);
}

static int _cffi_const_ERROR_SERIAL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (ERROR_SERIAL) && (ERROR_SERIAL) <= LONG_MAX)
    o = PyInt_FromLong((long)(ERROR_SERIAL));
  else if ((ERROR_SERIAL) <= 0)
    o = PyLong_FromLongLong((long long)(ERROR_SERIAL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(ERROR_SERIAL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "ERROR_SERIAL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_ERROR_FLAGS(lib);
}

static int _cffi_const_ERROR_TOO_LARGE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (ERROR_TOO_LARGE) && (ERROR_TOO_LARGE) <= LONG_MAX)
    o = PyInt_FromLong((long)(ERROR_TOO_LARGE));
  else if ((ERROR_TOO_LARGE) <= 0)
    o = PyLong_FromLongLong((long long)(ERROR_TOO_LARGE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(ERROR_TOO_LARGE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "ERROR_TOO_LARGE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_ERROR_SERIAL(lib);
}

static int _cffi_const_ERROR_TYPE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (ERROR_TYPE) && (ERROR_TYPE) <= LONG_MAX)
    o = PyInt_FromLong((long)(ERROR_TYPE));
  else if ((ERROR_TYPE) <= 0)
    o = PyLong_FromLongLong((long long)(ERROR_TYPE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(ERROR_TYPE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "ERROR_TYPE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_ERROR_TOO_LARGE(lib);
}

static int _cffi_const_ERROR_VERSION(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (ERROR_VERSION) && (ERROR_VERSION) <= LONG_MAX)
    o = PyInt_FromLong((long)(ERROR_VERSION));
  else if ((ERROR_VERSION) <= 0)
    o = PyLong_FromLongLong((long long)(ERROR_VERSION));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(ERROR_VERSION));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "ERROR_VERSION", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_ERROR_TYPE(lib);
}

static int _cffi_const_INCOMPLETE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (INCOMPLETE) && (INCOMPLETE) <= LONG_MAX)
    o = PyInt_FromLong((long)(INCOMPLETE));
  else if ((INCOMPLETE) <= 0)
    o = PyLong_FromLongLong((long long)(INCOMPLETE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(INCOMPLETE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "INCOMPLETE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_ERROR_VERSION(lib);
}

static int _cffi_const_OK(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (OK) && (OK) <= LONG_MAX)
    o = PyInt_FromLong((long)(OK));
  else if ((OK) <= 0)
    o = PyLong_FromLongLong((long long)(OK));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(OK));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "OK", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_INCOMPLETE(lib);
}

static void _cffi_check_struct_context(struct context *p)
{
  /* only to generate compile-time warnings or errors */
  { char const * *tmp = &p->buf; (void)tmp; }
  (void)((p->buflen) << 1);
  (void)((p->offset) << 1);
  (void)((p->error) << 1);
  (void)((p->big_endian) << 1);
  (void)((p->msglen) << 1);
  (void)((p->serial) << 1);
  (void)((p->state) << 1);
}
static PyObject *
_cffi_layout_struct_context(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct context y; };
  static Py_ssize_t nums[] = {
    sizeof(struct context),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct context, buf),
    sizeof(((struct context *)0)->buf),
    offsetof(struct context, buflen),
    sizeof(((struct context *)0)->buflen),
    offsetof(struct context, offset),
    sizeof(((struct context *)0)->offset),
    offsetof(struct context, error),
    sizeof(((struct context *)0)->error),
    offsetof(struct context, big_endian),
    sizeof(((struct context *)0)->big_endian),
    offsetof(struct context, msglen),
    sizeof(((struct context *)0)->msglen),
    offsetof(struct context, serial),
    sizeof(((struct context *)0)->serial),
    offsetof(struct context, state),
    sizeof(((struct context *)0)->state),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_context(0);
}

static int _cffi_setup_custom(PyObject *lib)
{
  return _cffi_const_OK(lib);
}

static PyMethodDef _cffi_methods[] = {
  {"split", _cffi_f_split, METH_O},
  {"_cffi_layout_struct_context", _cffi_layout_struct_context, METH_NOARGS},
  {"_cffi_setup", _cffi_setup, METH_VARARGS},
  {NULL, NULL}    /* Sentinel */
};

static struct PyModuleDef _cffi_module_def = {
  PyModuleDef_HEAD_INIT,
  "dbus_cffi",
  NULL,
  -1,
  _cffi_methods,
  NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit_dbus_cffi(void)
{
  PyObject *lib;
  lib = PyModule_Create(&_cffi_module_def);
  if (lib == NULL || 0 < 0)
    return NULL;
  _cffi_init();
  return lib;
}
