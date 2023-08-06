#include <regex>
#include "Python.h"

static PyObject *
regex_match(PyObject *self, PyObject *args)
{
	int ok;
	const char *text;
	const char *expr;
	bool match;
	ok = PyArg_ParseTuple(args, "ss", &expr, &text);

	if (ok) {
	    try {
	        #ifdef _WIN32
        	std::tr1::regex rx (expr);
        	#endif

	        #ifdef linux
        	std::regex rx (expr);
        	#endif

            try {
                match = std::tr1::regex_match(text, rx);
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

static PyMethodDef tr1regex_methods[] = {
	{"match", regex_match, METH_VARARGS, "match(pattern, text)"},
	{NULL, NULL}
};

PyMODINIT_FUNC
inittr1regex(void)
{
	Py_InitModule("tr1regex", tr1regex_methods);
}




