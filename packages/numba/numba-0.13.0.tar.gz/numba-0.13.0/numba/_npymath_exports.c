/*
 * This is a sample module exposing numpy math functions needed by numba.
 *
 * The module unique content will be a property containing a vector of tuples.
 * Each tuple will hold (symbol_name, function_pointer).
 */


#include "_pymodule.h"
#include <numpy/npy_math.h>

struct npy_math_entry {
    const char* name;
    void* func;
};


#define NPYMATH_SYMBOL(name) { "numba.npymath." #name, (void*) npy_##name }
struct npy_math_entry exports[] = {
    NPYMATH_SYMBOL(sin),
    NPYMATH_SYMBOL(cos),
    NPYMATH_SYMBOL(tan),
    NPYMATH_SYMBOL(asin),
    NPYMATH_SYMBOL(acos),
    NPYMATH_SYMBOL(atan),

    NPYMATH_SYMBOL(sinh),
    NPYMATH_SYMBOL(cosh),
    NPYMATH_SYMBOL(tanh),
    NPYMATH_SYMBOL(asinh),
    NPYMATH_SYMBOL(acosh),
    NPYMATH_SYMBOL(atanh),

    NPYMATH_SYMBOL(exp),
    NPYMATH_SYMBOL(exp2),
    NPYMATH_SYMBOL(expm1),

    NPYMATH_SYMBOL(log),
    NPYMATH_SYMBOL(log2),
    NPYMATH_SYMBOL(log10),
    NPYMATH_SYMBOL(log1p),

    NPYMATH_SYMBOL(floor),
    NPYMATH_SYMBOL(ceil),
    NPYMATH_SYMBOL(trunc),

    NPYMATH_SYMBOL(sqrt),

    NPYMATH_SYMBOL(deg2rad),
    NPYMATH_SYMBOL(rad2deg),

    NPYMATH_SYMBOL(atan2)
};
#undef NPY_MATH_SYMBOL

PyObject*
create_symbol_list()
{
    /*
     * note: reference stealing at its best
     * returns a PyList with a tuple for each symbol. The PyList has one reference.
     */
    size_t count = sizeof(exports) / sizeof(exports[0]);
    PyObject* pylist = PyList_New(count);
    const char* bv_format = sizeof(long) < sizeof(void*)?"(s,L)":"(s,l)";
    size_t i;

    for (i = 0; i < count; ++i) {
        /* create the tuple */
        PyObject* tuple = Py_BuildValue(bv_format, exports[i].name,
                                        exports[i].func);
        PyList_SET_ITEM(pylist, i, tuple);
    }

    return pylist;
}

MOD_INIT(_npymath_exports) {
    PyObject *module;
    MOD_DEF(module, "_npymath_exports", "No docs", NULL)
    if (!module) {
        return MOD_ERROR_VAL;
    }

    PyModule_AddObject(module, "symbols", create_symbol_list());

    return MOD_SUCCESS_VAL(module);
}


