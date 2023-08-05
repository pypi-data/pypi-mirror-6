
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

static PyObject *_cffi_setup_custom(PyObject *lib);   /* forward */

static PyObject *_cffi_setup(PyObject *self, PyObject *args)
{
    PyObject *library;
    if (!PyArg_ParseTuple(args, "OOO", &_cffi_types, &_cffi_VerificationError,
                                       &library))
        return NULL;
    Py_INCREF(_cffi_types);
    Py_INCREF(_cffi_VerificationError);
    return _cffi_setup_custom(library);
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



// Required for ldap_bind_simple
#define LDAP_DEPRECATED 1

#include <ldap.h>
#include <lber.h>


static PyObject *
_cffi_f_ber_bvstr(PyObject *self, PyObject *arg0)
{
  char const * x0;
  Py_ssize_t datasize;
  struct berval * result;

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
  { result = ber_bvstr(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(1));
}

static PyObject *
_cffi_f_ldap_add_ext_s(PyObject *self, PyObject *args)
{
  LDAP * x0;
  char const * x1;
  LDAPMod * * x2;
  LDAPControl * * x3;
  LDAPControl * * x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:ldap_add_ext_s", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(0), arg1) < 0)
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

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca(datasize);
    memset((void *)x3, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(4), arg3) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg4, (char **)&x4);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x4 = alloca(datasize);
    memset((void *)x4, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x4, _cffi_type(4), arg4) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ldap_add_ext_s(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_ldap_count_entries(PyObject *self, PyObject *args)
{
  LDAP * x0;
  LDAPMessage * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:ldap_count_entries", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
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

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ldap_count_entries(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_ldap_count_values(PyObject *self, PyObject *arg0)
{
  char * * x0;
  Py_ssize_t datasize;
  int result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(6), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(6), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ldap_count_values(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_ldap_delete_s(PyObject *self, PyObject *args)
{
  LDAP * x0;
  char * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:ldap_delete_s", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(7), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(7), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ldap_delete_s(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_ldap_err2string(PyObject *self, PyObject *arg0)
{
  int x0;
  char * result;

  x0 = _cffi_to_c_SIGNED(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ldap_err2string(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(7));
}

static PyObject *
_cffi_f_ldap_first_attribute(PyObject *self, PyObject *args)
{
  LDAP * x0;
  LDAPMessage * x1;
  BerElement * * x2;
  Py_ssize_t datasize;
  char * result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:ldap_first_attribute", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
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
      _cffi_type(8), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(8), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ldap_first_attribute(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(7));
}

static PyObject *
_cffi_f_ldap_first_entry(PyObject *self, PyObject *args)
{
  LDAP * x0;
  LDAPMessage * x1;
  Py_ssize_t datasize;
  LDAPMessage * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:ldap_first_entry", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
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

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ldap_first_entry(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(5));
}

static PyObject *
_cffi_f_ldap_get_dn(PyObject *self, PyObject *args)
{
  LDAP * x0;
  LDAPMessage * x1;
  Py_ssize_t datasize;
  char * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:ldap_get_dn", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
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

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ldap_get_dn(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(7));
}

static PyObject *
_cffi_f_ldap_get_values(PyObject *self, PyObject *args)
{
  LDAP * x0;
  LDAPMessage * x1;
  char * x2;
  Py_ssize_t datasize;
  char * * result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:ldap_get_values", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
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
      _cffi_type(7), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(7), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ldap_get_values(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(6));
}

static PyObject *
_cffi_f_ldap_initialize(PyObject *self, PyObject *args)
{
  LDAP * * x0;
  char * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:ldap_initialize", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(9), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(9), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(7), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(7), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ldap_initialize(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_ldap_modify_ext_s(PyObject *self, PyObject *args)
{
  LDAP * x0;
  char * x1;
  LDAPMod * * x2;
  LDAPControl * * x3;
  LDAPControl * * x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:ldap_modify_ext_s", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(7), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(7), arg1) < 0)
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

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca(datasize);
    memset((void *)x3, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(4), arg3) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg4, (char **)&x4);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x4 = alloca(datasize);
    memset((void *)x4, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x4, _cffi_type(4), arg4) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ldap_modify_ext_s(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_ldap_msgfree(PyObject *self, PyObject *arg0)
{
  LDAPMessage * x0;
  Py_ssize_t datasize;
  int result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(5), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(5), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ldap_msgfree(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_ldap_next_attribute(PyObject *self, PyObject *args)
{
  LDAP * x0;
  LDAPMessage * x1;
  BerElement * x2;
  Py_ssize_t datasize;
  char * result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:ldap_next_attribute", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
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
      _cffi_type(10), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(10), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ldap_next_attribute(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(7));
}

static PyObject *
_cffi_f_ldap_next_entry(PyObject *self, PyObject *args)
{
  LDAP * x0;
  LDAPMessage * x1;
  Py_ssize_t datasize;
  LDAPMessage * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:ldap_next_entry", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
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

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ldap_next_entry(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(5));
}

static PyObject *
_cffi_f_ldap_passwd_s(PyObject *self, PyObject *args)
{
  LDAP * x0;
  struct berval * x1;
  struct berval * x2;
  struct berval * x3;
  struct berval * x4;
  LDAPControl * * x5;
  LDAPControl * * x6;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;
  PyObject *arg5;
  PyObject *arg6;

  if (!PyArg_ParseTuple(args, "OOOOOOO:ldap_passwd_s", &arg0, &arg1, &arg2, &arg3, &arg4, &arg5, &arg6))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(1), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(1), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca(datasize);
    memset((void *)x3, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(1), arg3) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg4, (char **)&x4);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x4 = alloca(datasize);
    memset((void *)x4, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x4, _cffi_type(1), arg4) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg5, (char **)&x5);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x5 = alloca(datasize);
    memset((void *)x5, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x5, _cffi_type(4), arg5) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg6, (char **)&x6);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x6 = alloca(datasize);
    memset((void *)x6, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x6, _cffi_type(4), arg6) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ldap_passwd_s(x0, x1, x2, x3, x4, x5, x6); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_ldap_rename_s(PyObject *self, PyObject *args)
{
  LDAP * x0;
  char const * x1;
  char const * x2;
  char const * x3;
  int x4;
  LDAPControl * * x5;
  LDAPControl * * x6;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;
  PyObject *arg5;
  PyObject *arg6;

  if (!PyArg_ParseTuple(args, "OOOOOOO:ldap_rename_s", &arg0, &arg1, &arg2, &arg3, &arg4, &arg5, &arg6))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(0), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(0), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca(datasize);
    memset((void *)x3, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(0), arg3) < 0)
      return NULL;
  }

  x4 = _cffi_to_c_SIGNED(arg4, int);
  if (x4 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg5, (char **)&x5);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x5 = alloca(datasize);
    memset((void *)x5, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x5, _cffi_type(4), arg5) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg6, (char **)&x6);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x6 = alloca(datasize);
    memset((void *)x6, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x6, _cffi_type(4), arg6) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ldap_rename_s(x0, x1, x2, x3, x4, x5, x6); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_ldap_search_ext_s(PyObject *self, PyObject *args)
{
  LDAP * x0;
  char * x1;
  int x2;
  char * x3;
  char * * x4;
  int x5;
  LDAPControl * * x6;
  LDAPControl * * x7;
  struct timeval * x8;
  int x9;
  LDAPMessage * * x10;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;
  PyObject *arg5;
  PyObject *arg6;
  PyObject *arg7;
  PyObject *arg8;
  PyObject *arg9;
  PyObject *arg10;

  if (!PyArg_ParseTuple(args, "OOOOOOOOOOO:ldap_search_ext_s", &arg0, &arg1, &arg2, &arg3, &arg4, &arg5, &arg6, &arg7, &arg8, &arg9, &arg10))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(7), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(7), arg1) < 0)
      return NULL;
  }

  x2 = _cffi_to_c_SIGNED(arg2, int);
  if (x2 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(7), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca(datasize);
    memset((void *)x3, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(7), arg3) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(6), arg4, (char **)&x4);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x4 = alloca(datasize);
    memset((void *)x4, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x4, _cffi_type(6), arg4) < 0)
      return NULL;
  }

  x5 = _cffi_to_c_SIGNED(arg5, int);
  if (x5 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg6, (char **)&x6);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x6 = alloca(datasize);
    memset((void *)x6, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x6, _cffi_type(4), arg6) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg7, (char **)&x7);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x7 = alloca(datasize);
    memset((void *)x7, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x7, _cffi_type(4), arg7) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(11), arg8, (char **)&x8);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x8 = alloca(datasize);
    memset((void *)x8, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x8, _cffi_type(11), arg8) < 0)
      return NULL;
  }

  x9 = _cffi_to_c_SIGNED(arg9, int);
  if (x9 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(12), arg10, (char **)&x10);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x10 = alloca(datasize);
    memset((void *)x10, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x10, _cffi_type(12), arg10) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ldap_search_ext_s(x0, x1, x2, x3, x4, x5, x6, x7, x8, x9, x10); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_ldap_set_option(PyObject *self, PyObject *args)
{
  LDAP * x0;
  int x1;
  void const * x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:ldap_set_option", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_SIGNED(arg1, int);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(13), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(13), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ldap_set_option(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_ldap_simple_bind_s(PyObject *self, PyObject *args)
{
  LDAP * x0;
  char const * x1;
  char const * x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:ldap_simple_bind_s", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(2), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(0), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(0), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ldap_simple_bind_s(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static int _cffi_const_LDAP_INVALID_CREDENTIALS(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (LDAP_INVALID_CREDENTIALS) && (LDAP_INVALID_CREDENTIALS) <= LONG_MAX)
    o = PyInt_FromLong((long)(LDAP_INVALID_CREDENTIALS));
  else if ((LDAP_INVALID_CREDENTIALS) <= 0)
    o = PyLong_FromLongLong((long long)(LDAP_INVALID_CREDENTIALS));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(LDAP_INVALID_CREDENTIALS));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "LDAP_INVALID_CREDENTIALS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return 0;
}

static int _cffi_const_LDAP_MOD_ADD(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (LDAP_MOD_ADD) && (LDAP_MOD_ADD) <= LONG_MAX)
    o = PyInt_FromLong((long)(LDAP_MOD_ADD));
  else if ((LDAP_MOD_ADD) <= 0)
    o = PyLong_FromLongLong((long long)(LDAP_MOD_ADD));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(LDAP_MOD_ADD));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "LDAP_MOD_ADD", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_LDAP_INVALID_CREDENTIALS(lib);
}

static int _cffi_const_LDAP_MOD_DELETE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (LDAP_MOD_DELETE) && (LDAP_MOD_DELETE) <= LONG_MAX)
    o = PyInt_FromLong((long)(LDAP_MOD_DELETE));
  else if ((LDAP_MOD_DELETE) <= 0)
    o = PyLong_FromLongLong((long long)(LDAP_MOD_DELETE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(LDAP_MOD_DELETE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "LDAP_MOD_DELETE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_LDAP_MOD_ADD(lib);
}

static int _cffi_const_LDAP_MOD_REPLACE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (LDAP_MOD_REPLACE) && (LDAP_MOD_REPLACE) <= LONG_MAX)
    o = PyInt_FromLong((long)(LDAP_MOD_REPLACE));
  else if ((LDAP_MOD_REPLACE) <= 0)
    o = PyLong_FromLongLong((long long)(LDAP_MOD_REPLACE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(LDAP_MOD_REPLACE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "LDAP_MOD_REPLACE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_LDAP_MOD_DELETE(lib);
}

static int _cffi_const_LDAP_NO_LIMIT(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (LDAP_NO_LIMIT) && (LDAP_NO_LIMIT) <= LONG_MAX)
    o = PyInt_FromLong((long)(LDAP_NO_LIMIT));
  else if ((LDAP_NO_LIMIT) <= 0)
    o = PyLong_FromLongLong((long long)(LDAP_NO_LIMIT));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(LDAP_NO_LIMIT));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "LDAP_NO_LIMIT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_LDAP_MOD_REPLACE(lib);
}

static int _cffi_const_LDAP_NO_SUCH_OBJECT(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (LDAP_NO_SUCH_OBJECT) && (LDAP_NO_SUCH_OBJECT) <= LONG_MAX)
    o = PyInt_FromLong((long)(LDAP_NO_SUCH_OBJECT));
  else if ((LDAP_NO_SUCH_OBJECT) <= 0)
    o = PyLong_FromLongLong((long long)(LDAP_NO_SUCH_OBJECT));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(LDAP_NO_SUCH_OBJECT));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "LDAP_NO_SUCH_OBJECT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_LDAP_NO_LIMIT(lib);
}

static int _cffi_const_LDAP_OPT_PROTOCOL_VERSION(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (LDAP_OPT_PROTOCOL_VERSION) && (LDAP_OPT_PROTOCOL_VERSION) <= LONG_MAX)
    o = PyInt_FromLong((long)(LDAP_OPT_PROTOCOL_VERSION));
  else if ((LDAP_OPT_PROTOCOL_VERSION) <= 0)
    o = PyLong_FromLongLong((long long)(LDAP_OPT_PROTOCOL_VERSION));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(LDAP_OPT_PROTOCOL_VERSION));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "LDAP_OPT_PROTOCOL_VERSION", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_LDAP_NO_SUCH_OBJECT(lib);
}

static int _cffi_const_LDAP_OPT_TIMELIMIT(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (LDAP_OPT_TIMELIMIT) && (LDAP_OPT_TIMELIMIT) <= LONG_MAX)
    o = PyInt_FromLong((long)(LDAP_OPT_TIMELIMIT));
  else if ((LDAP_OPT_TIMELIMIT) <= 0)
    o = PyLong_FromLongLong((long long)(LDAP_OPT_TIMELIMIT));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(LDAP_OPT_TIMELIMIT));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "LDAP_OPT_TIMELIMIT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_LDAP_OPT_PROTOCOL_VERSION(lib);
}

static int _cffi_const_LDAP_OPT_X_TLS_ALLOW(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (LDAP_OPT_X_TLS_ALLOW) && (LDAP_OPT_X_TLS_ALLOW) <= LONG_MAX)
    o = PyInt_FromLong((long)(LDAP_OPT_X_TLS_ALLOW));
  else if ((LDAP_OPT_X_TLS_ALLOW) <= 0)
    o = PyLong_FromLongLong((long long)(LDAP_OPT_X_TLS_ALLOW));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(LDAP_OPT_X_TLS_ALLOW));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "LDAP_OPT_X_TLS_ALLOW", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_LDAP_OPT_TIMELIMIT(lib);
}

static int _cffi_const_LDAP_OPT_X_TLS_CACERTFILE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (LDAP_OPT_X_TLS_CACERTFILE) && (LDAP_OPT_X_TLS_CACERTFILE) <= LONG_MAX)
    o = PyInt_FromLong((long)(LDAP_OPT_X_TLS_CACERTFILE));
  else if ((LDAP_OPT_X_TLS_CACERTFILE) <= 0)
    o = PyLong_FromLongLong((long long)(LDAP_OPT_X_TLS_CACERTFILE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(LDAP_OPT_X_TLS_CACERTFILE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "LDAP_OPT_X_TLS_CACERTFILE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_LDAP_OPT_X_TLS_ALLOW(lib);
}

static int _cffi_const_LDAP_OPT_X_TLS_DEMAND(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (LDAP_OPT_X_TLS_DEMAND) && (LDAP_OPT_X_TLS_DEMAND) <= LONG_MAX)
    o = PyInt_FromLong((long)(LDAP_OPT_X_TLS_DEMAND));
  else if ((LDAP_OPT_X_TLS_DEMAND) <= 0)
    o = PyLong_FromLongLong((long long)(LDAP_OPT_X_TLS_DEMAND));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(LDAP_OPT_X_TLS_DEMAND));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "LDAP_OPT_X_TLS_DEMAND", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_LDAP_OPT_X_TLS_CACERTFILE(lib);
}

static int _cffi_const_LDAP_OPT_X_TLS_HARD(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (LDAP_OPT_X_TLS_HARD) && (LDAP_OPT_X_TLS_HARD) <= LONG_MAX)
    o = PyInt_FromLong((long)(LDAP_OPT_X_TLS_HARD));
  else if ((LDAP_OPT_X_TLS_HARD) <= 0)
    o = PyLong_FromLongLong((long long)(LDAP_OPT_X_TLS_HARD));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(LDAP_OPT_X_TLS_HARD));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "LDAP_OPT_X_TLS_HARD", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_LDAP_OPT_X_TLS_DEMAND(lib);
}

static int _cffi_const_LDAP_OPT_X_TLS_NEVER(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (LDAP_OPT_X_TLS_NEVER) && (LDAP_OPT_X_TLS_NEVER) <= LONG_MAX)
    o = PyInt_FromLong((long)(LDAP_OPT_X_TLS_NEVER));
  else if ((LDAP_OPT_X_TLS_NEVER) <= 0)
    o = PyLong_FromLongLong((long long)(LDAP_OPT_X_TLS_NEVER));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(LDAP_OPT_X_TLS_NEVER));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "LDAP_OPT_X_TLS_NEVER", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_LDAP_OPT_X_TLS_HARD(lib);
}

static int _cffi_const_LDAP_OPT_X_TLS_NEWCTX(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (LDAP_OPT_X_TLS_NEWCTX) && (LDAP_OPT_X_TLS_NEWCTX) <= LONG_MAX)
    o = PyInt_FromLong((long)(LDAP_OPT_X_TLS_NEWCTX));
  else if ((LDAP_OPT_X_TLS_NEWCTX) <= 0)
    o = PyLong_FromLongLong((long long)(LDAP_OPT_X_TLS_NEWCTX));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(LDAP_OPT_X_TLS_NEWCTX));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "LDAP_OPT_X_TLS_NEWCTX", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_LDAP_OPT_X_TLS_NEVER(lib);
}

static int _cffi_const_LDAP_OPT_X_TLS_REQUIRE_CERT(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (LDAP_OPT_X_TLS_REQUIRE_CERT) && (LDAP_OPT_X_TLS_REQUIRE_CERT) <= LONG_MAX)
    o = PyInt_FromLong((long)(LDAP_OPT_X_TLS_REQUIRE_CERT));
  else if ((LDAP_OPT_X_TLS_REQUIRE_CERT) <= 0)
    o = PyLong_FromLongLong((long long)(LDAP_OPT_X_TLS_REQUIRE_CERT));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(LDAP_OPT_X_TLS_REQUIRE_CERT));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "LDAP_OPT_X_TLS_REQUIRE_CERT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_LDAP_OPT_X_TLS_NEWCTX(lib);
}

static int _cffi_const_LDAP_OPT_X_TLS_TRY(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (LDAP_OPT_X_TLS_TRY) && (LDAP_OPT_X_TLS_TRY) <= LONG_MAX)
    o = PyInt_FromLong((long)(LDAP_OPT_X_TLS_TRY));
  else if ((LDAP_OPT_X_TLS_TRY) <= 0)
    o = PyLong_FromLongLong((long long)(LDAP_OPT_X_TLS_TRY));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(LDAP_OPT_X_TLS_TRY));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "LDAP_OPT_X_TLS_TRY", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_LDAP_OPT_X_TLS_REQUIRE_CERT(lib);
}

static int _cffi_const_LDAP_SCOPE_BASE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (LDAP_SCOPE_BASE) && (LDAP_SCOPE_BASE) <= LONG_MAX)
    o = PyInt_FromLong((long)(LDAP_SCOPE_BASE));
  else if ((LDAP_SCOPE_BASE) <= 0)
    o = PyLong_FromLongLong((long long)(LDAP_SCOPE_BASE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(LDAP_SCOPE_BASE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "LDAP_SCOPE_BASE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_LDAP_OPT_X_TLS_TRY(lib);
}

static int _cffi_const_LDAP_SCOPE_ONELEVEL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (LDAP_SCOPE_ONELEVEL) && (LDAP_SCOPE_ONELEVEL) <= LONG_MAX)
    o = PyInt_FromLong((long)(LDAP_SCOPE_ONELEVEL));
  else if ((LDAP_SCOPE_ONELEVEL) <= 0)
    o = PyLong_FromLongLong((long long)(LDAP_SCOPE_ONELEVEL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(LDAP_SCOPE_ONELEVEL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "LDAP_SCOPE_ONELEVEL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_LDAP_SCOPE_BASE(lib);
}

static int _cffi_const_LDAP_SCOPE_SUBTREE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (LDAP_SCOPE_SUBTREE) && (LDAP_SCOPE_SUBTREE) <= LONG_MAX)
    o = PyInt_FromLong((long)(LDAP_SCOPE_SUBTREE));
  else if ((LDAP_SCOPE_SUBTREE) <= 0)
    o = PyLong_FromLongLong((long long)(LDAP_SCOPE_SUBTREE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(LDAP_SCOPE_SUBTREE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "LDAP_SCOPE_SUBTREE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_LDAP_SCOPE_ONELEVEL(lib);
}

static int _cffi_const_LDAP_SERVER_DOWN(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (LDAP_SERVER_DOWN) && (LDAP_SERVER_DOWN) <= LONG_MAX)
    o = PyInt_FromLong((long)(LDAP_SERVER_DOWN));
  else if ((LDAP_SERVER_DOWN) <= 0)
    o = PyLong_FromLongLong((long long)(LDAP_SERVER_DOWN));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(LDAP_SERVER_DOWN));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "LDAP_SERVER_DOWN", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_LDAP_SCOPE_SUBTREE(lib);
}

static int _cffi_const_LDAP_SUCCESS(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (LDAP_SUCCESS) && (LDAP_SUCCESS) <= LONG_MAX)
    o = PyInt_FromLong((long)(LDAP_SUCCESS));
  else if ((LDAP_SUCCESS) <= 0)
    o = PyLong_FromLongLong((long long)(LDAP_SUCCESS));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(LDAP_SUCCESS));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "LDAP_SUCCESS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_LDAP_SERVER_DOWN(lib);
}

static int _cffi_const_LDAP_VERSION3(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (LDAP_VERSION3) && (LDAP_VERSION3) <= LONG_MAX)
    o = PyInt_FromLong((long)(LDAP_VERSION3));
  else if ((LDAP_VERSION3) <= 0)
    o = PyLong_FromLongLong((long long)(LDAP_VERSION3));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(LDAP_VERSION3));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "LDAP_VERSION3", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_LDAP_SUCCESS(lib);
}

static void _cffi_check_struct_ldapmod(struct ldapmod *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->mod_op) << 1);
  { char * *tmp = &p->mod_type; (void)tmp; }
  /* cannot generate 'union $1' in field 'mod_vals': unknown type name */
}
static PyObject *
_cffi_layout_struct_ldapmod(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct ldapmod y; };
  static Py_ssize_t nums[] = {
    sizeof(struct ldapmod),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct ldapmod, mod_op),
    sizeof(((struct ldapmod *)0)->mod_op),
    offsetof(struct ldapmod, mod_type),
    sizeof(((struct ldapmod *)0)->mod_type),
    offsetof(struct ldapmod, mod_vals),
    sizeof(((struct ldapmod *)0)->mod_vals),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_ldapmod(0);
}

static PyObject *_cffi_setup_custom(PyObject *lib)
{
  if (_cffi_const_LDAP_VERSION3(lib) < 0)
    return NULL;
  Py_INCREF(Py_None);
  return Py_None;
}

static PyMethodDef _cffi_methods[] = {
  {"ber_bvstr", _cffi_f_ber_bvstr, METH_O},
  {"ldap_add_ext_s", _cffi_f_ldap_add_ext_s, METH_VARARGS},
  {"ldap_count_entries", _cffi_f_ldap_count_entries, METH_VARARGS},
  {"ldap_count_values", _cffi_f_ldap_count_values, METH_O},
  {"ldap_delete_s", _cffi_f_ldap_delete_s, METH_VARARGS},
  {"ldap_err2string", _cffi_f_ldap_err2string, METH_O},
  {"ldap_first_attribute", _cffi_f_ldap_first_attribute, METH_VARARGS},
  {"ldap_first_entry", _cffi_f_ldap_first_entry, METH_VARARGS},
  {"ldap_get_dn", _cffi_f_ldap_get_dn, METH_VARARGS},
  {"ldap_get_values", _cffi_f_ldap_get_values, METH_VARARGS},
  {"ldap_initialize", _cffi_f_ldap_initialize, METH_VARARGS},
  {"ldap_modify_ext_s", _cffi_f_ldap_modify_ext_s, METH_VARARGS},
  {"ldap_msgfree", _cffi_f_ldap_msgfree, METH_O},
  {"ldap_next_attribute", _cffi_f_ldap_next_attribute, METH_VARARGS},
  {"ldap_next_entry", _cffi_f_ldap_next_entry, METH_VARARGS},
  {"ldap_passwd_s", _cffi_f_ldap_passwd_s, METH_VARARGS},
  {"ldap_rename_s", _cffi_f_ldap_rename_s, METH_VARARGS},
  {"ldap_search_ext_s", _cffi_f_ldap_search_ext_s, METH_VARARGS},
  {"ldap_set_option", _cffi_f_ldap_set_option, METH_VARARGS},
  {"ldap_simple_bind_s", _cffi_f_ldap_simple_bind_s, METH_VARARGS},
  {"_cffi_layout_struct_ldapmod", _cffi_layout_struct_ldapmod, METH_NOARGS},
  {"_cffi_setup", _cffi_setup, METH_VARARGS},
  {NULL, NULL}    /* Sentinel */
};

PyMODINIT_FUNC
init_cffi__x9a871d0dxf45fbc6f(void)
{
  PyObject *lib;
  lib = Py_InitModule("_cffi__x9a871d0dxf45fbc6f", _cffi_methods);
  if (lib == NULL || 0 < 0)
    return;
  _cffi_init();
  return;
}
