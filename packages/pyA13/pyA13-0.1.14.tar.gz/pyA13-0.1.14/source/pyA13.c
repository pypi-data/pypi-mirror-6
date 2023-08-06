/*
 * pyA20.c
 *
 * Copyright 2013 Stanimir Petev <support@olimex.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 */


#include "Python.h"
#include "gpio_lib.h"


static PyObject *SetupException;
static PyObject *OutputException;
static PyObject *InputException;
static PyObject *inp;
static PyObject *out;
static PyObject *high;
static PyObject *low;


static int module_setup(void) {
    int result;

    result = sunxi_gpio_init();
    if(result == SETUP_DEVMEM_FAIL) {
        PyErr_SetString(SetupException, "No access to /dev/mem. Try running as root!");
        return SETUP_DEVMEM_FAIL;
    }
    else if(result == SETUP_MALLOC_FAIL) {
        PyErr_NoMemory();
        return SETUP_MALLOC_FAIL;
    }
    else if(result == SETUP_MMAP_FAIL) {
        PyErr_SetString(SetupException, "Mmap failed on module import");
        return SETUP_MMAP_FAIL;
    }
    else {
        return SETUP_OK;
    }

    return SETUP_OK;
}


static PyObject* py_output(PyObject* self, PyObject* args) {
    int gpio;
    int value;

    if(!PyArg_ParseTuple(args, "ii", &gpio, &value))
        return NULL;

    if(value != 0 && value != 1) {
        PyErr_SetString(OutputException, "Invalid output state");
        return NULL;
    }

    if(sunxi_gpio_get_cfgpin(gpio) != SUNXI_GPIO_OUTPUT) {
        PyErr_SetString(OutputException, "GPIO is not an output");
        return NULL;
    }
    sunxi_gpio_output(gpio, value);

    Py_RETURN_NONE;
}
static PyObject* py_input(PyObject* self, PyObject* args) {
    int gpio;
    int result;

    if(!PyArg_ParseTuple(args, "i", &gpio))
        return NULL;

    if(sunxi_gpio_get_cfgpin(gpio) != SUNXI_GPIO_INPUT) {
        PyErr_SetString(InputException, "GPIO is not an input");
        return NULL;
    }
    result = sunxi_gpio_input(gpio);

    if(result == -1) {
        PyErr_SetString(InputException, "Reading pin failed");
        return NULL;
    }


    return Py_BuildValue("i", result);
}

static PyObject* py_setcfg(PyObject* self, PyObject* args) {
    int gpio;
    int direction;

    if(!PyArg_ParseTuple(args, "ii", &gpio, &direction))
        return NULL;

    if(direction != 0 && direction != 1 && direction != 2) {
        PyErr_SetString(SetupException, "Invalid direction");
        return NULL;
    }
    sunxi_gpio_set_cfgpin(gpio, direction);

    Py_RETURN_NONE;
}
static PyObject* py_getcfg(PyObject* self, PyObject* args) {
    int gpio;
    int result;


    if(!PyArg_ParseTuple(args, "i", &gpio))
        return NULL;

    result = sunxi_gpio_get_cfgpin(gpio);


    return Py_BuildValue("i", result);


}
static PyObject* py_init(PyObject* self, PyObject* args) {

    module_setup();

    Py_RETURN_NONE;
}
static PyObject* py_cleanup(PyObject* self, PyObject* args) {

    sunxi_gpio_cleanup();
    Py_RETURN_NONE;
}


PyMethodDef module_methods[] = {
    {"init", py_init, METH_NOARGS, "Initialize module"},
    {"cleanup", py_cleanup, METH_NOARGS, "munmap /dev/map."},
    {"setcfg", py_setcfg, METH_VARARGS, "Set direction."},
    {"getcfg", py_getcfg, METH_VARARGS, "Get direction."},
    {"output", py_output, METH_VARARGS, "Set output state"},
    {"input", py_input, METH_VARARGS, "Get input state"},
    {NULL, NULL, 0, NULL}
};
#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef module_def = {
    PyModuleDef_HEAD_INIT,
    "A13 module",
    NULL,
    -1,
    module_methods
};
#endif
PyMODINIT_FUNC initA13_GPIO(void) {
    PyObject* module = NULL;


#if PY_MAJOR_VERSION >= 3
    module = PyModule_Create(&module_methods);
#else
    module = Py_InitModule("A13_GPIO", module_methods);
#endif


    if(module == NULL)
#if PY_MAJOR_VERSION >= 3
        return module;
#else
        return;
#endif



    SetupException = PyErr_NewException("PyA13.SetupException", NULL, NULL);
    PyModule_AddObject(module, "SetupException", SetupException);
    OutputException = PyErr_NewException("PyA13.OutputException", NULL, NULL);
    PyModule_AddObject(module, "OutputException", OutputException);
    InputException = PyErr_NewException("PyA13.InputException", NULL, NULL);
    PyModule_AddObject(module, "InputException", InputException);



    high = Py_BuildValue("i", HIGH);
    PyModule_AddObject(module, "HIGH", high);

    low = Py_BuildValue("i", LOW);
    PyModule_AddObject(module, "LOW", low);

    inp = Py_BuildValue("i", INPUT);
    PyModule_AddObject(module, "INPUT", inp);

    out = Py_BuildValue("i", OUTPUT);
    PyModule_AddObject(module, "OUTPUT", out);

    // Build Pin Objects
	PyModule_AddObject(module,	"PIN2_9",	Py_BuildValue("i", SUNXI_GPB(2)));
	PyModule_AddObject(module,	"PIN2_11",	Py_BuildValue("i", SUNXI_GPB(3)));
	PyModule_AddObject(module,	"PIN2_13",	Py_BuildValue("i", SUNXI_GPB(4)));
	PyModule_AddObject(module,	"PIN2_21",	Py_BuildValue("i", SUNXI_GPC(0)));
	PyModule_AddObject(module,	"PIN2_23",	Py_BuildValue("i", SUNXI_GPC(1)));
	PyModule_AddObject(module,	"PIN2_25",	Py_BuildValue("i", SUNXI_GPC(2)));
	PyModule_AddObject(module,	"PIN2_27",	Py_BuildValue("i", SUNXI_GPC(3)));
	PyModule_AddObject(module,	"PIN2_29",	Py_BuildValue("i", SUNXI_GPC(4)));
	PyModule_AddObject(module,	"PIN2_31",	Py_BuildValue("i", SUNXI_GPC(5)));
	PyModule_AddObject(module,	"PIN2_33",	Py_BuildValue("i", SUNXI_GPC(6)));
	PyModule_AddObject(module,	"PIN2_35",	Py_BuildValue("i", SUNXI_GPC(7)));
	PyModule_AddObject(module,	"PIN2_37",	Py_BuildValue("i", SUNXI_GPC(8)));
	PyModule_AddObject(module,	"PIN2_39",	Py_BuildValue("i", SUNXI_GPC(9)));
	PyModule_AddObject(module,	"PIN2_40",	Py_BuildValue("i", SUNXI_GPC(10)));
	PyModule_AddObject(module,	"PIN2_38",	Py_BuildValue("i", SUNXI_GPC(11)));
	PyModule_AddObject(module,	"PIN2_36",	Py_BuildValue("i", SUNXI_GPC(12)));
	PyModule_AddObject(module,	"PIN2_34",	Py_BuildValue("i", SUNXI_GPC(13)));
	PyModule_AddObject(module,	"PIN2_32",	Py_BuildValue("i", SUNXI_GPC(14)));
	PyModule_AddObject(module,	"PIN2_30",	Py_BuildValue("i", SUNXI_GPC(15)));
	PyModule_AddObject(module,	"PIN2_28",	Py_BuildValue("i", SUNXI_GPC(19)));
	PyModule_AddObject(module,	"PIN2_6",	Py_BuildValue("i", SUNXI_GPG(10)));
	PyModule_AddObject(module,	"PIN2_8",	Py_BuildValue("i", SUNXI_GPG(11)));
	PyModule_AddObject(module,	"PIN2_10",	Py_BuildValue("i", SUNXI_GPG(10)));
	PyModule_AddObject(module,	"PIN2_26",	Py_BuildValue("i", SUNXI_GPE(4)));
	PyModule_AddObject(module,	"PIN2_24",	Py_BuildValue("i", SUNXI_GPE(5)));
	PyModule_AddObject(module,	"PIN2_22",	Py_BuildValue("i", SUNXI_GPE(6)));
	PyModule_AddObject(module,	"PIN2_20",	Py_BuildValue("i", SUNXI_GPE(7)));
	PyModule_AddObject(module,	"PIN2_18",	Py_BuildValue("i", SUNXI_GPE(8)));
	PyModule_AddObject(module,	"PIN2_16",	Py_BuildValue("i", SUNXI_GPE(9)));
	PyModule_AddObject(module,	"PIN2_14",	Py_BuildValue("i", SUNXI_GPE(10)));
	PyModule_AddObject(module,	"PIN2_12",	Py_BuildValue("i", SUNXI_GPE(11)));




    if(Py_AtExit(sunxi_gpio_cleanup) != 0){
        sunxi_gpio_cleanup();
#if PY_MAJOR_VERSION >= 3
        return NULL;
#else
        return;
#endif
    }



}

