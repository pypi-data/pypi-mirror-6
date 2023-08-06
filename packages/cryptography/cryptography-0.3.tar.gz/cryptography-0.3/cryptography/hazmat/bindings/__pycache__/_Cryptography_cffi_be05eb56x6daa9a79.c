
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




#include <CommonCrypto/CommonDigest.h>


#include <CommonCrypto/CommonHMAC.h>


#include <CommonCrypto/CommonKeyDerivation.h>


#include <CommonCrypto/CommonCryptor.h>



int CC_MD5_Init(CC_MD5_CTX *);
int CC_MD5_Update(CC_MD5_CTX *, const void *, CC_LONG);
int CC_MD5_Final(unsigned char *, CC_MD5_CTX *);

int CC_SHA1_Init(CC_SHA1_CTX *);
int CC_SHA1_Update(CC_SHA1_CTX *, const void *, CC_LONG);
int CC_SHA1_Final(unsigned char *, CC_SHA1_CTX *);

int CC_SHA224_Init(CC_SHA256_CTX *);
int CC_SHA224_Update(CC_SHA256_CTX *, const void *, CC_LONG);
int CC_SHA224_Final(unsigned char *, CC_SHA256_CTX *);

int CC_SHA256_Init(CC_SHA256_CTX *);
int CC_SHA256_Update(CC_SHA256_CTX *, const void *, CC_LONG);
int CC_SHA256_Final(unsigned char *, CC_SHA256_CTX *);

int CC_SHA384_Init(CC_SHA512_CTX *);
int CC_SHA384_Update(CC_SHA512_CTX *, const void *, CC_LONG);
int CC_SHA384_Final(unsigned char *, CC_SHA512_CTX *);

int CC_SHA512_Init(CC_SHA512_CTX *);
int CC_SHA512_Update(CC_SHA512_CTX *, const void *, CC_LONG);
int CC_SHA512_Final(unsigned char *, CC_SHA512_CTX *);


void CCHmacInit(CCHmacContext *, CCHmacAlgorithm, const void *, size_t);
void CCHmacUpdate(CCHmacContext *, const void *, size_t);
void CCHmacFinal(CCHmacContext *, void *);



int CCKeyDerivationPBKDF(CCPBKDFAlgorithm, const char *, size_t,
                         const uint8_t *, size_t, CCPseudoRandomAlgorithm,
                         uint, uint8_t *, size_t);
uint CCCalibratePBKDF(CCPBKDFAlgorithm, size_t, size_t,
                      CCPseudoRandomAlgorithm, size_t, uint32_t);


CCCryptorStatus CCCryptorCreateWithMode(CCOperation, CCMode, CCAlgorithm,
                                        CCPadding, const void *, const void *,
                                        size_t, const void *, size_t, int,
                                        CCModeOptions, CCCryptorRef *);
CCCryptorStatus CCCryptorCreate(CCOperation, CCAlgorithm, CCOptions,
                                const void *, size_t, const void *,
                                CCCryptorRef *);
CCCryptorStatus CCCryptorUpdate(CCCryptorRef, const void *, size_t, void *,
                                size_t, size_t *);
CCCryptorStatus CCCryptorFinal(CCCryptorRef, void *, size_t, size_t *);
CCCryptorStatus CCCryptorRelease(CCCryptorRef);

CCCryptorStatus CCCryptorGCMAddIV(CCCryptorRef, const void *, size_t);
CCCryptorStatus CCCryptorGCMAddAAD(CCCryptorRef, const void *, size_t);
CCCryptorStatus CCCryptorGCMEncrypt(CCCryptorRef, const void *, size_t,
                                    void *);
CCCryptorStatus CCCryptorGCMDecrypt(CCCryptorRef, const void *, size_t,
                                    void *);
CCCryptorStatus CCCryptorGCMFinal(CCCryptorRef, const void *, size_t *);
CCCryptorStatus CCCryptorGCMReset(CCCryptorRef);








// Not defined in the public header
enum {
    kCCModeGCM = 11
};


static int _cffi_e__$enum_$1(PyObject *lib)
{
  if ((kCCHmacAlgSHA1) < 0 || (unsigned long)(kCCHmacAlgSHA1) != 0UL) {
    char buf[64];
    if ((kCCHmacAlgSHA1) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCHmacAlgSHA1));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCHmacAlgSHA1));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$1", "kCCHmacAlgSHA1", buf, "0");
    return -1;
  }
  if ((kCCHmacAlgMD5) < 0 || (unsigned long)(kCCHmacAlgMD5) != 1UL) {
    char buf[64];
    if ((kCCHmacAlgMD5) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCHmacAlgMD5));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCHmacAlgMD5));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$1", "kCCHmacAlgMD5", buf, "1");
    return -1;
  }
  if ((kCCHmacAlgSHA256) < 0 || (unsigned long)(kCCHmacAlgSHA256) != 2UL) {
    char buf[64];
    if ((kCCHmacAlgSHA256) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCHmacAlgSHA256));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCHmacAlgSHA256));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$1", "kCCHmacAlgSHA256", buf, "2");
    return -1;
  }
  if ((kCCHmacAlgSHA384) < 0 || (unsigned long)(kCCHmacAlgSHA384) != 3UL) {
    char buf[64];
    if ((kCCHmacAlgSHA384) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCHmacAlgSHA384));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCHmacAlgSHA384));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$1", "kCCHmacAlgSHA384", buf, "3");
    return -1;
  }
  if ((kCCHmacAlgSHA512) < 0 || (unsigned long)(kCCHmacAlgSHA512) != 4UL) {
    char buf[64];
    if ((kCCHmacAlgSHA512) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCHmacAlgSHA512));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCHmacAlgSHA512));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$1", "kCCHmacAlgSHA512", buf, "4");
    return -1;
  }
  if ((kCCHmacAlgSHA224) < 0 || (unsigned long)(kCCHmacAlgSHA224) != 5UL) {
    char buf[64];
    if ((kCCHmacAlgSHA224) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCHmacAlgSHA224));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCHmacAlgSHA224));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$1", "kCCHmacAlgSHA224", buf, "5");
    return -1;
  }
  return 0;
}

static int _cffi_e__$enum_$2(PyObject *lib)
{
  if ((kCCPBKDF2) < 0 || (unsigned long)(kCCPBKDF2) != 2UL) {
    char buf[64];
    if ((kCCPBKDF2) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCPBKDF2));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCPBKDF2));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$2", "kCCPBKDF2", buf, "2");
    return -1;
  }
  return _cffi_e__$enum_$1(lib);
}

static int _cffi_e__$enum_$3(PyObject *lib)
{
  if ((kCCPRFHmacAlgSHA1) < 0 || (unsigned long)(kCCPRFHmacAlgSHA1) != 1UL) {
    char buf[64];
    if ((kCCPRFHmacAlgSHA1) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCPRFHmacAlgSHA1));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCPRFHmacAlgSHA1));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$3", "kCCPRFHmacAlgSHA1", buf, "1");
    return -1;
  }
  if ((kCCPRFHmacAlgSHA224) < 0 || (unsigned long)(kCCPRFHmacAlgSHA224) != 2UL) {
    char buf[64];
    if ((kCCPRFHmacAlgSHA224) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCPRFHmacAlgSHA224));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCPRFHmacAlgSHA224));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$3", "kCCPRFHmacAlgSHA224", buf, "2");
    return -1;
  }
  if ((kCCPRFHmacAlgSHA256) < 0 || (unsigned long)(kCCPRFHmacAlgSHA256) != 3UL) {
    char buf[64];
    if ((kCCPRFHmacAlgSHA256) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCPRFHmacAlgSHA256));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCPRFHmacAlgSHA256));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$3", "kCCPRFHmacAlgSHA256", buf, "3");
    return -1;
  }
  if ((kCCPRFHmacAlgSHA384) < 0 || (unsigned long)(kCCPRFHmacAlgSHA384) != 4UL) {
    char buf[64];
    if ((kCCPRFHmacAlgSHA384) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCPRFHmacAlgSHA384));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCPRFHmacAlgSHA384));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$3", "kCCPRFHmacAlgSHA384", buf, "4");
    return -1;
  }
  if ((kCCPRFHmacAlgSHA512) < 0 || (unsigned long)(kCCPRFHmacAlgSHA512) != 5UL) {
    char buf[64];
    if ((kCCPRFHmacAlgSHA512) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCPRFHmacAlgSHA512));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCPRFHmacAlgSHA512));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$3", "kCCPRFHmacAlgSHA512", buf, "5");
    return -1;
  }
  return _cffi_e__$enum_$2(lib);
}

static int _cffi_e__$enum_$4(PyObject *lib)
{
  if ((kCCAlgorithmAES128) < 0 || (unsigned long)(kCCAlgorithmAES128) != 0UL) {
    char buf[64];
    if ((kCCAlgorithmAES128) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCAlgorithmAES128));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCAlgorithmAES128));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$4", "kCCAlgorithmAES128", buf, "0");
    return -1;
  }
  if ((kCCAlgorithmDES) < 0 || (unsigned long)(kCCAlgorithmDES) != 1UL) {
    char buf[64];
    if ((kCCAlgorithmDES) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCAlgorithmDES));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCAlgorithmDES));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$4", "kCCAlgorithmDES", buf, "1");
    return -1;
  }
  if ((kCCAlgorithm3DES) < 0 || (unsigned long)(kCCAlgorithm3DES) != 2UL) {
    char buf[64];
    if ((kCCAlgorithm3DES) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCAlgorithm3DES));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCAlgorithm3DES));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$4", "kCCAlgorithm3DES", buf, "2");
    return -1;
  }
  if ((kCCAlgorithmCAST) < 0 || (unsigned long)(kCCAlgorithmCAST) != 3UL) {
    char buf[64];
    if ((kCCAlgorithmCAST) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCAlgorithmCAST));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCAlgorithmCAST));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$4", "kCCAlgorithmCAST", buf, "3");
    return -1;
  }
  if ((kCCAlgorithmRC4) < 0 || (unsigned long)(kCCAlgorithmRC4) != 4UL) {
    char buf[64];
    if ((kCCAlgorithmRC4) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCAlgorithmRC4));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCAlgorithmRC4));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$4", "kCCAlgorithmRC4", buf, "4");
    return -1;
  }
  if ((kCCAlgorithmRC2) < 0 || (unsigned long)(kCCAlgorithmRC2) != 5UL) {
    char buf[64];
    if ((kCCAlgorithmRC2) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCAlgorithmRC2));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCAlgorithmRC2));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$4", "kCCAlgorithmRC2", buf, "5");
    return -1;
  }
  if ((kCCAlgorithmBlowfish) < 0 || (unsigned long)(kCCAlgorithmBlowfish) != 6UL) {
    char buf[64];
    if ((kCCAlgorithmBlowfish) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCAlgorithmBlowfish));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCAlgorithmBlowfish));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$4", "kCCAlgorithmBlowfish", buf, "6");
    return -1;
  }
  return _cffi_e__$enum_$3(lib);
}

static int _cffi_e__$enum_$5(PyObject *lib)
{
  if ((kCCSuccess) < 0 || (unsigned long)(kCCSuccess) != 0UL) {
    char buf[64];
    if ((kCCSuccess) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCSuccess));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCSuccess));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$5", "kCCSuccess", buf, "0");
    return -1;
  }
  if ((kCCParamError) >= 0 || (long)(kCCParamError) != -4300L) {
    char buf[64];
    if ((kCCParamError) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCParamError));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCParamError));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$5", "kCCParamError", buf, "-4300");
    return -1;
  }
  if ((kCCBufferTooSmall) >= 0 || (long)(kCCBufferTooSmall) != -4301L) {
    char buf[64];
    if ((kCCBufferTooSmall) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCBufferTooSmall));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCBufferTooSmall));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$5", "kCCBufferTooSmall", buf, "-4301");
    return -1;
  }
  if ((kCCMemoryFailure) >= 0 || (long)(kCCMemoryFailure) != -4302L) {
    char buf[64];
    if ((kCCMemoryFailure) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCMemoryFailure));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCMemoryFailure));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$5", "kCCMemoryFailure", buf, "-4302");
    return -1;
  }
  if ((kCCAlignmentError) >= 0 || (long)(kCCAlignmentError) != -4303L) {
    char buf[64];
    if ((kCCAlignmentError) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCAlignmentError));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCAlignmentError));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$5", "kCCAlignmentError", buf, "-4303");
    return -1;
  }
  if ((kCCDecodeError) >= 0 || (long)(kCCDecodeError) != -4304L) {
    char buf[64];
    if ((kCCDecodeError) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCDecodeError));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCDecodeError));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$5", "kCCDecodeError", buf, "-4304");
    return -1;
  }
  if ((kCCUnimplemented) >= 0 || (long)(kCCUnimplemented) != -4305L) {
    char buf[64];
    if ((kCCUnimplemented) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCUnimplemented));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCUnimplemented));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$5", "kCCUnimplemented", buf, "-4305");
    return -1;
  }
  return _cffi_e__$enum_$4(lib);
}

static int _cffi_e__$enum_$6(PyObject *lib)
{
  if ((kCCEncrypt) < 0 || (unsigned long)(kCCEncrypt) != 0UL) {
    char buf[64];
    if ((kCCEncrypt) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCEncrypt));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCEncrypt));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$6", "kCCEncrypt", buf, "0");
    return -1;
  }
  if ((kCCDecrypt) < 0 || (unsigned long)(kCCDecrypt) != 1UL) {
    char buf[64];
    if ((kCCDecrypt) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCDecrypt));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCDecrypt));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$6", "kCCDecrypt", buf, "1");
    return -1;
  }
  return _cffi_e__$enum_$5(lib);
}

static int _cffi_e__$enum_$7(PyObject *lib)
{
  if ((kCCModeOptionCTR_LE) < 0 || (unsigned long)(kCCModeOptionCTR_LE) != 1UL) {
    char buf[64];
    if ((kCCModeOptionCTR_LE) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCModeOptionCTR_LE));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCModeOptionCTR_LE));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$7", "kCCModeOptionCTR_LE", buf, "1");
    return -1;
  }
  if ((kCCModeOptionCTR_BE) < 0 || (unsigned long)(kCCModeOptionCTR_BE) != 2UL) {
    char buf[64];
    if ((kCCModeOptionCTR_BE) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCModeOptionCTR_BE));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCModeOptionCTR_BE));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$7", "kCCModeOptionCTR_BE", buf, "2");
    return -1;
  }
  return _cffi_e__$enum_$6(lib);
}

static int _cffi_e__$enum_$8(PyObject *lib)
{
  if ((kCCModeECB) < 0 || (unsigned long)(kCCModeECB) != 1UL) {
    char buf[64];
    if ((kCCModeECB) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCModeECB));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCModeECB));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$8", "kCCModeECB", buf, "1");
    return -1;
  }
  if ((kCCModeCBC) < 0 || (unsigned long)(kCCModeCBC) != 2UL) {
    char buf[64];
    if ((kCCModeCBC) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCModeCBC));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCModeCBC));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$8", "kCCModeCBC", buf, "2");
    return -1;
  }
  if ((kCCModeCFB) < 0 || (unsigned long)(kCCModeCFB) != 3UL) {
    char buf[64];
    if ((kCCModeCFB) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCModeCFB));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCModeCFB));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$8", "kCCModeCFB", buf, "3");
    return -1;
  }
  if ((kCCModeCTR) < 0 || (unsigned long)(kCCModeCTR) != 4UL) {
    char buf[64];
    if ((kCCModeCTR) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCModeCTR));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCModeCTR));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$8", "kCCModeCTR", buf, "4");
    return -1;
  }
  if ((kCCModeF8) < 0 || (unsigned long)(kCCModeF8) != 5UL) {
    char buf[64];
    if ((kCCModeF8) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCModeF8));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCModeF8));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$8", "kCCModeF8", buf, "5");
    return -1;
  }
  if ((kCCModeLRW) < 0 || (unsigned long)(kCCModeLRW) != 6UL) {
    char buf[64];
    if ((kCCModeLRW) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCModeLRW));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCModeLRW));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$8", "kCCModeLRW", buf, "6");
    return -1;
  }
  if ((kCCModeOFB) < 0 || (unsigned long)(kCCModeOFB) != 7UL) {
    char buf[64];
    if ((kCCModeOFB) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCModeOFB));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCModeOFB));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$8", "kCCModeOFB", buf, "7");
    return -1;
  }
  if ((kCCModeXTS) < 0 || (unsigned long)(kCCModeXTS) != 8UL) {
    char buf[64];
    if ((kCCModeXTS) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCModeXTS));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCModeXTS));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$8", "kCCModeXTS", buf, "8");
    return -1;
  }
  if ((kCCModeRC4) < 0 || (unsigned long)(kCCModeRC4) != 9UL) {
    char buf[64];
    if ((kCCModeRC4) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCModeRC4));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCModeRC4));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$8", "kCCModeRC4", buf, "9");
    return -1;
  }
  if ((kCCModeCFB8) < 0 || (unsigned long)(kCCModeCFB8) != 10UL) {
    char buf[64];
    if ((kCCModeCFB8) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCModeCFB8));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCModeCFB8));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$8", "kCCModeCFB8", buf, "10");
    return -1;
  }
  if ((kCCModeGCM) < 0 || (unsigned long)(kCCModeGCM) != 11UL) {
    char buf[64];
    if ((kCCModeGCM) < 0)
        snprintf(buf, 63, "%ld", (long)(kCCModeGCM));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(kCCModeGCM));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$8", "kCCModeGCM", buf, "11");
    return -1;
  }
  return _cffi_e__$enum_$7(lib);
}

static int _cffi_e__$enum_$9(PyObject *lib)
{
  if ((ccNoPadding) < 0 || (unsigned long)(ccNoPadding) != 0UL) {
    char buf[64];
    if ((ccNoPadding) < 0)
        snprintf(buf, 63, "%ld", (long)(ccNoPadding));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(ccNoPadding));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$9", "ccNoPadding", buf, "0");
    return -1;
  }
  if ((ccPKCS7Padding) < 0 || (unsigned long)(ccPKCS7Padding) != 1UL) {
    char buf[64];
    if ((ccPKCS7Padding) < 0)
        snprintf(buf, 63, "%ld", (long)(ccPKCS7Padding));
    else
        snprintf(buf, 63, "%lu", (unsigned long)(ccPKCS7Padding));
    PyErr_Format(_cffi_VerificationError,
                 "enum %s: %s has the real value %s, not %s",
                 "$enum_$9", "ccPKCS7Padding", buf, "1");
    return -1;
  }
  return _cffi_e__$enum_$8(lib);
}

static void _cffi_check__CCHmacContext(CCHmacContext *p)
{
  /* only to generate compile-time warnings or errors */
}
static PyObject *
_cffi_layout__CCHmacContext(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; CCHmacContext y; };
  static Py_ssize_t nums[] = {
    sizeof(CCHmacContext),
    offsetof(struct _cffi_aligncheck, y),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check__CCHmacContext(0);
}

static PyObject *
_cffi_f_CCCalibratePBKDF(PyObject *self, PyObject *args)
{
  uint32_t x0;
  size_t x1;
  size_t x2;
  uint32_t x3;
  size_t x4;
  uint32_t x5;
  unsigned int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;
  PyObject *arg5;

  if (!PyArg_ParseTuple(args, "OOOOOO:CCCalibratePBKDF", &arg0, &arg1, &arg2, &arg3, &arg4, &arg5))
    return NULL;

  x0 = _cffi_to_c_UNSIGNED(arg0, uint32_t);
  if (x0 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

  x1 = _cffi_to_c_UNSIGNED(arg1, size_t);
  if (x1 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  x2 = _cffi_to_c_UNSIGNED(arg2, size_t);
  if (x2 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  x3 = _cffi_to_c_UNSIGNED(arg3, uint32_t);
  if (x3 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

  x4 = _cffi_to_c_UNSIGNED(arg4, size_t);
  if (x4 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  x5 = _cffi_to_c_UNSIGNED(arg5, uint32_t);
  if (x5 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CCCalibratePBKDF(x0, x1, x2, x3, x4, x5); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_UNSIGNED(result, unsigned int);
}

static PyObject *
_cffi_f_CCCryptorCreate(PyObject *self, PyObject *args)
{
  uint32_t x0;
  uint32_t x1;
  uint32_t x2;
  void const * x3;
  size_t x4;
  void const * x5;
  CCCryptorRef * x6;
  Py_ssize_t datasize;
  int32_t result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;
  PyObject *arg5;
  PyObject *arg6;

  if (!PyArg_ParseTuple(args, "OOOOOOO:CCCryptorCreate", &arg0, &arg1, &arg2, &arg3, &arg4, &arg5, &arg6))
    return NULL;

  x0 = _cffi_to_c_UNSIGNED(arg0, uint32_t);
  if (x0 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

  x1 = _cffi_to_c_UNSIGNED(arg1, uint32_t);
  if (x1 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

  x2 = _cffi_to_c_UNSIGNED(arg2, uint32_t);
  if (x2 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

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

  x4 = _cffi_to_c_UNSIGNED(arg4, size_t);
  if (x4 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg5, (char **)&x5);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x5 = alloca(datasize);
    memset((void *)x5, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x5, _cffi_type(0), arg5) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg6, (char **)&x6);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x6 = alloca(datasize);
    memset((void *)x6, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x6, _cffi_type(1), arg6) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CCCryptorCreate(x0, x1, x2, x3, x4, x5, x6); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int32_t);
}

static PyObject *
_cffi_f_CCCryptorCreateWithMode(PyObject *self, PyObject *args)
{
  uint32_t x0;
  uint32_t x1;
  uint32_t x2;
  uint32_t x3;
  void const * x4;
  void const * x5;
  size_t x6;
  void const * x7;
  size_t x8;
  int x9;
  uint32_t x10;
  CCCryptorRef * x11;
  Py_ssize_t datasize;
  int32_t result;
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
  PyObject *arg11;

  if (!PyArg_ParseTuple(args, "OOOOOOOOOOOO:CCCryptorCreateWithMode", &arg0, &arg1, &arg2, &arg3, &arg4, &arg5, &arg6, &arg7, &arg8, &arg9, &arg10, &arg11))
    return NULL;

  x0 = _cffi_to_c_UNSIGNED(arg0, uint32_t);
  if (x0 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

  x1 = _cffi_to_c_UNSIGNED(arg1, uint32_t);
  if (x1 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

  x2 = _cffi_to_c_UNSIGNED(arg2, uint32_t);
  if (x2 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

  x3 = _cffi_to_c_UNSIGNED(arg3, uint32_t);
  if (x3 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg4, (char **)&x4);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x4 = alloca(datasize);
    memset((void *)x4, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x4, _cffi_type(0), arg4) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg5, (char **)&x5);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x5 = alloca(datasize);
    memset((void *)x5, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x5, _cffi_type(0), arg5) < 0)
      return NULL;
  }

  x6 = _cffi_to_c_UNSIGNED(arg6, size_t);
  if (x6 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg7, (char **)&x7);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x7 = alloca(datasize);
    memset((void *)x7, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x7, _cffi_type(0), arg7) < 0)
      return NULL;
  }

  x8 = _cffi_to_c_UNSIGNED(arg8, size_t);
  if (x8 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  x9 = _cffi_to_c_SIGNED(arg9, int);
  if (x9 == (int)-1 && PyErr_Occurred())
    return NULL;

  x10 = _cffi_to_c_UNSIGNED(arg10, uint32_t);
  if (x10 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg11, (char **)&x11);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x11 = alloca(datasize);
    memset((void *)x11, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x11, _cffi_type(1), arg11) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CCCryptorCreateWithMode(x0, x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int32_t);
}

static PyObject *
_cffi_f_CCCryptorFinal(PyObject *self, PyObject *args)
{
  CCCryptorRef x0;
  void * x1;
  size_t x2;
  size_t * x3;
  Py_ssize_t datasize;
  int32_t result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:CCCryptorFinal", &arg0, &arg1, &arg2, &arg3))
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
      _cffi_type(3), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(3), arg1) < 0)
      return NULL;
  }

  x2 = _cffi_to_c_UNSIGNED(arg2, size_t);
  if (x2 == (size_t)-1 && PyErr_Occurred())
    return NULL;

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

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CCCryptorFinal(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int32_t);
}

static PyObject *
_cffi_f_CCCryptorGCMAddAAD(PyObject *self, PyObject *args)
{
  CCCryptorRef x0;
  void const * x1;
  size_t x2;
  Py_ssize_t datasize;
  int32_t result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:CCCryptorGCMAddAAD", &arg0, &arg1, &arg2))
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

  x2 = _cffi_to_c_UNSIGNED(arg2, size_t);
  if (x2 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CCCryptorGCMAddAAD(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int32_t);
}

static PyObject *
_cffi_f_CCCryptorGCMAddIV(PyObject *self, PyObject *args)
{
  CCCryptorRef x0;
  void const * x1;
  size_t x2;
  Py_ssize_t datasize;
  int32_t result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:CCCryptorGCMAddIV", &arg0, &arg1, &arg2))
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

  x2 = _cffi_to_c_UNSIGNED(arg2, size_t);
  if (x2 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CCCryptorGCMAddIV(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int32_t);
}

static PyObject *
_cffi_f_CCCryptorGCMDecrypt(PyObject *self, PyObject *args)
{
  CCCryptorRef x0;
  void const * x1;
  size_t x2;
  void * x3;
  Py_ssize_t datasize;
  int32_t result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:CCCryptorGCMDecrypt", &arg0, &arg1, &arg2, &arg3))
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

  x2 = _cffi_to_c_UNSIGNED(arg2, size_t);
  if (x2 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca(datasize);
    memset((void *)x3, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(3), arg3) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CCCryptorGCMDecrypt(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int32_t);
}

static PyObject *
_cffi_f_CCCryptorGCMEncrypt(PyObject *self, PyObject *args)
{
  CCCryptorRef x0;
  void const * x1;
  size_t x2;
  void * x3;
  Py_ssize_t datasize;
  int32_t result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:CCCryptorGCMEncrypt", &arg0, &arg1, &arg2, &arg3))
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

  x2 = _cffi_to_c_UNSIGNED(arg2, size_t);
  if (x2 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca(datasize);
    memset((void *)x3, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(3), arg3) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CCCryptorGCMEncrypt(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int32_t);
}

static PyObject *
_cffi_f_CCCryptorGCMFinal(PyObject *self, PyObject *args)
{
  CCCryptorRef x0;
  void const * x1;
  size_t * x2;
  Py_ssize_t datasize;
  int32_t result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:CCCryptorGCMFinal", &arg0, &arg1, &arg2))
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
      _cffi_type(4), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(4), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CCCryptorGCMFinal(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int32_t);
}

static PyObject *
_cffi_f_CCCryptorGCMReset(PyObject *self, PyObject *arg0)
{
  CCCryptorRef x0;
  Py_ssize_t datasize;
  int32_t result;

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
  { result = CCCryptorGCMReset(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int32_t);
}

static PyObject *
_cffi_f_CCCryptorRelease(PyObject *self, PyObject *arg0)
{
  CCCryptorRef x0;
  Py_ssize_t datasize;
  int32_t result;

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
  { result = CCCryptorRelease(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int32_t);
}

static PyObject *
_cffi_f_CCCryptorUpdate(PyObject *self, PyObject *args)
{
  CCCryptorRef x0;
  void const * x1;
  size_t x2;
  void * x3;
  size_t x4;
  size_t * x5;
  Py_ssize_t datasize;
  int32_t result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;
  PyObject *arg5;

  if (!PyArg_ParseTuple(args, "OOOOOO:CCCryptorUpdate", &arg0, &arg1, &arg2, &arg3, &arg4, &arg5))
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

  x2 = _cffi_to_c_UNSIGNED(arg2, size_t);
  if (x2 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca(datasize);
    memset((void *)x3, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(3), arg3) < 0)
      return NULL;
  }

  x4 = _cffi_to_c_UNSIGNED(arg4, size_t);
  if (x4 == (size_t)-1 && PyErr_Occurred())
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

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CCCryptorUpdate(x0, x1, x2, x3, x4, x5); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int32_t);
}

static PyObject *
_cffi_f_CCHmacFinal(PyObject *self, PyObject *args)
{
  CCHmacContext * x0;
  void * x1;
  Py_ssize_t datasize;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:CCHmacFinal", &arg0, &arg1))
    return NULL;

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

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { CCHmacFinal(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_CCHmacInit(PyObject *self, PyObject *args)
{
  CCHmacContext * x0;
  uint32_t x1;
  void const * x2;
  size_t x3;
  Py_ssize_t datasize;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:CCHmacInit", &arg0, &arg1, &arg2, &arg3))
    return NULL;

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

  x1 = _cffi_to_c_UNSIGNED(arg1, uint32_t);
  if (x1 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

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

  x3 = _cffi_to_c_UNSIGNED(arg3, size_t);
  if (x3 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { CCHmacInit(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_CCHmacUpdate(PyObject *self, PyObject *args)
{
  CCHmacContext * x0;
  void const * x1;
  size_t x2;
  Py_ssize_t datasize;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:CCHmacUpdate", &arg0, &arg1, &arg2))
    return NULL;

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

  x2 = _cffi_to_c_UNSIGNED(arg2, size_t);
  if (x2 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { CCHmacUpdate(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_CCKeyDerivationPBKDF(PyObject *self, PyObject *args)
{
  uint32_t x0;
  char const * x1;
  size_t x2;
  uint8_t const * x3;
  size_t x4;
  uint32_t x5;
  unsigned int x6;
  uint8_t * x7;
  size_t x8;
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

  if (!PyArg_ParseTuple(args, "OOOOOOOOO:CCKeyDerivationPBKDF", &arg0, &arg1, &arg2, &arg3, &arg4, &arg5, &arg6, &arg7, &arg8))
    return NULL;

  x0 = _cffi_to_c_UNSIGNED(arg0, uint32_t);
  if (x0 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

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

  x2 = _cffi_to_c_UNSIGNED(arg2, size_t);
  if (x2 == (size_t)-1 && PyErr_Occurred())
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

  x4 = _cffi_to_c_UNSIGNED(arg4, size_t);
  if (x4 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  x5 = _cffi_to_c_UNSIGNED(arg5, uint32_t);
  if (x5 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

  x6 = _cffi_to_c_UNSIGNED(arg6, unsigned int);
  if (x6 == (unsigned int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(9), arg7, (char **)&x7);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x7 = alloca(datasize);
    memset((void *)x7, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x7, _cffi_type(9), arg7) < 0)
      return NULL;
  }

  x8 = _cffi_to_c_UNSIGNED(arg8, size_t);
  if (x8 == (size_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CCKeyDerivationPBKDF(x0, x1, x2, x3, x4, x5, x6, x7, x8); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_CC_MD5_Final(PyObject *self, PyObject *args)
{
  unsigned char * x0;
  CC_MD5_CTX * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:CC_MD5_Final", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(10), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(10), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(11), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(11), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CC_MD5_Final(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_CC_MD5_Init(PyObject *self, PyObject *arg0)
{
  CC_MD5_CTX * x0;
  Py_ssize_t datasize;
  int result;

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
  { result = CC_MD5_Init(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_CC_MD5_Update(PyObject *self, PyObject *args)
{
  CC_MD5_CTX * x0;
  void const * x1;
  uint32_t x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:CC_MD5_Update", &arg0, &arg1, &arg2))
    return NULL;

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

  x2 = _cffi_to_c_UNSIGNED(arg2, uint32_t);
  if (x2 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CC_MD5_Update(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_CC_SHA1_Final(PyObject *self, PyObject *args)
{
  unsigned char * x0;
  CC_SHA1_CTX * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:CC_SHA1_Final", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(10), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(10), arg0) < 0)
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
  { result = CC_SHA1_Final(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_CC_SHA1_Init(PyObject *self, PyObject *arg0)
{
  CC_SHA1_CTX * x0;
  Py_ssize_t datasize;
  int result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(12), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(12), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CC_SHA1_Init(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_CC_SHA1_Update(PyObject *self, PyObject *args)
{
  CC_SHA1_CTX * x0;
  void const * x1;
  uint32_t x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:CC_SHA1_Update", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(12), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(12), arg0) < 0)
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

  x2 = _cffi_to_c_UNSIGNED(arg2, uint32_t);
  if (x2 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CC_SHA1_Update(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_CC_SHA224_Final(PyObject *self, PyObject *args)
{
  unsigned char * x0;
  CC_SHA256_CTX * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:CC_SHA224_Final", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(10), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(10), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(13), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(13), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CC_SHA224_Final(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_CC_SHA224_Init(PyObject *self, PyObject *arg0)
{
  CC_SHA256_CTX * x0;
  Py_ssize_t datasize;
  int result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(13), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(13), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CC_SHA224_Init(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_CC_SHA224_Update(PyObject *self, PyObject *args)
{
  CC_SHA256_CTX * x0;
  void const * x1;
  uint32_t x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:CC_SHA224_Update", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(13), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(13), arg0) < 0)
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

  x2 = _cffi_to_c_UNSIGNED(arg2, uint32_t);
  if (x2 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CC_SHA224_Update(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_CC_SHA256_Final(PyObject *self, PyObject *args)
{
  unsigned char * x0;
  CC_SHA256_CTX * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:CC_SHA256_Final", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(10), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(10), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(13), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(13), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CC_SHA256_Final(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_CC_SHA256_Init(PyObject *self, PyObject *arg0)
{
  CC_SHA256_CTX * x0;
  Py_ssize_t datasize;
  int result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(13), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(13), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CC_SHA256_Init(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_CC_SHA256_Update(PyObject *self, PyObject *args)
{
  CC_SHA256_CTX * x0;
  void const * x1;
  uint32_t x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:CC_SHA256_Update", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(13), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(13), arg0) < 0)
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

  x2 = _cffi_to_c_UNSIGNED(arg2, uint32_t);
  if (x2 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CC_SHA256_Update(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_CC_SHA384_Final(PyObject *self, PyObject *args)
{
  unsigned char * x0;
  CC_SHA512_CTX * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:CC_SHA384_Final", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(10), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(10), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(14), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(14), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CC_SHA384_Final(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_CC_SHA384_Init(PyObject *self, PyObject *arg0)
{
  CC_SHA512_CTX * x0;
  Py_ssize_t datasize;
  int result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(14), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(14), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CC_SHA384_Init(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_CC_SHA384_Update(PyObject *self, PyObject *args)
{
  CC_SHA512_CTX * x0;
  void const * x1;
  uint32_t x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:CC_SHA384_Update", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(14), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(14), arg0) < 0)
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

  x2 = _cffi_to_c_UNSIGNED(arg2, uint32_t);
  if (x2 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CC_SHA384_Update(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_CC_SHA512_Final(PyObject *self, PyObject *args)
{
  unsigned char * x0;
  CC_SHA512_CTX * x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:CC_SHA512_Final", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(10), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(10), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(14), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(14), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CC_SHA512_Final(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_CC_SHA512_Init(PyObject *self, PyObject *arg0)
{
  CC_SHA512_CTX * x0;
  Py_ssize_t datasize;
  int result;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(14), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(14), arg0) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CC_SHA512_Init(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_CC_SHA512_Update(PyObject *self, PyObject *args)
{
  CC_SHA512_CTX * x0;
  void const * x1;
  uint32_t x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:CC_SHA512_Update", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(14), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(14), arg0) < 0)
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

  x2 = _cffi_to_c_UNSIGNED(arg2, uint32_t);
  if (x2 == (uint32_t)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = CC_SHA512_Update(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static void _cffi_check_struct_CC_MD5state_st(struct CC_MD5state_st *p)
{
  /* only to generate compile-time warnings or errors */
}
static PyObject *
_cffi_layout_struct_CC_MD5state_st(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct CC_MD5state_st y; };
  static Py_ssize_t nums[] = {
    sizeof(struct CC_MD5state_st),
    offsetof(struct _cffi_aligncheck, y),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_CC_MD5state_st(0);
}

static void _cffi_check_struct_CC_SHA1state_st(struct CC_SHA1state_st *p)
{
  /* only to generate compile-time warnings or errors */
}
static PyObject *
_cffi_layout_struct_CC_SHA1state_st(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct CC_SHA1state_st y; };
  static Py_ssize_t nums[] = {
    sizeof(struct CC_SHA1state_st),
    offsetof(struct _cffi_aligncheck, y),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_CC_SHA1state_st(0);
}

static void _cffi_check_struct_CC_SHA256state_st(struct CC_SHA256state_st *p)
{
  /* only to generate compile-time warnings or errors */
}
static PyObject *
_cffi_layout_struct_CC_SHA256state_st(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct CC_SHA256state_st y; };
  static Py_ssize_t nums[] = {
    sizeof(struct CC_SHA256state_st),
    offsetof(struct _cffi_aligncheck, y),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_CC_SHA256state_st(0);
}

static void _cffi_check_struct_CC_SHA512state_st(struct CC_SHA512state_st *p)
{
  /* only to generate compile-time warnings or errors */
}
static PyObject *
_cffi_layout_struct_CC_SHA512state_st(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct CC_SHA512state_st y; };
  static Py_ssize_t nums[] = {
    sizeof(struct CC_SHA512state_st),
    offsetof(struct _cffi_aligncheck, y),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_CC_SHA512state_st(0);
}

static int _cffi_setup_custom(PyObject *lib)
{
  return _cffi_e__$enum_$9(lib);
}

static PyMethodDef _cffi_methods[] = {
  {"_cffi_layout__CCHmacContext", _cffi_layout__CCHmacContext, METH_NOARGS},
  {"CCCalibratePBKDF", _cffi_f_CCCalibratePBKDF, METH_VARARGS},
  {"CCCryptorCreate", _cffi_f_CCCryptorCreate, METH_VARARGS},
  {"CCCryptorCreateWithMode", _cffi_f_CCCryptorCreateWithMode, METH_VARARGS},
  {"CCCryptorFinal", _cffi_f_CCCryptorFinal, METH_VARARGS},
  {"CCCryptorGCMAddAAD", _cffi_f_CCCryptorGCMAddAAD, METH_VARARGS},
  {"CCCryptorGCMAddIV", _cffi_f_CCCryptorGCMAddIV, METH_VARARGS},
  {"CCCryptorGCMDecrypt", _cffi_f_CCCryptorGCMDecrypt, METH_VARARGS},
  {"CCCryptorGCMEncrypt", _cffi_f_CCCryptorGCMEncrypt, METH_VARARGS},
  {"CCCryptorGCMFinal", _cffi_f_CCCryptorGCMFinal, METH_VARARGS},
  {"CCCryptorGCMReset", _cffi_f_CCCryptorGCMReset, METH_O},
  {"CCCryptorRelease", _cffi_f_CCCryptorRelease, METH_O},
  {"CCCryptorUpdate", _cffi_f_CCCryptorUpdate, METH_VARARGS},
  {"CCHmacFinal", _cffi_f_CCHmacFinal, METH_VARARGS},
  {"CCHmacInit", _cffi_f_CCHmacInit, METH_VARARGS},
  {"CCHmacUpdate", _cffi_f_CCHmacUpdate, METH_VARARGS},
  {"CCKeyDerivationPBKDF", _cffi_f_CCKeyDerivationPBKDF, METH_VARARGS},
  {"CC_MD5_Final", _cffi_f_CC_MD5_Final, METH_VARARGS},
  {"CC_MD5_Init", _cffi_f_CC_MD5_Init, METH_O},
  {"CC_MD5_Update", _cffi_f_CC_MD5_Update, METH_VARARGS},
  {"CC_SHA1_Final", _cffi_f_CC_SHA1_Final, METH_VARARGS},
  {"CC_SHA1_Init", _cffi_f_CC_SHA1_Init, METH_O},
  {"CC_SHA1_Update", _cffi_f_CC_SHA1_Update, METH_VARARGS},
  {"CC_SHA224_Final", _cffi_f_CC_SHA224_Final, METH_VARARGS},
  {"CC_SHA224_Init", _cffi_f_CC_SHA224_Init, METH_O},
  {"CC_SHA224_Update", _cffi_f_CC_SHA224_Update, METH_VARARGS},
  {"CC_SHA256_Final", _cffi_f_CC_SHA256_Final, METH_VARARGS},
  {"CC_SHA256_Init", _cffi_f_CC_SHA256_Init, METH_O},
  {"CC_SHA256_Update", _cffi_f_CC_SHA256_Update, METH_VARARGS},
  {"CC_SHA384_Final", _cffi_f_CC_SHA384_Final, METH_VARARGS},
  {"CC_SHA384_Init", _cffi_f_CC_SHA384_Init, METH_O},
  {"CC_SHA384_Update", _cffi_f_CC_SHA384_Update, METH_VARARGS},
  {"CC_SHA512_Final", _cffi_f_CC_SHA512_Final, METH_VARARGS},
  {"CC_SHA512_Init", _cffi_f_CC_SHA512_Init, METH_O},
  {"CC_SHA512_Update", _cffi_f_CC_SHA512_Update, METH_VARARGS},
  {"_cffi_layout_struct_CC_MD5state_st", _cffi_layout_struct_CC_MD5state_st, METH_NOARGS},
  {"_cffi_layout_struct_CC_SHA1state_st", _cffi_layout_struct_CC_SHA1state_st, METH_NOARGS},
  {"_cffi_layout_struct_CC_SHA256state_st", _cffi_layout_struct_CC_SHA256state_st, METH_NOARGS},
  {"_cffi_layout_struct_CC_SHA512state_st", _cffi_layout_struct_CC_SHA512state_st, METH_NOARGS},
  {"_cffi_setup", _cffi_setup, METH_VARARGS},
  {NULL, NULL}    /* Sentinel */
};

PyMODINIT_FUNC
init_Cryptography_cffi_be05eb56x6daa9a79(void)
{
  PyObject *lib;
  lib = Py_InitModule("_Cryptography_cffi_be05eb56x6daa9a79", _cffi_methods);
  if (lib == NULL || 0 < 0)
    return;
  _cffi_init();
  return;
}
