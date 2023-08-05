#include <Python.h>
#include <structmember.h>

#include "polynomials.h"

/* Compatibility - taken from cPython 3.3 */
#ifndef Py_RETURN_NOTIMPLEMENTED
#define Py_RETURN_NOTIMPLEMENTED \
    return Py_INCREF(Py_NotImplemented), Py_NotImplemented
#endif

/* A Python Polynomial Object */
typedef struct {
    PyObject_HEAD
    Polynomial poly;
} PyPoly_PolynomialObject;

static PyTypeObject PyPoly_PolynomialType;  // Forward declaration

/* Classic macro to check if a PyObject is a Polynomial */
#define PyPolynomial_Check(op) PyObject_TypeCheck((op), &PyPoly_PolynomialType)

/* Create a new Python Polynomial object.
 * If a pointer to a Polynomial is given as parameter, the pointed Polynomial
 * will be copied into the PyObject and the "deg" parameter will be ignored.
 * /!\ This will transfer ownership of the coefficients pointer /!\
 *
 * If not, a new Polynomial of degree "deg" will be allocated, initialized to 0.
 */
static PyPoly_PolynomialObject*
new_poly_st(PyTypeObject *subtype, int deg, Polynomial *P)
{
    PyPoly_PolynomialObject *self;
    self = (PyPoly_PolynomialObject *) (subtype->tp_alloc(subtype, 0));
    if (self != NULL) {
        if (P == NULL) {
            if(!poly_init(&(self->poly), deg)) {
                Py_DECREF(self);
                return (PyPoly_PolynomialObject*)PyErr_NoMemory();
            }
        } else {
            self->poly = *P;
        }
    }
    return self;
}
#define NewPoly(deg, P)     new_poly_st(&PyPoly_PolynomialType, (int)(deg), (Polynomial*)(P))
#define ReturnPyPolyOrFree(P)                       \
PyObject *p;                                        \
if ((p = (PyObject*)NewPoly(0, &P)) == NULL) {      \
    poly_free(&P);                                  \
    return PyErr_NoMemory();                        \
}                                                   \
return p;

/* Polynomial extraction helpers.
 * Those functions deal with the problem of getting a Polynomial object out
 * of an arbitrary PyObject.
 *
 * The macro ExtractOrBorrowPoly(obj, P, status) will try to borrow a Polynomial
 * from "obj", if "obj" is a Python Polynomial.
 * Otherwise, it will try and create a new Polynomial, if possible
 * (a Python number will give a constant Polynomial).
 * The "extracted" Polynomial will be stored in destination pointed by "P"
 * and the status flag will be set accordingly.
 */
typedef enum {
   EXTRACT_CREATED,      // Polynomial created
   EXTRACT_BORROWED,     // Polynomial "borrowed" from object
   EXTRACT_ERR,          // Generic error handled by cPython (overflow, etc.)
   EXTRACT_ERRTYPE,      // Unsupported type
   EXTRACT_ERRMEM        // Malloc failure
} ExtractionStatus;

#define PolyExtractionFailure(status) ((ExtractionStatus)(status) >= EXTRACT_ERR)

static ExtractionStatus
extract_complex(PyObject *obj, Py_complex *dest)
{
    Py_complex c;
    if (PyComplex_Check(obj)) {
        c = PyComplex_AsCComplex(obj);
        if (c.real == -1.0 && PyErr_Occurred()) {
            return EXTRACT_ERR;
        }
    } else if (PyFloat_Check(obj)) {
        c = CZero;
        c.real = PyFloat_AsDouble(obj);
        if (c.real == -1.0 && PyErr_Occurred()) {
            return EXTRACT_ERR;
        }
    } else if (PyLong_Check(obj)) {
        c = CZero;
        c.real = PyLong_AsDouble(obj);
        if (c.real == -1.0 && PyErr_Occurred()) {
            return EXTRACT_ERR;
        }
    } else {
        return EXTRACT_ERRTYPE;
    }
    *dest = c;
    return EXTRACT_CREATED;
}

static inline ExtractionStatus
extract_poly(PyObject *obj, Polynomial *P)
{
    Py_complex c;
    int errmem = 0;
    ExtractionStatus status;
    status = extract_complex(obj, &c);
    if (status == EXTRACT_CREATED) {
        Poly_InitConst(P, c, errmem)
        if (errmem) status = EXTRACT_ERRMEM;
    }
    return status;
}

#define ExtractOrBorrowPoly(obj, P, status)             \
    if (PyPolynomial_Check(obj)) {                      \
        P = ((PyPoly_PolynomialObject*)obj)->poly;      \
        status = EXTRACT_BORROWED;                      \
    } else {                                            \
        status = extract_poly(obj, &P);                 \
    }

/**
 * PyObject API implementation
 */

static PyObject*
PyPoly_new(PyTypeObject *subtype, PyObject *args, PyObject *kwds)
{
    PyPoly_PolynomialObject *self;
    int size = PyTuple_GET_SIZE(args);
    self = new_poly_st(subtype, size - 1, NULL);
    if (self != NULL) {
        Py_complex c;
        int i;
        for (i = 0; i < size; ++i) {
            c = PyComplex_AsCComplex(PyTuple_GET_ITEM(args, i));
            if (c.real == -1.0 && PyErr_Occurred()) {
                Py_DECREF(self);
                return NULL;
            }
            poly_set_coef(&(self->poly), i, c);
        }
    }
    return (PyObject*)self;
}

static void
PyPoly_dealloc(PyPoly_PolynomialObject *self)
{
    poly_free(&(self->poly));
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject*
PyPoly_copy(PyPoly_PolynomialObject *self)
{
    Polynomial P;
    if (!poly_copy(&(self->poly), &P)) {
        return PyErr_NoMemory();
    }
    ReturnPyPolyOrFree(P)
}

static PyObject*
PyPoly_repr(PyPoly_PolynomialObject *self)
{
    char* str = poly_to_string(&(self->poly));
    PyObject* ret;
#if PY_VERSION_HEX >= 0x03030000
    ret = PyUnicode_FromKindAndData(PyUnicode_1BYTE_KIND, str, strlen(str));
#else
    ret = PyUnicode_FromStringAndSize(str, strlen(str));
#endif
    free(str);
    return ret;
}

/* Macro for converting the arguments of a function into
 * into two Polynomial objects, in order to perform some operation
 * Assumes: PyObject *self, *other are the arguments
 * Constructs: Polynomial A, B; ExtractionStatus A_status, B_status
 */
#define PYPOLY_BINARYFUNC_HEADER                            \
    int A_status, B_status;                                 \
    Polynomial A, B;                                        \
    ExtractOrBorrowPoly(self, A, A_status)                  \
    ExtractOrBorrowPoly(other, B, B_status)                 \
    if (PolyExtractionFailure(A_status)                     \
        ||                                                  \
        PolyExtractionFailure(B_status)) {                  \
        if (A_status == EXTRACT_CREATED) poly_free(&A);     \
        if (B_status == EXTRACT_CREATED) poly_free(&B);     \
        if (A_status == EXTRACT_ERRTYPE                     \
            ||                                              \
            B_status == EXTRACT_ERRTYPE) {                  \
            Py_RETURN_NOTIMPLEMENTED;                       \
        } else {                                            \
            return PyErr_NoMemory();                        \
        }                                                   \
    }
#define PYPOLY_BINARYFUNC_FOOTER                            \
    if (A_status == EXTRACT_CREATED) poly_free(&A);         \
    if (B_status == EXTRACT_CREATED) poly_free(&B);

static PyObject*
PyPoly_add(PyObject *self, PyObject *other)
{
    PYPOLY_BINARYFUNC_HEADER
    Polynomial R;
    if (!poly_add(&A, &B, &R)) {
        if (A_status == EXTRACT_CREATED) poly_free(&A);
        if (B_status == EXTRACT_CREATED) poly_free(&B);
        return PyErr_NoMemory();
    }
    PYPOLY_BINARYFUNC_FOOTER
    ReturnPyPolyOrFree(R)
}

static PyObject*
PyPoly_sub(PyObject *self, PyObject *other)
{
    PYPOLY_BINARYFUNC_HEADER
    Polynomial R;
    if (!poly_sub(&A, &B, &R)) {
        if (A_status == EXTRACT_CREATED) poly_free(&A);
        if (B_status == EXTRACT_CREATED) poly_free(&B);
        return PyErr_NoMemory();
    }
    PYPOLY_BINARYFUNC_FOOTER
    ReturnPyPolyOrFree(R)
}

static PyObject*
PyPoly_mult(PyObject *self, PyObject *other)
{
    PYPOLY_BINARYFUNC_HEADER
    Polynomial R;
    if (!poly_multiply(&A, &B, &R)) {
        if (A_status == EXTRACT_CREATED) poly_free(&A);
        if (B_status == EXTRACT_CREATED) poly_free(&B);
        return PyErr_NoMemory();
    }
    PYPOLY_BINARYFUNC_FOOTER
    ReturnPyPolyOrFree(R)
}

static PyObject*
PyPoly_div(PyObject *self, PyObject *other)
{
    if(!PyPolynomial_Check(self)) {
        Py_RETURN_NOTIMPLEMENTED;
    }
    Py_complex c;
    ExtractionStatus c_status = extract_complex(other, &c);
    switch (c_status) {
        case EXTRACT_CREATED:
            break;
        case EXTRACT_ERR:
            return PyErr_NoMemory();
        case EXTRACT_ERRTYPE:
            Py_RETURN_NOTIMPLEMENTED;
        case EXTRACT_ERRMEM:
            return PyErr_NoMemory();
        default:
            Py_RETURN_NOTIMPLEMENTED;
    }
    if (c.real == 0. && c.imag == 0.) {
        PyErr_SetString(PyExc_ZeroDivisionError,
                        "Cannot divide Polynomial by zero");
        return NULL;
    }
    c = _Py_c_quot(COne, c);
    Polynomial P;
    if(!poly_scal_multiply(&(((PyPoly_PolynomialObject*)self)->poly), c, &P)) {
        return PyErr_NoMemory();
    }
    ReturnPyPolyOrFree(P)
}

static PyObject*
PyPoly_neg(PyPoly_PolynomialObject *self)
{
    Polynomial P;
    if (!poly_neg(&(self->poly), &P)) {
        return PyErr_NoMemory();
    }
    ReturnPyPolyOrFree(P)
}

static PyObject*
PyPoly_call(PyPoly_PolynomialObject *self, PyObject *args, PyObject *kw)
{
    Py_complex x;

    if (!_PyArg_NoKeywords("__call__()", kw) || !PyArg_ParseTuple(args, "D", &x)) {
        return NULL;
    }
    Py_complex y = poly_eval(&(self->poly), x);
    if (y.imag == 0) {
        return PyFloat_FromDouble(y.real);
    }
    return PyComplex_FromCComplex(y);
}

static PyObject*
PyPoly_pow(PyPoly_PolynomialObject *self, PyObject *pyexp, PyObject *pymod)
{
    unsigned long exponent = PyLong_AsUnsignedLong(pyexp);
    if (exponent == -1 && PyErr_Occurred()) {
        Py_RETURN_NOTIMPLEMENTED;
    }
    Polynomial P;
    if (!poly_pow(&(self->poly), exponent, &P)) {
        return PyErr_NoMemory();
    }
    ReturnPyPolyOrFree(P)
}

static PyObject*
PyPoly_derive(PyPoly_PolynomialObject *self, PyObject *other)
{
    unsigned long steps = PyLong_AsUnsignedLong(other);
    if (steps == -1 && PyErr_Occurred()) {
        Py_RETURN_NOTIMPLEMENTED;
    }
    Polynomial P;
    if (!poly_derive(&(self->poly), steps, &P)) {
        return PyErr_NoMemory();
    }
    ReturnPyPolyOrFree(P)
}

static PyObject*
PyPoly_integrate(PyPoly_PolynomialObject *self, PyObject *other)
{
    unsigned long steps = PyLong_AsUnsignedLong(other);
    if (steps == -1 && PyErr_Occurred()) {
        Py_RETURN_NOTIMPLEMENTED;
    }
    Polynomial P;
    if (!poly_integrate(&(self->poly), steps, &P)) {
        return PyErr_NoMemory();
    }
    ReturnPyPolyOrFree(P)
}

static PyObject*
PyPoly_remain(PyObject *self, PyObject *other)
{
    PYPOLY_BINARYFUNC_HEADER
    Polynomial R;
    int res = poly_div(&A, &B, NULL, &R);
    if (res != 1) {
        if (A_status == EXTRACT_CREATED) poly_free(&A);
        if (B_status == EXTRACT_CREATED) poly_free(&B);
        if (res == -1) {
            PyErr_SetString(PyExc_ZeroDivisionError,
                            "Polynomial Euclidean division by"
                            " zero is undefined");
            return NULL;
        }
        return PyErr_NoMemory();
    }
    PYPOLY_BINARYFUNC_FOOTER
    ReturnPyPolyOrFree(R)
}

static PyObject*
PyPoly_divmod(PyObject *self, PyObject *other)
{
    PYPOLY_BINARYFUNC_HEADER
    Polynomial Q, R;
    int res = poly_div(&A, &B, &Q, &R);
    if (res != 1) {
        if (A_status == EXTRACT_CREATED) poly_free(&A);
        if (B_status == EXTRACT_CREATED) poly_free(&B);
        if (res == -1) {
            PyErr_SetString(PyExc_ZeroDivisionError,
                            "Polynomial Euclidean division by"
                            " zero is undefined");
            return NULL;
        }
        return PyErr_NoMemory();
    }
    PYPOLY_BINARYFUNC_FOOTER
    PyObject *p1, *p2, *t;
    if ((p1 = (PyObject*)NewPoly(0, &Q)) == NULL) {
        poly_free(&Q);
        return NULL;
    }
    if ((p2 = (PyObject*)NewPoly(0, &R)) == NULL) {
        poly_free(&R);
        Py_DECREF(p1);
        return NULL;
    }
    if ((t = PyTuple_Pack(2, p1, p2)) == NULL) {
        Py_DECREF(p1);
        Py_DECREF(p2);
        return NULL;
    }
    return t;
}

static PyObject*
PyPoly_floordiv(PyObject *self, PyObject *other)
{   /* Same as PyPoly_divmod, we just discard R */
    PYPOLY_BINARYFUNC_HEADER
    Polynomial Q, R;
    int res = poly_div(&A, &B, &Q, &R);
    if (res != 1) {
        if (A_status == EXTRACT_CREATED) poly_free(&A);
        if (B_status == EXTRACT_CREATED) poly_free(&B);
        if (res == -1) {
            PyErr_SetString(PyExc_ZeroDivisionError,
                            "Polynomial Euclidean division by"
                            " zero is undefined");
            return NULL;
        }
        return PyErr_NoMemory();
    }
    poly_free(&R);
    PYPOLY_BINARYFUNC_FOOTER
    ReturnPyPolyOrFree(Q)
}

static PyObject*
PyPoly_compare(PyObject *self, PyObject *other, int opid)
{
    if (opid != Py_EQ && opid != Py_NE) {
        Py_RETURN_NOTIMPLEMENTED;
    }
    PYPOLY_BINARYFUNC_HEADER
    int ret = (poly_equal(&A, &B) && opid == Py_EQ)
                    ||
              (!poly_equal(&A, &B) && opid == Py_NE);
    PYPOLY_BINARYFUNC_FOOTER
    if (ret) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

static PyObject*
PyPoly_getitem(PyPoly_PolynomialObject *self, Py_ssize_t i)
{
    Py_complex coef = Poly_GetCoef(&(self->poly), i);
    if (coef.imag == 0) {
        return PyFloat_FromDouble(coef.real);
    }
    return PyComplex_FromCComplex(coef);
}

/* Module methods */

static PyObject*
PyPoly_gcd(PyObject *self, PyObject *args)
{
    int i = PyTuple_GET_SIZE(args);
    if (i < 2) {
        PyErr_SetString(PyExc_TypeError,
                        "'gcd' takes two or more polynomials as arguments");
        return NULL;
    }

    PyObject* item;
    Polynomial P, T;
    poly_init(&P, -1);
    poly_init(&T, -1);
    while (--i >= 0) {
        item = PyTuple_GET_ITEM(args, i);
        if(!PyPolynomial_Check(item)) {
            poly_free(&P);
            Py_RETURN_NOTIMPLEMENTED;
        }
        if (!poly_gcd(&P, &(((PyPoly_PolynomialObject*)item)->poly), &T)) goto memerror;
        poly_free(&P);
        if (!poly_copy(&T, &P)) goto memerror;
        poly_free(&T);
    }
    ReturnPyPolyOrFree(P)
memerror:
    poly_free(&P);
    poly_free(&T);
    return PyErr_NoMemory();
}

static PyMemberDef
PyPoly_members[] = {
    {"degree", T_INT, offsetof(PyPoly_PolynomialObject, poly) + offsetof(Polynomial, deg),
     READONLY, "The degree of the Polynomial instance."},
    { NULL }
};

static PyNumberMethods PyPoly_NumberMethods = {
    (binaryfunc)PyPoly_add,         /* nb_add */
    (binaryfunc)PyPoly_sub,         /* nb_subtract */
    (binaryfunc)PyPoly_mult,        /* nb_multiply */
    (binaryfunc)PyPoly_remain,      /* nb_remainder */
    (binaryfunc)PyPoly_divmod,      /* nb_divmod */
    (ternaryfunc)PyPoly_pow,        /* nb_power */
    (unaryfunc)PyPoly_neg,          /* nb_negative */
    (unaryfunc)PyPoly_copy,         /* nb_positive */
    0,                              /* nb_absolute */
    0,                              /* nb_bool; */
    0,                              /* nb_invert; */
    (binaryfunc)PyPoly_integrate,   /* nb_lshift; */
    (binaryfunc)PyPoly_derive,      /* nb_rshift; */
    0,                              /* nb_and; */
    0,                              /* nb_xor; */
    0,                              /* nb_or; */
    0,                              /* nb_int; */
    0,                              /* nb_reserved; */
    0,                              /* nb_float; */
    0,                              /* nb_inplace_add; */
    0,                              /* nb_inplace_subtract; */
    0,                              /* nb_inplace_multiply; */
    0,                              /* nb_inplace_remainder; */
    0,                              /* nb_inplace_power; */
    0,                              /* nb_inplace_lshift; */
    0,                              /* nb_inplace_rshift; */
    0,                              /* nb_inplace_and; */
    0,                              /* nb_inplace_xor; */
    0,                              /* nb_inplace_or; */
    (binaryfunc)PyPoly_floordiv,    /* nb_floor_divide; */
    (binaryfunc)PyPoly_div,         /* nb_true_divide; */
    0,                              /* nb_inplace_floor_divide; */
    0,                              /* nb_inplace_true_divide; */
    0                               /* nb_index; */
};

static PySequenceMethods PyPoly_as_sequence = {
    0,  /* sq_length */
    0,  /* sq_concat */
    0,  /* sq_repeat */
    (ssizeargfunc)PyPoly_getitem,
    0,
    0,  /* sq_ass_item */
    0,
};

static PyTypeObject PyPoly_PolynomialType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "Polynomial",                       /* tp_name */
    sizeof(PyPoly_PolynomialObject),    /* tp_basicsize */
    0,                                  /* tp_itemsize */
    (destructor)PyPoly_dealloc,         /* tp_dealloc */
    0,                                  /* tp_print */
    0,                                  /* tp_getattr */
    0,                                  /* tp_setattr */
    0,                                  /* tp_reserved */
    (reprfunc)PyPoly_repr,              /* tp_repr */
    &PyPoly_NumberMethods,              /* tp_as_number */
    &PyPoly_as_sequence,                /* tp_as_sequence */
    0,                                  /* tp_as_mapping */
    0,                                  /* tp_hash  */
    (ternaryfunc)PyPoly_call,           /* tp_call */
    0,                                  /* tp_str */
    0,                                  /* tp_getattro */
    0,                                  /* tp_setattro */
    0,                                  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                 /* tp_flags */
    "Polynomial objects",               /* tp_doc */
    0,                                  /* tp_traverse */
    0,                                  /* tp_clear */
    (richcmpfunc)PyPoly_compare,        /* tp_richcompare */
    0,                                  /* tp_weaklistoffset */
    0,                                  /* tp_iter */
    0,                                  /* tp_iternext */
    NULL,                               /* tp_methods */
    PyPoly_members,                     /* tp_members */
    0,                                  /* tp_getset */
    0,                                  /* tp_base */
    0,                                  /* tp_dict */
    0,                                  /* tp_descr_get */
    0,                                  /* tp_descr_set */
    0,                                  /* tp_dictoffset */
    0,                                  /* tp_init */
    0,                                  /* tp_alloc */
    (newfunc)PyPoly_new,                /* tp_new */
};

static PyMethodDef PyPolymethods[] = {
    {"gcd", PyPoly_gcd, METH_VARARGS,
     "Compute the GCD of two or more polynomials."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static PyModuleDef PyPolymodule = {
    PyModuleDef_HEAD_INIT,
    "pypoly",
    "Python Polynomial module implemented in C.",
    -1,
    PyPolymethods,
    NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit_pypoly(void) 
{
    PyObject* m;

    if (PyType_Ready(&PyPoly_PolynomialType) < 0)
        return NULL;

    m = PyModule_Create(&PyPolymodule);
    if (m == NULL)
        return NULL;

    /* Add "Polynomial" type to module */
    Py_INCREF(&PyPoly_PolynomialType);
    PyModule_AddObject(m, "Polynomial", (PyObject *)&PyPoly_PolynomialType);

    /* Add "X" Polynomial to module */
    Polynomial X;
    if (!poly_initX(&X)) {
        return PyErr_NoMemory();
    }
    PyPoly_PolynomialObject *PyPoly_X;
    if ((PyPoly_X = NewPoly(0, &X)) == NULL) {
        poly_free(&X);
        return NULL;
    }
    Py_INCREF(PyPoly_X);
    PyModule_AddObject(m, "X", (PyObject *)PyPoly_X);

    return m;
}
