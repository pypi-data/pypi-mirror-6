#define PY_SSIZE_T_CLEAN

#include <Python.h>
#include "liji.h"

#define MAX_WANTED_KEYS 1024
#define MIN(a, b) (((a) < (b)) ? (a) : (b))


static PyObject*
_liji_inspect(PyObject *self, PyObject *args)
{
    const char *json;
    Py_ssize_t json_len, keys_len, i;
    PyObject *keys;

    PyArg_ParseTuple(args, "s#O", &json, &json_len, &keys);
    keys_len = PyList_Size(keys);

    int str_sizes[MAX_WANTED_KEYS];
    char *str_keys[MAX_WANTED_KEYS];
    keys_len = MIN(keys_len, MAX_WANTED_KEYS);
    for (i = 0; i < keys_len; ++i) {
        PyObject *list_item = PyList_GetItem(keys, i);
        str_sizes[i] = PyString_Size(list_item);
        str_keys[i] = PyString_AsString(list_item);
    }

    liji_state state = liji_init((char *)json, json_len, str_keys, str_sizes, keys_len);

    PyObject *result_list = PyList_New(0);
    while (liji_find_multi_state(&state)) {
        PyObject *py_str = PyString_FromStringAndSize(state.response.result_start, state.response.len);
        PyList_Append(result_list, py_str);
        Py_DECREF(py_str);
    }

    return result_list;
}


static PyMethodDef liji_methods[] = {
    {"inspect", _liji_inspect, METH_VARARGS, ""},
    {0, 0, 0, 0}
};


PyMODINIT_FUNC init_liji(void) {
    Py_InitModule3("_liji", liji_methods, "liji native module");
}
