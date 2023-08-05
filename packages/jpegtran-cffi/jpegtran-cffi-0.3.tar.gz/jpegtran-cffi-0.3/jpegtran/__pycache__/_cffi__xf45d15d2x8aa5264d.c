
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



#include "Epeg.h"
#include "epeg_private.h"
#include "jmorecfg.h"
#include "jpeglib.h"
#include "cdjpeg.h"
#include "transupp.h"
#include "jerror.h"


static int _cffi_e__JCOPY_OPTION(PyObject *lib)
{
  if (JCOPYOPT_NONE != 0) {
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %d, not %d",
                 "JCOPY_OPTION", "JCOPYOPT_NONE", (int)JCOPYOPT_NONE, 0);
    return -1;
  }
  if (JCOPYOPT_COMMENTS != 1) {
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %d, not %d",
                 "JCOPY_OPTION", "JCOPYOPT_COMMENTS", (int)JCOPYOPT_COMMENTS, 1);
    return -1;
  }
  if (JCOPYOPT_ALL != 2) {
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %d, not %d",
                 "JCOPY_OPTION", "JCOPYOPT_ALL", (int)JCOPYOPT_ALL, 2);
    return -1;
  }
  return 0;
}

static int _cffi_e__JCROP_CODE(PyObject *lib)
{
  if (JCROP_UNSET != 0) {
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %d, not %d",
                 "JCROP_CODE", "JCROP_UNSET", (int)JCROP_UNSET, 0);
    return -1;
  }
  if (JCROP_POS != 1) {
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %d, not %d",
                 "JCROP_CODE", "JCROP_POS", (int)JCROP_POS, 1);
    return -1;
  }
  if (JCROP_NEG != 2) {
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %d, not %d",
                 "JCROP_CODE", "JCROP_NEG", (int)JCROP_NEG, 2);
    return -1;
  }
  if (JCROP_FORCE != 3) {
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %d, not %d",
                 "JCROP_CODE", "JCROP_FORCE", (int)JCROP_FORCE, 3);
    return -1;
  }
  return _cffi_e__JCOPY_OPTION(lib);
}

static int _cffi_e__JXFORM_CODE(PyObject *lib)
{
  if (JXFORM_NONE != 0) {
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %d, not %d",
                 "JXFORM_CODE", "JXFORM_NONE", (int)JXFORM_NONE, 0);
    return -1;
  }
  if (JXFORM_FLIP_H != 1) {
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %d, not %d",
                 "JXFORM_CODE", "JXFORM_FLIP_H", (int)JXFORM_FLIP_H, 1);
    return -1;
  }
  if (JXFORM_FLIP_V != 2) {
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %d, not %d",
                 "JXFORM_CODE", "JXFORM_FLIP_V", (int)JXFORM_FLIP_V, 2);
    return -1;
  }
  if (JXFORM_TRANSPOSE != 3) {
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %d, not %d",
                 "JXFORM_CODE", "JXFORM_TRANSPOSE", (int)JXFORM_TRANSPOSE, 3);
    return -1;
  }
  if (JXFORM_TRANSVERSE != 4) {
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %d, not %d",
                 "JXFORM_CODE", "JXFORM_TRANSVERSE", (int)JXFORM_TRANSVERSE, 4);
    return -1;
  }
  if (JXFORM_ROT_90 != 5) {
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %d, not %d",
                 "JXFORM_CODE", "JXFORM_ROT_90", (int)JXFORM_ROT_90, 5);
    return -1;
  }
  if (JXFORM_ROT_180 != 6) {
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %d, not %d",
                 "JXFORM_CODE", "JXFORM_ROT_180", (int)JXFORM_ROT_180, 6);
    return -1;
  }
  if (JXFORM_ROT_270 != 7) {
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %d, not %d",
                 "JXFORM_CODE", "JXFORM_ROT_270", (int)JXFORM_ROT_270, 7);
    return -1;
  }
  return _cffi_e__JCROP_CODE(lib);
}

static void _cffi_check__jpeg_transform_info(jpeg_transform_info *p)
{
  /* only to generate compile-time warnings or errors */
  { JXFORM_CODE *tmp = &p->transform; (void)tmp; }
  (void)((p->perfect) << 1);
  (void)((p->trim) << 1);
  (void)((p->force_grayscale) << 1);
  (void)((p->crop) << 1);
  (void)((p->crop_width) << 1);
  { JCROP_CODE *tmp = &p->crop_width_set; (void)tmp; }
  (void)((p->crop_height) << 1);
  { JCROP_CODE *tmp = &p->crop_height_set; (void)tmp; }
  (void)((p->crop_xoffset) << 1);
  { JCROP_CODE *tmp = &p->crop_xoffset_set; (void)tmp; }
  (void)((p->crop_yoffset) << 1);
  { JCROP_CODE *tmp = &p->crop_yoffset_set; (void)tmp; }
}
static PyObject *
_cffi_layout__jpeg_transform_info(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; jpeg_transform_info y; };
  static Py_ssize_t nums[] = {
    sizeof(jpeg_transform_info),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(jpeg_transform_info, transform),
    sizeof(((jpeg_transform_info *)0)->transform),
    offsetof(jpeg_transform_info, perfect),
    sizeof(((jpeg_transform_info *)0)->perfect),
    offsetof(jpeg_transform_info, trim),
    sizeof(((jpeg_transform_info *)0)->trim),
    offsetof(jpeg_transform_info, force_grayscale),
    sizeof(((jpeg_transform_info *)0)->force_grayscale),
    offsetof(jpeg_transform_info, crop),
    sizeof(((jpeg_transform_info *)0)->crop),
    offsetof(jpeg_transform_info, crop_width),
    sizeof(((jpeg_transform_info *)0)->crop_width),
    offsetof(jpeg_transform_info, crop_width_set),
    sizeof(((jpeg_transform_info *)0)->crop_width_set),
    offsetof(jpeg_transform_info, crop_height),
    sizeof(((jpeg_transform_info *)0)->crop_height),
    offsetof(jpeg_transform_info, crop_height_set),
    sizeof(((jpeg_transform_info *)0)->crop_height_set),
    offsetof(jpeg_transform_info, crop_xoffset),
    sizeof(((jpeg_transform_info *)0)->crop_xoffset),
    offsetof(jpeg_transform_info, crop_xoffset_set),
    sizeof(((jpeg_transform_info *)0)->crop_xoffset_set),
    offsetof(jpeg_transform_info, crop_yoffset),
    sizeof(((jpeg_transform_info *)0)->crop_yoffset),
    offsetof(jpeg_transform_info, crop_yoffset_set),
    sizeof(((jpeg_transform_info *)0)->crop_yoffset_set),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check__jpeg_transform_info(0);
}

static PyObject *
_cffi_f_epeg_close(PyObject *self, PyObject *arg0)
{
  Epeg_Image * x0;
  Py_ssize_t datasize;

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
  { epeg_close(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_epeg_decode_size_set(PyObject *self, PyObject *args)
{
  Epeg_Image * x0;
  int x1;
  int x2;
  Py_ssize_t datasize;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:epeg_decode_size_set", &arg0, &arg1, &arg2))
    return NULL;

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

  x1 = _cffi_to_c_SIGNED(arg1, int);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  x2 = _cffi_to_c_SIGNED(arg2, int);
  if (x2 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { epeg_decode_size_set(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_epeg_encode(PyObject *self, PyObject *arg0)
{
  Epeg_Image * x0;
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
  { result = epeg_encode(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_epeg_file_open(PyObject *self, PyObject *arg0)
{
  char const * x0;
  Py_ssize_t datasize;
  Epeg_Image * result;

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

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = epeg_file_open(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(0));
}

static PyObject *
_cffi_f_epeg_file_output_set(PyObject *self, PyObject *args)
{
  Epeg_Image * x0;
  char const * x1;
  Py_ssize_t datasize;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:epeg_file_output_set", &arg0, &arg1))
    return NULL;

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

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(2), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { epeg_file_output_set(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_epeg_memory_open(PyObject *self, PyObject *args)
{
  unsigned char * x0;
  int x1;
  Py_ssize_t datasize;
  Epeg_Image * result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:epeg_memory_open", &arg0, &arg1))
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

  x1 = _cffi_to_c_SIGNED(arg1, int);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = epeg_memory_open(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(0));
}

static PyObject *
_cffi_f_epeg_memory_output_set(PyObject *self, PyObject *args)
{
  Epeg_Image * x0;
  unsigned char * * x1;
  int * x2;
  Py_ssize_t datasize;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:epeg_memory_output_set", &arg0, &arg1, &arg2))
    return NULL;

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

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(4), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(5), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(5), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { epeg_memory_output_set(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_epeg_quality_set(PyObject *self, PyObject *args)
{
  Epeg_Image * x0;
  int x1;
  Py_ssize_t datasize;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:epeg_quality_set", &arg0, &arg1))
    return NULL;

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

  x1 = _cffi_to_c_SIGNED(arg1, int);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { epeg_quality_set(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_epeg_size_get(PyObject *self, PyObject *args)
{
  Epeg_Image * x0;
  int * x1;
  int * x2;
  Py_ssize_t datasize;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:epeg_size_get", &arg0, &arg1, &arg2))
    return NULL;

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
      _cffi_type(5), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(5), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { epeg_size_get(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_epeg_trim(PyObject *self, PyObject *arg0)
{
  Epeg_Image * x0;
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
  { result = epeg_trim(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_jcopy_markers_execute(PyObject *self, PyObject *args)
{
  struct jpeg_decompress_struct * x0;
  struct jpeg_compress_struct * x1;
  JCOPY_OPTION x2;
  Py_ssize_t datasize;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:jcopy_markers_execute", &arg0, &arg1, &arg2))
    return NULL;

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

  if (_cffi_to_c((char *)&x2, _cffi_type(8), arg2) < 0)
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { jcopy_markers_execute(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_jcopy_markers_setup(PyObject *self, PyObject *args)
{
  struct jpeg_decompress_struct * x0;
  JCOPY_OPTION x1;
  Py_ssize_t datasize;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:jcopy_markers_setup", &arg0, &arg1))
    return NULL;

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

  if (_cffi_to_c((char *)&x1, _cffi_type(8), arg1) < 0)
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { jcopy_markers_setup(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_jpeg_copy_critical_parameters(PyObject *self, PyObject *args)
{
  struct jpeg_decompress_struct * x0;
  struct jpeg_compress_struct * x1;
  Py_ssize_t datasize;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:jpeg_copy_critical_parameters", &arg0, &arg1))
    return NULL;

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
  { jpeg_copy_critical_parameters(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_jpeg_create_compress(PyObject *self, PyObject *arg0)
{
  struct jpeg_compress_struct * x0;
  Py_ssize_t datasize;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(7), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(7), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { jpeg_create_compress(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_jpeg_create_decompress(PyObject *self, PyObject *arg0)
{
  struct jpeg_decompress_struct * x0;
  Py_ssize_t datasize;

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
  { jpeg_create_decompress(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_jpeg_destroy_compress(PyObject *self, PyObject *arg0)
{
  struct jpeg_compress_struct * x0;
  Py_ssize_t datasize;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(7), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(7), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { jpeg_destroy_compress(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_jpeg_destroy_decompress(PyObject *self, PyObject *arg0)
{
  struct jpeg_decompress_struct * x0;
  Py_ssize_t datasize;

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
  { jpeg_destroy_decompress(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_jpeg_finish_compress(PyObject *self, PyObject *arg0)
{
  struct jpeg_compress_struct * x0;
  Py_ssize_t datasize;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(7), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(7), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { jpeg_finish_compress(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_jpeg_finish_decompress(PyObject *self, PyObject *arg0)
{
  struct jpeg_decompress_struct * x0;
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
  { result = jpeg_finish_decompress(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_jpeg_mem_dest(PyObject *self, PyObject *args)
{
  struct jpeg_compress_struct * x0;
  unsigned char * * x1;
  unsigned long * x2;
  Py_ssize_t datasize;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:jpeg_mem_dest", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(7), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(7), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(4), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(4), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(9), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(9), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { jpeg_mem_dest(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_jpeg_mem_src(PyObject *self, PyObject *args)
{
  struct jpeg_decompress_struct * x0;
  unsigned char * x1;
  unsigned long x2;
  Py_ssize_t datasize;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:jpeg_mem_src", &arg0, &arg1, &arg2))
    return NULL;

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

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(3), arg1) < 0)
      return NULL;
  }

  x2 = _cffi_to_c_UNSIGNED(arg2, unsigned long);
  if (x2 == (unsigned long)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { jpeg_mem_src(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_jpeg_read_coefficients(PyObject *self, PyObject *arg0)
{
  struct jpeg_decompress_struct * x0;
  Py_ssize_t datasize;
  jvirt_barray_ptr * result;

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
  { result = jpeg_read_coefficients(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(10));
}

static PyObject *
_cffi_f_jpeg_read_header(PyObject *self, PyObject *args)
{
  struct jpeg_decompress_struct * x0;
  int x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:jpeg_read_header", &arg0, &arg1))
    return NULL;

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

  x1 = _cffi_to_c_SIGNED(arg1, int);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = jpeg_read_header(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_jpeg_std_error(PyObject *self, PyObject *arg0)
{
  struct jpeg_error_mgr * x0;
  Py_ssize_t datasize;
  struct jpeg_error_mgr * result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(11), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(11), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = jpeg_std_error(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(11));
}

static PyObject *
_cffi_f_jpeg_write_coefficients(PyObject *self, PyObject *args)
{
  struct jpeg_compress_struct * x0;
  jvirt_barray_ptr * x1;
  Py_ssize_t datasize;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:jpeg_write_coefficients", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(7), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(7), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(10), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(10), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { jpeg_write_coefficients(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_jtransform_adjust_parameters(PyObject *self, PyObject *args)
{
  struct jpeg_decompress_struct * x0;
  struct jpeg_compress_struct * x1;
  jvirt_barray_ptr * x2;
  jpeg_transform_info * x3;
  Py_ssize_t datasize;
  jvirt_barray_ptr * result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:jtransform_adjust_parameters", &arg0, &arg1, &arg2, &arg3))
    return NULL;

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
      _cffi_type(10), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(10), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(12), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca(datasize);
    memset((void *)x3, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(12), arg3) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = jtransform_adjust_parameters(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_pointer((char *)result, _cffi_type(10));
}

static PyObject *
_cffi_f_jtransform_execute_transform(PyObject *self, PyObject *args)
{
  struct jpeg_decompress_struct * x0;
  struct jpeg_compress_struct * x1;
  jvirt_barray_ptr * x2;
  jpeg_transform_info * x3;
  Py_ssize_t datasize;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:jtransform_execute_transform", &arg0, &arg1, &arg2, &arg3))
    return NULL;

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
      _cffi_type(10), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(10), arg2) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(12), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca(datasize);
    memset((void *)x3, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(12), arg3) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { jtransform_execute_transform(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_jtransform_request_workspace(PyObject *self, PyObject *args)
{
  struct jpeg_decompress_struct * x0;
  jpeg_transform_info * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:jtransform_request_workspace", &arg0, &arg1))
    return NULL;

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

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(12), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(12), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = jtransform_request_workspace(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static void _cffi_check_struct_jpeg_common_struct(struct jpeg_common_struct *p)
{
  /* only to generate compile-time warnings or errors */
  { struct jpeg_error_mgr * *tmp = &p->err; (void)tmp; }
}
static PyObject *
_cffi_layout_struct_jpeg_common_struct(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct jpeg_common_struct y; };
  static Py_ssize_t nums[] = {
    sizeof(struct jpeg_common_struct),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct jpeg_common_struct, err),
    sizeof(((struct jpeg_common_struct *)0)->err),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_jpeg_common_struct(0);
}

static void _cffi_check_struct_jpeg_compress_struct(struct jpeg_compress_struct *p)
{
  /* only to generate compile-time warnings or errors */
  { struct jpeg_error_mgr * *tmp = &p->err; (void)tmp; }
}
static PyObject *
_cffi_layout_struct_jpeg_compress_struct(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct jpeg_compress_struct y; };
  static Py_ssize_t nums[] = {
    sizeof(struct jpeg_compress_struct),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct jpeg_compress_struct, err),
    sizeof(((struct jpeg_compress_struct *)0)->err),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_jpeg_compress_struct(0);
}

static void _cffi_check_struct_jpeg_decompress_struct(struct jpeg_decompress_struct *p)
{
  /* only to generate compile-time warnings or errors */
  { struct jpeg_error_mgr * *tmp = &p->err; (void)tmp; }
}
static PyObject *
_cffi_layout_struct_jpeg_decompress_struct(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct jpeg_decompress_struct y; };
  static Py_ssize_t nums[] = {
    sizeof(struct jpeg_decompress_struct),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct jpeg_decompress_struct, err),
    sizeof(((struct jpeg_decompress_struct *)0)->err),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_jpeg_decompress_struct(0);
}

static void _cffi_check_struct_jpeg_error_mgr(struct jpeg_error_mgr *p)
{
  /* only to generate compile-time warnings or errors */
  { void(* *tmp)(struct jpeg_common_struct *) = &p->reset_error_mgr; (void)tmp; }
  { void(* *tmp)(struct jpeg_common_struct *, int) = &p->emit_message; (void)tmp; }
  (void)((p->trace_level) << 1);
  (void)((p->num_warnings) << 1);
  (void)((p->msg_code) << 1);
}
static PyObject *
_cffi_layout_struct_jpeg_error_mgr(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct jpeg_error_mgr y; };
  static Py_ssize_t nums[] = {
    sizeof(struct jpeg_error_mgr),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct jpeg_error_mgr, reset_error_mgr),
    sizeof(((struct jpeg_error_mgr *)0)->reset_error_mgr),
    offsetof(struct jpeg_error_mgr, emit_message),
    sizeof(((struct jpeg_error_mgr *)0)->emit_message),
    offsetof(struct jpeg_error_mgr, trace_level),
    sizeof(((struct jpeg_error_mgr *)0)->trace_level),
    offsetof(struct jpeg_error_mgr, num_warnings),
    sizeof(((struct jpeg_error_mgr *)0)->num_warnings),
    offsetof(struct jpeg_error_mgr, msg_code),
    sizeof(((struct jpeg_error_mgr *)0)->msg_code),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_jpeg_error_mgr(0);
}

static PyObject *_cffi_setup_custom(PyObject *lib)
{
  if (_cffi_e__JXFORM_CODE(lib) < 0)
    return NULL;
  Py_INCREF(Py_None);
  return Py_None;
}

static PyMethodDef _cffi_methods[] = {
  {"_cffi_layout__jpeg_transform_info", _cffi_layout__jpeg_transform_info, METH_NOARGS},
  {"epeg_close", _cffi_f_epeg_close, METH_O},
  {"epeg_decode_size_set", _cffi_f_epeg_decode_size_set, METH_VARARGS},
  {"epeg_encode", _cffi_f_epeg_encode, METH_O},
  {"epeg_file_open", _cffi_f_epeg_file_open, METH_O},
  {"epeg_file_output_set", _cffi_f_epeg_file_output_set, METH_VARARGS},
  {"epeg_memory_open", _cffi_f_epeg_memory_open, METH_VARARGS},
  {"epeg_memory_output_set", _cffi_f_epeg_memory_output_set, METH_VARARGS},
  {"epeg_quality_set", _cffi_f_epeg_quality_set, METH_VARARGS},
  {"epeg_size_get", _cffi_f_epeg_size_get, METH_VARARGS},
  {"epeg_trim", _cffi_f_epeg_trim, METH_O},
  {"jcopy_markers_execute", _cffi_f_jcopy_markers_execute, METH_VARARGS},
  {"jcopy_markers_setup", _cffi_f_jcopy_markers_setup, METH_VARARGS},
  {"jpeg_copy_critical_parameters", _cffi_f_jpeg_copy_critical_parameters, METH_VARARGS},
  {"jpeg_create_compress", _cffi_f_jpeg_create_compress, METH_O},
  {"jpeg_create_decompress", _cffi_f_jpeg_create_decompress, METH_O},
  {"jpeg_destroy_compress", _cffi_f_jpeg_destroy_compress, METH_O},
  {"jpeg_destroy_decompress", _cffi_f_jpeg_destroy_decompress, METH_O},
  {"jpeg_finish_compress", _cffi_f_jpeg_finish_compress, METH_O},
  {"jpeg_finish_decompress", _cffi_f_jpeg_finish_decompress, METH_O},
  {"jpeg_mem_dest", _cffi_f_jpeg_mem_dest, METH_VARARGS},
  {"jpeg_mem_src", _cffi_f_jpeg_mem_src, METH_VARARGS},
  {"jpeg_read_coefficients", _cffi_f_jpeg_read_coefficients, METH_O},
  {"jpeg_read_header", _cffi_f_jpeg_read_header, METH_VARARGS},
  {"jpeg_std_error", _cffi_f_jpeg_std_error, METH_O},
  {"jpeg_write_coefficients", _cffi_f_jpeg_write_coefficients, METH_VARARGS},
  {"jtransform_adjust_parameters", _cffi_f_jtransform_adjust_parameters, METH_VARARGS},
  {"jtransform_execute_transform", _cffi_f_jtransform_execute_transform, METH_VARARGS},
  {"jtransform_request_workspace", _cffi_f_jtransform_request_workspace, METH_VARARGS},
  {"_cffi_layout_struct_jpeg_common_struct", _cffi_layout_struct_jpeg_common_struct, METH_NOARGS},
  {"_cffi_layout_struct_jpeg_compress_struct", _cffi_layout_struct_jpeg_compress_struct, METH_NOARGS},
  {"_cffi_layout_struct_jpeg_decompress_struct", _cffi_layout_struct_jpeg_decompress_struct, METH_NOARGS},
  {"_cffi_layout_struct_jpeg_error_mgr", _cffi_layout_struct_jpeg_error_mgr, METH_NOARGS},
  {"_cffi_setup", _cffi_setup, METH_VARARGS},
  {NULL, NULL}    /* Sentinel */
};

PyMODINIT_FUNC
init_cffi__xf45d15d2x8aa5264d(void)
{
  PyObject *lib;
  lib = Py_InitModule("_cffi__xf45d15d2x8aa5264d", _cffi_methods);
  if (lib == NULL || 0 < 0)
    return;
  _cffi_init();
  return;
}
