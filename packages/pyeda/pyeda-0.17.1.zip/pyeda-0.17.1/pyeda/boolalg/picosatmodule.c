// Filename: picosatmodule.c
//
// Constants
//     PICOSAT_VERSION
//     PICOSAT_COPYRIGHT
//
// Exceptions:
//     PicosatError
//
// Interface Functions:
//     satisfy_one
//     satisfy_all

#include <Python.h>
#include <math.h>
#include "picosat.h"

static PyObject *PicosatError;

PyDoc_STRVAR(picosaterr_docstring, "PicoSAT Error");

//==============================================================================
// Pass these to picosat_minit to use Python as PicoSAT's memory manager.
//==============================================================================

inline static void *
py_malloc(void *pmgr, size_t nbytes) {
    return PyMem_Malloc(nbytes);
}

inline static void *
py_realloc(void *pmgr, void *p, size_t old, size_t new) {
    return PyMem_Realloc(p, new);
}

inline static void
py_free(void *pmgr, void *p, size_t nbytes) {
    PyMem_Free(p);
}

//==============================================================================
// Add all clause literals to a PicoSAT instance.
//
// Returns:
//     0 : Exception
//     1 : Success
//==============================================================================

static int
add_clauses(PicoSAT *picosat, PyObject *clauses) {

    int nvars;
    PyObject *pyclauses, *pyclause;
    PyObject *pylits, *pylit;
    int lit;

    nvars = picosat_variables(picosat);

    pyclauses = PyObject_GetIter(clauses);
    if (pyclauses == NULL) {
        goto ADD_CLAUSES_ERROR;
    }
    while ((pyclause = PyIter_Next(pyclauses)) != 0) {
        pylits = PyObject_GetIter(pyclause);
        if (pylits == NULL) {
            goto ADD_CLAUSES_DECREF_PYCLAUSES;
        }
        while ((pylit = PyIter_Next(pylits)) != 0) {
            if (!PyLong_Check(pylit)) {
                PyErr_SetString(PyExc_TypeError, "expected clause literal to be an int");
                goto ADD_CLAUSES_DECREF_PYLITS;
            }
            lit = PyLong_AsLong(pylit);
            if (lit == 0 || abs(lit) > nvars) {
                PyErr_Format(
                    PyExc_ValueError,
                    "expected clause literal in range [-%d, 0), (0, %d], got: %d",
                    nvars, nvars, lit
                );
                goto ADD_CLAUSES_DECREF_PYLITS;
            }

            // Add clause literal
            picosat_add(picosat, lit);

            Py_DECREF(pylit);
        } // for pylit in pylits
        Py_DECREF(pylits);

        if (PyErr_Occurred()) {
            goto ADD_CLAUSES_DECREF_PYCLAUSES;
        }

        // Terminate clause
        picosat_add(picosat, 0);

        Py_DECREF(pyclause);
    } // for pyclause in pyclauses
    Py_DECREF(pyclauses);

    if (PyErr_Occurred()) {
        goto ADD_CLAUSES_ERROR;
    }

    // Success!
    return 1;

ADD_CLAUSES_DECREF_PYLITS:
    Py_DECREF(pylit);
    Py_DECREF(pylits);

ADD_CLAUSES_DECREF_PYCLAUSES:
    Py_DECREF(pyclause);
    Py_DECREF(pyclauses);

ADD_CLAUSES_ERROR:
    return 0;
}

//==============================================================================
// Add all assumptions to a PicoSAT instance.
//
// Returns:
//     0 : Exception
//     1 : Success
//==============================================================================

static int
add_assumptions(PicoSAT *picosat, PyObject *assumptions) {

    int nvars;
    PyObject *pylits, *pylit;
    int lit;

    nvars = picosat_variables(picosat);

    pylits = PyObject_GetIter(assumptions);
    if (pylits == NULL) {
        goto ADD_ASSUMPTIONS_ERROR;
    }
    while ((pylit = PyIter_Next(pylits)) != 0) {
        if (!PyLong_Check(pylit)) {
            PyErr_SetString(PyExc_TypeError, "expected assumption literal to be an int");
            goto ADD_ASSUMPTIONS_DECREF_PYLITS;
        }
        lit = PyLong_AsLong(pylit);
        if (lit == 0 || abs(lit) > nvars) {
            PyErr_Format(
                PyExc_ValueError,
                "expected assumption literal in range [-%d, 0), (0, %d], got: %d",
                nvars, nvars, lit
            );
            goto ADD_ASSUMPTIONS_DECREF_PYLITS;
        }

        // Add assumption literal
        picosat_assume(picosat, lit);

        Py_DECREF(pylit);
    } // for pylit in pylits
    Py_DECREF(pylits);

    if (PyErr_Occurred()) {
        goto ADD_ASSUMPTIONS_ERROR;
    }

    // Success!
    return 1;

ADD_ASSUMPTIONS_DECREF_PYLITS:
    Py_DECREF(pylit);
    Py_DECREF(pylits);

ADD_ASSUMPTIONS_ERROR:
    return 0;
}


//==============================================================================
// Retrieve a solution from PicoSAT, and convert it to a Python tuple.
// Return NULL if an error happens.
//
// The tuple items map to Boolean values as follows:
//     -1 : 0
//      0 : unknown
//      1 : 1
//==============================================================================

static PyObject *
get_soln(PicoSAT *picosat) {

    int i;
    int nvars;
    PyObject *pytuple, *pyitem;

    nvars = picosat_variables(picosat);

    pytuple = PyTuple_New(nvars);
    if (pytuple == NULL) {
        goto GET_SOLN_ERROR;
    }
    for (i = 1; i <= nvars; i++) {
        pyitem = PyLong_FromLong((long) picosat_deref(picosat, i));
        if (pyitem == NULL) {
            goto GET_SOLN_DECREF_PYTUPLE;
        }
        if (PyTuple_SetItem(pytuple, i - 1, pyitem) < 0) {
            goto GET_SOLN_DECREF_PYITEM;
        }
    }

    // Success!
    return pytuple;

GET_SOLN_DECREF_PYITEM:
    Py_DECREF(pyitem);

GET_SOLN_DECREF_PYTUPLE:
    Py_DECREF(pytuple);

GET_SOLN_ERROR:
    return NULL;
}

//==============================================================================
// Add the inverse of the current solution to the clauses.
//
// NOTE: Copied from PicoSAT "app.c".
//==============================================================================

static int
block_soln(PicoSAT *picosat, signed char *soln)
{
    int i;
    int nvars;

    nvars = picosat_variables(picosat);
    for (i = 1; i <= nvars; i++)
        soln[i] = (picosat_deref(picosat, i) > 0) ? 1 : -1;

    for (i = 1; i <= nvars; i++)
        picosat_add(picosat, (soln[i] < 0) ? i : -i);

    picosat_add(picosat, 0);
    return 1;
}

//==============================================================================
// Return a single solution to a CNF instance.
//
// satisfy_one(nvars, clauses,
//             verbosity=0, default_phase=2, propagation_limit=-1,
//             decision_limit=-1)
//==============================================================================

PyDoc_STRVAR(satisfy_one_docstring,
    "\n\
    If the input CNF is satisfiable, return a satisfying input point.\n\
    A contradiction will return None.\n\
\n\
    Parameters\n\
    ----------\n\
    nvars : posint\n\
        Number of variables in the CNF\n\
\n\
    clauses : iter of iter of (nonzero) int\n\
        The CNF clauses\n\
\n\
    verbosity : int, optional\n\
        Set verbosity level. A verbosity level of 1 and above prints more and\n\
        more detailed progress reports to stdout.\n\
\n\
    default_phase : {0, 1, 2, 3}\n\
        Set default initial phase:\n\
            0 = false\n\
            1 = true\n\
            2 = Jeroslow-Wang (default)\n\
            3 = random\n\
\n\
    progagation_limit : int\n\
        Set a limit on the number of propagations. A negative value sets no\n\
        propagation limit.\n\
\n\
    decision_limit : int\n\
        Set a limit on the number of decisions. A negative value sets no\n\
        decision limit.\n\
\n\
    assumptions : iter of (nonzero) int\n\
        Add assumptions (unit clauses) to the CNF\n\
\n\
    Returns\n\
    -------\n\
    tuple of {-1, 0, 1}\n\
        -1 : zero\n\
         0 : dont-care\n\
         1 : one\n\
    "
);

static PyObject *
satisfy_one(PyObject *self, PyObject *args, PyObject *kwargs) {

    static char *keywords[] = {
        "nvars", "clauses",
        "verbosity", "default_phase", "propagation_limit", "decision_limit",
        "assumptions",
        NULL
    };

    // PicoSAT instance
    PicoSAT *picosat;

    // PicoSAT input parameters
    int nvars = 0;
    PyObject *clauses;
    int verbosity = 0;
    int default_phase = 2; // 0 = false, 1 = true, 2 = Jeroslow-Wang, 3 = random
    int propagation_limit = -1;
    int decision_limit = -1;
    PyObject *assumptions = NULL;

    // PicoSAT return value
    int result;

    // Python return value
    PyObject *pyret = NULL;

    if (!PyArg_ParseTupleAndKeywords(
            args, kwargs, "iO|iiiiO:satisfy_one", keywords,
            &nvars, &clauses,
            &verbosity, &default_phase, &propagation_limit, &decision_limit,
            &assumptions)) {
        goto SATISFY_ONE_RETURN;
    }

    if (nvars < 0) {
        PyErr_Format(PyExc_ValueError, "expected nvars >= 0, got: %d", nvars);
        goto SATISFY_ONE_RETURN;
    }
    if (default_phase < 0 || default_phase > 3) {
        PyErr_Format(PyExc_ValueError, "expected default_phase in {0, 1, 2, 3}, got: %d", default_phase);
        goto SATISFY_ONE_RETURN;
    }

    picosat = picosat_minit(NULL, py_malloc, py_realloc, py_free);
    if (picosat == NULL) {
        PyErr_SetString(PicosatError, "could not initialize PicoSAT");
        goto SATISFY_ONE_RETURN;
    }

    picosat_set_verbosity(picosat, verbosity);
    picosat_set_global_default_phase(picosat, default_phase);
    picosat_set_propagation_limit(picosat, propagation_limit);

    picosat_adjust(picosat, nvars);

    if (!add_clauses(picosat, clauses)) {
        goto SATISFY_ONE_RESET_PICOSAT;
    }
    if (assumptions != NULL && assumptions != Py_None) {
        if (!add_assumptions(picosat, assumptions)) {
            goto SATISFY_ONE_RESET_PICOSAT;
        }
    }

    // picosat_set_seed(picosat, seed);

    // Do the damn thing
    Py_BEGIN_ALLOW_THREADS
    result = picosat_sat(picosat, decision_limit);
    Py_END_ALLOW_THREADS

    // Prepare Python return value
    if (result == PICOSAT_UNSATISFIABLE) {
        Py_RETURN_NONE;
    }
    else if (result == PICOSAT_SATISFIABLE) {
        // Might be NULL
        pyret = get_soln(picosat);
    }
    else if (result == PICOSAT_UNKNOWN) {
        PyErr_SetString(PicosatError, "PicoSAT returned UNKNOWN");
    }
    else {
        PyErr_Format(PicosatError, "PicoSAT returned: %d", result);
    }

SATISFY_ONE_RESET_PICOSAT:
    picosat_reset(picosat);

SATISFY_ONE_RETURN:
    return pyret;
}

//==============================================================================
// Iterate through all solutions to a CNF instance.
//
// satisfy_all(nvars, clauses,
//             verbosity=0, default_phase=2, propagation_limit=-1,
//             decision_limit=-1)
//==============================================================================

PyDoc_STRVAR(satisfy_all_docstring,
    "\n\
    Iterate through all satisfying input points.\n\
\n\
    Parameters\n\
    ----------\n\
    nvars : posint\n\
        Number of variables in the CNF\n\
\n\
    clauses : iter of iter of (nonzero) int\n\
        The CNF clauses\n\
\n\
    verbosity : int, optional\n\
        Set verbosity level. A verbosity level of 1 and above prints more and\n\
        more detailed progress reports to stdout.\n\
\n\
    default_phase : {0, 1, 2, 3}\n\
        Set default initial phase:\n\
            0 = false\n\
            1 = true\n\
            2 = Jeroslow-Wang (default)\n\
            3 = random\n\
\n\
    progagation_limit : int\n\
        Set a limit on the number of propagations. A negative value sets no\n\
        propagation limit.\n\
\n\
    decision_limit : int\n\
        Set a limit on the number of decisions. A negative value sets no\n\
        decision limit.\n\
\n\
    Returns\n\
    -------\n\
    iter of tuple of {-1, 0, 1}\n\
        -1 : zero\n\
         0 : dont-care\n\
         1 : one\n\
    "
);

//==============================================================================
// Iterator state
//==============================================================================

typedef struct {
    PyObject_HEAD

    PicoSAT *picosat;
    int decision_limit;
    signed char *soln;
} SatisfyAllState;

//==============================================================================
// satisfy_all constructor
//==============================================================================

static PyObject *
satisfy_all_new(PyTypeObject *cls, PyObject *args, PyObject *kwargs)
{
    static char *keywords[] = {
        "nvars", "clauses",
        "verbosity", "default_phase", "propagation_limit", "decision_limit",
        NULL
    };

    // PicoSAT instance
    PicoSAT *picosat;

    // PicoSAT input parameters
    int nvars = 0;
    PyObject *clauses;
    int verbosity = 0;
    int default_phase = 2; // 0 = false, 1 = true, 2 = Jeroslow-Wang, 3 = random
    int propagation_limit = -1;
    int decision_limit = -1;

    // Python return value
    SatisfyAllState *state;

    if (!PyArg_ParseTupleAndKeywords(
            args, kwargs, "iO|iiii:satisfy_all", keywords,
            &nvars, &clauses,
            &verbosity, &default_phase, &propagation_limit, &decision_limit)) {
        goto SATISFY_ALL_ERROR;
    }

    if (nvars < 0) {
        PyErr_Format(PyExc_ValueError, "expected nvars >= 0, got: %d", nvars);
        goto SATISFY_ALL_ERROR;
    }
    if (default_phase < 0 || default_phase > 3) {
        PyErr_Format(PyExc_ValueError, "expected default_phase in {0, 1, 2, 3}, got: %d", default_phase);
        goto SATISFY_ALL_ERROR;
    }

    picosat = picosat_minit(NULL, py_malloc, py_realloc, py_free);
    if (picosat == NULL) {
        PyErr_SetString(PicosatError, "could not initialize PicoSAT");
        goto SATISFY_ALL_ERROR;
    }

    picosat_set_verbosity(picosat, verbosity);
    picosat_set_global_default_phase(picosat, default_phase);
    picosat_set_propagation_limit(picosat, propagation_limit);

    picosat_adjust(picosat, nvars);

    if (!add_clauses(picosat, clauses)) {
        goto SATISFY_ALL_RESET_PICOSAT;
    }

    // picosat_set_seed(picosat, seed);

    state = (SatisfyAllState *) cls->tp_alloc(cls, 0);
    if (state == NULL) {
        goto SATISFY_ALL_RESET_PICOSAT;
    }

    state->picosat = picosat;
    state->decision_limit = decision_limit;
    state->soln = PyMem_Malloc(nvars + 1);
    if (state->soln == NULL) {
        PyErr_NoMemory();
        goto SATISFY_ALL_RESET_PICOSAT;
    }

    // Success!
    return (PyObject *) state;

SATISFY_ALL_RESET_PICOSAT:
    picosat_reset(picosat);

SATISFY_ALL_ERROR:
    return NULL;
}

//==============================================================================
// satisfy_all destructor
//==============================================================================

static void
satisfy_all_dealloc(SatisfyAllState *state)
{
    PyMem_Free(state->soln);
    Py_TYPE(state)->tp_free(state);

    picosat_reset(state->picosat);
}

//==============================================================================
// satisfy_all next method
//==============================================================================

static PyObject *
satisfy_all_next(SatisfyAllState *state)
{
    PyObject *pysoln;

    // PicoSAT return value
    int result;

    // Python return value
    PyObject *pyret = NULL;

    // Do the damn thing
    Py_BEGIN_ALLOW_THREADS
    result = picosat_sat(state->picosat, state->decision_limit);
    Py_END_ALLOW_THREADS

    // Prepare Python return value
    if (result == PICOSAT_UNSATISFIABLE) {
        // No solution
    }
    else if (result == PICOSAT_SATISFIABLE) {
        // Might be NULL
        pysoln = get_soln(state->picosat);
        if (pysoln != NULL) {
            block_soln(state->picosat, state->soln);
            pyret = pysoln;
        }
    }
    else if (result == PICOSAT_UNKNOWN) {
        // No more solutions
    }
    else {
        PyErr_Format(PicosatError, "PicoSAT returned: %d", result);
    }

    return pyret;
}

//==============================================================================
// satisfy_all type definition
//==============================================================================

static PyTypeObject
SatisfyAllType = {
    //PyObject_HEAD_INIT(NULL)
    PyVarObject_HEAD_INIT(NULL, 0)

    "satisfy_all",                      // tp_name
    sizeof(SatisfyAllState),            // tp_basicsize
    0,                                  // tp_itemsize
    (destructor) satisfy_all_dealloc,   // tp_dealloc
    0,                                  // tp_print
    0,                                  // tp_getattr
    0,                                  // tp_setattr
    0,                                  // tp_reserved
    0,                                  // tp_repr
    0,                                  // tp_as_number
    0,                                  // tp_as_sequence
    0,                                  // tp_as_mapping
    0,                                  // tp_hash
    0,                                  // tp_call
    0,                                  // tp_str
    0,                                  // tp_getattro
    0,                                  // tp_setattro
    0,                                  // tp_as_buffer
    Py_TPFLAGS_DEFAULT,                 // tp_flags
    satisfy_all_docstring,              // tp_doc
    0,                                  // tp_traverse
    0,                                  // tp_clear
    0,                                  // tp_richcompare
    0,                                  // tp_weaklistoffset
    PyObject_SelfIter,                  // tp_iter
    (iternextfunc) satisfy_all_next,    // tp_iternext
    0,                                  // tp_methods
    0,                                  // tp_members
    0,                                  // tp_getset
    0,                                  // tp_base
    0,                                  // tp_dict
    0,                                  // tp_descr_get
    0,                                  // tp_descr_set
    0,                                  // tp_dictoffset
    0,                                  // tp_init
    PyType_GenericAlloc,                // tp_alloc
    satisfy_all_new,                    // tp_new
};

//==============================================================================
// Module Definition
//==============================================================================

PyDoc_STRVAR(module_docstring,
"\n\
PicoSAT Interface\n\
\n\
Constants:\n\
    PICOSAT_VERSION\n\
    PICOSAT_COPYRIGHT\n\
\n\
Exceptions:\n\
    PicosatError\n\
\n\
Interface Functions:\n\
    satisfy_one\n\
    satisfy_all\n\
"
);

static PyMethodDef functions[] = {
    {"satisfy_one", (PyCFunction) satisfy_one, METH_VARARGS | METH_KEYWORDS, satisfy_one_docstring},

    // sentinel
    {NULL, NULL, 0, NULL}
};

static PyModuleDef module = {
    PyModuleDef_HEAD_INIT,

    "picosat",          // m_name
    module_docstring,   // m_doc
    -1,                 // m_size
    functions,          // m_methods
};

PyMODINIT_FUNC
PyInit_picosat(void)
{
    PyObject *pymodule;

    pymodule = PyModule_Create(&module);
    if (pymodule == NULL)
        goto INIT_PICOSAT_ERROR;

    // Define Constants
    if (PyModule_AddStringConstant(pymodule, "PICOSAT_VERSION", "957") < 0)
        goto INIT_PICOSAT_ERROR;
    if (PyModule_AddStringConstant(pymodule, "PICOSAT_COPYRIGHT", picosat_copyright()) < 0)
        goto INIT_PICOSAT_ERROR;

    // Define PicosatError
    PicosatError = PyErr_NewExceptionWithDoc("picosat.PicosatError",
                                             picosaterr_docstring, NULL, NULL);
    if (PicosatError == NULL) {
        goto INIT_PICOSAT_ERROR;
    }
    else {
        Py_INCREF(PicosatError);
        if (PyModule_AddObject(pymodule, "PicosatError", PicosatError) < 0) {
            Py_DECREF(PicosatError);
            goto INIT_PICOSAT_ERROR;
        }
    }

    // Define satisfy_all
    if (PyType_Ready(&SatisfyAllType) < 0) {
        goto INIT_PICOSAT_ERROR;
    }
    else {
        Py_INCREF((PyObject *) &SatisfyAllType);
        if (PyModule_AddObject(pymodule, "satisfy_all", (PyObject *) &SatisfyAllType) < 0) {
            Py_DECREF((PyObject *) &SatisfyAllType);
            goto INIT_PICOSAT_ERROR;
        }
    }

    // Success!
    return pymodule;

INIT_PICOSAT_ERROR:
    return NULL;
}
