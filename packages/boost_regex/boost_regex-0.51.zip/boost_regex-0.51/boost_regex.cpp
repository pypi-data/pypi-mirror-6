#include <boost/regex.hpp>
#include "Python.h"
#include <structmember.h>

typedef boost::wregex pyregex;
typedef struct {
	PyObject_HEAD
	pyregex *rx;
} BoostRegexObject;

static int BoostRegex_init(BoostRegexObject *self, PyObject *args, PyObject *kwds)
{
	PyUnicodeObject *pattern;
	int len;
    wchar_t *w_pattern;

	if (!PyArg_ParseTuple(args, "U", &pattern))
	    return NULL;

    try{
        len = PyUnicode_GET_SIZE(pattern);
        w_pattern = new wchar_t[len + 1];
        w_pattern[len] = 0;
        if (PyUnicode_AsWideChar(pattern, w_pattern, len)!=len){
            printf("Internal error");
            PyErr_SetString(PyExc_ValueError, "Internal error");
            return NULL;
        };
        //printf("%i: %S\n", wcslen(w_pattern), w_pattern);
    }
    catch(...)
    {
        printf("Internal exception init");
        PyErr_SetString(PyExc_ValueError, "Internal exception init");
        return NULL;
    }

  	self->rx = new pyregex(w_pattern, boost::regex_constants::normal | boost::regex_constants::no_except);
    delete w_pattern;
	return 0;
};

static void BoostRegex_dealloc(BoostRegexObject *self)
{
    delete self->rx;
    Py_TYPE(self)->tp_free((PyObject *)self);
};

static PyMemberDef BoostRegex_members[] = {
	{NULL}  /* Sentinel */
};

static PyObject *BoostRegex_match(BoostRegexObject *self, PyObject *args)
{
	PyUnicodeObject *text;
	int len;
	bool match;
    wchar_t *w_text;

	if (!PyArg_ParseTuple(args, "U", &text))
	    return NULL;

    try {
        len = PyUnicode_GET_SIZE(text);
        w_text = new wchar_t[len + 1];
        w_text[len] = 0;
        if (PyUnicode_AsWideChar(text, w_text, len)!=len){
            printf("Internal error");
            PyErr_SetString(PyExc_ValueError, "Internal error");
            return NULL;
        };
    }
    catch(...)
    {
        printf("Internal exception");
        PyErr_SetString(PyExc_ValueError, "Internal exception");
        return NULL;
    }

    if (self->rx->empty()) {
        PyErr_SetString(PyExc_ValueError, "Regular expression invalid");
        return NULL;
    };

    try {
        match = boost::regex_match(w_text, *self->rx);
        delete w_text;
        if (match)
        {
            Py_INCREF(Py_True);
            return Py_True;
        }
        else
        {
            Py_INCREF(Py_False);
            return Py_False;
        };
    }
    catch (...) {
        PyErr_SetString(PyExc_RuntimeError, "Matching failed");
        return NULL;
    };
};

static PyObject *BoostRegex_search(BoostRegexObject *self, PyObject *args)
{
	Py_UNICODE *text;
	bool match;

	if (!PyArg_ParseTuple(args, "u", &text))
	    return NULL;

    if (self->rx->empty()) {
        PyErr_SetString(PyExc_ValueError, "Regular expression invalid");
        return NULL;
    };

    try {
        //match = boost::regex_search((CHAR_TYPE*)text, *self->rx);
        if (match)
        {
            Py_INCREF(Py_True);
            return Py_True;
        }
        else
        {
            Py_INCREF(Py_False);
            return Py_False;
        };
    }
    catch (...) {
        PyErr_SetString(PyExc_RuntimeError, "Searching failed");
        return NULL;
    };
};

static PyMethodDef BoostRegex_methods[] = {
	{"match", (PyCFunction)BoostRegex_match, METH_VARARGS, "Full regex match."},
	{"search", (PyCFunction)BoostRegex_search, METH_VARARGS, "Regex search."},
	{NULL}
};

static char BoostRegex_doc[] =
	"Boost regular expression.";

static PyTypeObject BoostRegexObjectType = {
	PyObject_HEAD_INIT(NULL)
	0,				/* ob_size           */
	"boost_regex.BoostRegex",			/* tp_name           */
	sizeof(BoostRegexObject),		/* tp_basicsize      */
	0,				/* tp_itemsize       */
	(destructor)BoostRegex_dealloc,				/* tp_dealloc        */
	0,				/* tp_print          */
	0,				/* tp_getattr        */
	0,				/* tp_setattr        */
	0,				/* tp_compare        */
	0,				/* tp_repr           */
	0,				/* tp_as_number      */
	0,				/* tp_as_sequence    */
	0,				/* tp_as_mapping     */
	0,				/* tp_hash           */
	0,				/* tp_call           */
	0,				/* tp_str            */
	0,				/* tp_getattro       */
	0,				/* tp_setattro       */
	0,				/* tp_as_buffer      */
	Py_TPFLAGS_DEFAULT,		/* tp_flags          */
	BoostRegex_doc,			/* tp_doc            */
	0,				/* tp_traverse       */
	0,				/* tp_clear          */
	0,				/* tp_richcompare    */
	0,				/* tp_weaklistoffset */
	0,				/* tp_iter           */
	0,				/* tp_iternext       */
	BoostRegex_methods,	   		/* tp_methods        */
	BoostRegex_members,			/* tp_members        */
	0,				/* tp_getset         */
	0,				/* tp_base           */
	0,				/* tp_dict           */
	0,				/* tp_descr_get      */
	0,				/* tp_descr_set      */
	0,				/* tp_dictoffset     */
	(initproc)BoostRegex_init,		/* tp_init           */
    PyType_GenericAlloc,                        /* tp_alloc */
    PyType_GenericNew,                          /* tp_new */
    PyObject_Del,                            /* tp_free */
};

static PyObject* match(PyObject *self, PyObject *args)
{
	int ok;
	const char *text;
	const char *expr;
	bool match;
	ok = PyArg_ParseTuple(args, "ss", &expr, &text);

	if (ok) {
	    try {
	        using namespace boost;

            regex rx(expr);

            try {
                match = regex_match(text, rx);

                if (match)
                {
                    Py_INCREF(Py_True);
                    return Py_True;
                }
                else
                {
                    Py_INCREF(Py_False);
                    return Py_False;
                };
            }
            catch (...) {
                PyErr_SetString(PyExc_RuntimeError, "Matching failed");
                return NULL;
            };
	    }
	    catch (...) {
	        PyErr_SetString(PyExc_ValueError, "Regular expression invalid");
	        return NULL;
	    };
	};

	return NULL;
}

static PyMethodDef boost_regex_methods[] = {
	{"match", match, METH_VARARGS, "match(pattern, text)"},
	{NULL, NULL}
};

PyMODINIT_FUNC
initboost_regex(void)
{
	PyObject* m;

	if (PyType_Ready(&BoostRegexObjectType) < 0)
		return;

	m = Py_InitModule("boost_regex", boost_regex_methods);
	if (m == NULL)
		return;

	Py_INCREF(&BoostRegexObjectType);
	PyModule_AddObject(m, "BoostRegex", (PyObject *)&BoostRegexObjectType);
}




