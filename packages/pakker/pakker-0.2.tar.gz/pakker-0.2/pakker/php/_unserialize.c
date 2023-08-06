#define PY_SSIZE_T_CLEAN
#include "Python.h"

/**
 * Unserializes data that was serialized with PHP's `serialize()` function.
 *
 * Limitations:
 *
 *  - Only supports UTF-8 as encodings for strings for now (not a
 *    technical restriction, but I don't need anything else).
 *  - Always uses the 'ignore' error-handler for decoding
 *
 * Copyright (c) 2012 Andreas Stührk <andy-python@hammerhartes.de>
 */


PyObject *unserialize(char *, Py_ssize_t, Py_ssize_t *, int);


#define CHECK_EOF REQUIRE(0)

#define REQUIRE(n) \
    if (*offset + n >= length) { \
        PyErr_SetString(PyExc_ValueError, "unexpected end of string"); \
        goto error; \
    } \

#define EXPECT(c) { \
    char __v; \
    CHECK_EOF; \
    __v = data[(*offset)++];                    \
    if (__v != c) { \
        PyErr_Format(PyExc_ValueError, "expected '%c', got '%c'", c, __v);  \
        goto error; \
    } \
    }

#define READ_INT(target, delim) { \
    PyObject *__long_data, *__long_object; \
    UNTIL(__long_data, delim); \
    __long_object = PyLong_FromString( \
        PyBytes_AS_STRING(__long_data), NULL, 10); \
    Py_DECREF(__long_data); \
    if (__long_object == NULL) { \
        goto error; \
    } \
    target = PyLong_AsSsize_t(__long_object); \
    Py_DECREF(__long_object); \
    if (target == -1 && PyErr_Occurred()) { \
        goto error; \
    }\
    }
    

/**
 * Returns a substring up to (and not included) `delim`. Returns a
 * PyBytesObject.
 */
#define UNTIL(target, delim) { \
    char *__ptr; \
    char *__start = data + *offset; \
    for (__ptr = __start; __ptr <= (data + length) && *__ptr != delim; ++__ptr)\
        ; \
    if (*__ptr == delim) { \
        target = PyBytes_FromStringAndSize(__start, __ptr - __start); \
        if (target == NULL) { \
            goto error; \
        } \
        *offset += __ptr - __start + 1; \
    } else { \
        PyErr_SetString(PyExc_ValueError, "unexpected end of string"); \
        goto error; \
    } \
}

PyObject *
unserialize_number(char *data, Py_ssize_t length, Py_ssize_t *offset, char type) {
    PyObject *number_data = NULL, *retval = NULL;
    EXPECT(':');
    UNTIL(number_data, ';');
    if (type == 'i') {
        retval = PyLong_FromString(
            PyBytes_AS_STRING(number_data), NULL, 10);
    } else if (type == 'd') {
#if PY_MAJOR_VERSION >= 3
        retval = PyFloat_FromString(number_data);
#else
        retval = PyFloat_FromString(number_data, NULL);
#endif
    } else {
        PyObject *number = PyLong_FromString(
            PyBytes_AS_STRING(number_data), NULL, 10);
        if (number != NULL) {
            int value = PyObject_IsTrue(number);
            if (value != -1) {
                retval = PyBool_FromLong(value);
            }
        }
        Py_XDECREF(number);
    }
    Py_DECREF(number_data);
    return retval;

  error:
    return NULL;
}

PyObject *
unserialize_string(char *data, Py_ssize_t length, Py_ssize_t *offset, int decode) {
    Py_ssize_t string_length;
    PyObject *retval = NULL;
    EXPECT(':');
    READ_INT(string_length, ':');
    if (string_length < 0) {
        PyErr_SetString(PyExc_ValueError, "negative string size");
        goto error;
    }
    EXPECT('"');
    REQUIRE(string_length);
    retval = PyBytes_FromStringAndSize(data + *offset, string_length);
    if (retval != NULL && decode) {
        PyObject *encoded = retval;
        retval = PyUnicode_DecodeUTF8(
            PyBytes_AS_STRING(encoded), PyBytes_GET_SIZE(encoded),
            "ignore");
        Py_DECREF(encoded);
    }
    *offset += string_length;
    if (retval != NULL) {
        EXPECT('"');
        EXPECT(';');
    }
    return retval;

  error:
    Py_XDECREF(retval);
    return NULL;
}

PyObject *
unserialize_array(char *data, Py_ssize_t length, Py_ssize_t *offset, int decode)
{
    PyObject *result = NULL;
    PyObject *last_item = Py_Ellipsis, *item = NULL;
    Py_ssize_t i, items;
    EXPECT(':');
    READ_INT(items, ':');
    if (items < 0) {
        PyErr_SetString(PyExc_ValueError, "negative array size");
        goto error;
    } else if (items >= PY_SSIZE_T_MAX / 2) {
        PyErr_SetString(PyExc_OverflowError, "array size too large");
        goto error;
    }
    EXPECT('{');
    items *= 2;
    result = PyDict_New();
    if (result == NULL) {
        goto error;
    }
    for (i = 0; i < items; ++i) {
        if (Py_EnterRecursiveCall(" while decoding an array")) {
            goto error;
        }
        item = unserialize(data, length, offset, decode);
        Py_LeaveRecursiveCall();
        if (item == NULL) {
            goto error;
        } else if (last_item == Py_Ellipsis) {
            last_item = item;
        } else {
            if (PyDict_SetItem(result, last_item, item) == -1) {
                goto error;
            }
            Py_CLEAR(item);
            Py_CLEAR(last_item);
            last_item = Py_Ellipsis;
        }
    }
    EXPECT('}');
    return result;
    
  error:
    if (last_item != Py_Ellipsis) {
        Py_XDECREF(last_item);
    }
    Py_XDECREF(item);
    Py_XDECREF(result);
    return NULL;
}

PyObject *
unserialize(char *data, Py_ssize_t length, Py_ssize_t *offset, int decode) {
    CHECK_EOF;
    char type = tolower(data[(*offset)++]);
    if (type == 'n') {
        EXPECT(';');
        Py_RETURN_NONE;
    } else if (type == 'i' || type == 'd' || type == 'b') {
        return unserialize_number(data, length, offset, type);
    } else if (type == 's') {
        return unserialize_string(data, length, offset, decode);
    } else if (type == 'a') {
        return unserialize_array(data, length, offset, decode);
    }
    PyErr_Format(PyExc_ValueError, "unknown opcode: '%c'", type);
  error:
    return NULL;
}

static PyObject *
loads(PyObject *self, PyObject *args, PyObject *kwargs) {
    char *data;
    Py_ssize_t length;
    int decode_strings = 0;
    PyObject *decode_strings_object = Py_False;
    long offset = 0;
    static char *kwlist[] = {"data", "decode_strings", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s#|O", kwlist,
                                     &data, &length, &decode_strings_object)) {
        return NULL;
    }
    decode_strings = PyObject_IsTrue(decode_strings_object);
    if (decode_strings == -1) {
        return NULL;
    }
    return unserialize(data, length, &offset, decode_strings);
}

static PyMethodDef phpunserialize_methods[] = {
    {"loads", (PyCFunction)loads, METH_VARARGS | METH_KEYWORDS, NULL},
    {NULL, NULL}
};

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "pakker.php._unserialize",
    NULL,
    0,
    phpunserialize_methods,
    NULL,
    NULL,
    NULL,
    NULL
};

#define INITERROR return NULL

PyObject *
PyInit__unserialize(void)

#else
#define INITERROR return

void
init_unserialize(void)
#endif
{
#if PY_MAJOR_VERSION >= 3
    PyObject *module = PyModule_Create(&moduledef);
#else
    PyObject *module = Py_InitModule(
        "pakker.php._unserialize", phpunserialize_methods);
#endif

    if (module == NULL)
        INITERROR;

#if PY_MAJOR_VERSION >= 3
    return module;
#endif
}
