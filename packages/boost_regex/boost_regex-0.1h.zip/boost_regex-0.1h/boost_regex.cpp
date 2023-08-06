#include <boost/regex.hpp>
#include "Python.h"

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
        	regex rx (expr);

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
	Py_InitModule("boost_regex", boost_regex_methods);
}




