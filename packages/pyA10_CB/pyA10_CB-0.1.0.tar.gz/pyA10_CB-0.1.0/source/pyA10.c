/*
 * pyA10.c
 *
 * Copyright 2014 Markus Sigg <dev.siggie@gmail.com>
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
static PyObject *per;
static PyObject *high;
static PyObject *low;

// *** U14 ***
// LCD
#define PIN_PD0   SUNXI_GPD(0)
#define PIN_PD1   SUNXI_GPD(1)
#define PIN_PD2   SUNXI_GPD(2)
#define PIN_PD3   SUNXI_GPD(3)
#define PIN_PD4   SUNXI_GPD(4)
#define PIN_PD5   SUNXI_GPD(5)
#define PIN_PD6   SUNXI_GPD(6)
#define PIN_PD7   SUNXI_GPD(7)
#define PIN_PD8   SUNXI_GPD(8)
#define PIN_PD9   SUNXI_GPD(9)
#define PIN_PD10  SUNXI_GPD(10)
#define PIN_PD11  SUNXI_GPD(11)
#define PIN_PD12  SUNXI_GPD(12)
#define PIN_PD13  SUNXI_GPD(13)
#define PIN_PD14  SUNXI_GPD(14)
#define PIN_PD15  SUNXI_GPD(15)
#define PIN_PD16  SUNXI_GPD(16)
#define PIN_PD17  SUNXI_GPD(17)
#define PIN_PD18  SUNXI_GPD(18)
#define PIN_PD19  SUNXI_GPD(19)
#define PIN_PD20  SUNXI_GPD(20)
#define PIN_PD21  SUNXI_GPD(21)
#define PIN_PD22  SUNXI_GPD(22)
#define PIN_PD23  SUNXI_GPD(23)
#define PIN_PD24  SUNXI_GPD(24)
#define PIN_PD25  SUNXI_GPD(25)
#define PIN_PD26  SUNXI_GPD(26)
#define PIN_PD27  SUNXI_GPD(27)
#define PIN_PB2   SUNXI_GPB(2)
#define PIN_PB10  SUNXI_GPB(10)
#define PIN_PB11  SUNXI_GPB(11)
#define PIN_PH7	  SUNXI_GPH(7)
// SPI0
#define PIN_PI10  SUNXI_GPI(10)
#define PIN_PI11  SUNXI_GPI(11)
#define PIN_PI12  SUNXI_GPI(12)
#define PIN_PI13  SUNXI_GPI(13)

// *** U15 ***
// CSI1/TS
#define PIN_PH14  SUNXI_GPH(14)
#define PIN_PH15  SUNXI_GPH(15)
#define PIN_PB18  SUNXI_GPB(18)
#define PIN_PB19  SUNXI_GPB(19)
#define PIN_PG0   SUNXI_GPG(0)
#define PIN_PG1   SUNXI_GPG(1)
#define PIN_PG2   SUNXI_GPG(2)
#define PIN_PG3   SUNXI_GPG(3)
#define PIN_PG4   SUNXI_GPG(4)
#define PIN_PG5   SUNXI_GPG(5)
#define PIN_PG6   SUNXI_GPG(6)
#define PIN_PG7   SUNXI_GPG(7)
#define PIN_PG8   SUNXI_GPG(8)
#define PIN_PG9   SUNXI_GPG(9)
#define PIN_PG10  SUNXI_GPG(10)
#define PIN_PG11  SUNXI_GPG(11)
// SDIO3
#define PIN_PI4   SUNXI_GPI(4)
#define PIN_PI5   SUNXI_GPI(5)
#define PIN_PI6   SUNXI_GPI(6)
#define PIN_PI7   SUNXI_GPI(7)
#define PIN_PI8   SUNXI_GPI(8)
#define PIN_PI9   SUNXI_GPI(9)
// CSI0/TS
#define PIN_PE4   SUNXI_GPE(4)
#define PIN_PE5   SUNXI_GPE(5)
#define PIN_PE6   SUNXI_GPE(6)
#define PIN_PE7   SUNXI_GPE(7)
#define PIN_PE8   SUNXI_GPE(8)
#define PIN_PE9   SUNXI_GPE(9)
#define PIN_PE10  SUNXI_GPE(10)
#define PIN_PE11  SUNXI_GPE(11)



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
        PyErr_SetString(OutputException, "GPIO is no an output");
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
    "A10 module",
    NULL,
    -1,
    module_methods
};
#endif
PyMODINIT_FUNC initA10_GPIO(void) {
    PyObject* module = NULL;


#if PY_MAJOR_VERSION >= 3
    module = PyModule_Create(&module_methods);
#else
    module = Py_InitModule("A10_GPIO", module_methods);
#endif


    if(module == NULL)
#if PY_MAJOR_VERSION >= 3
        return module;
#else
        return;
#endif



    SetupException = PyErr_NewException("PyA10.SetupException", NULL, NULL);
    PyModule_AddObject(module, "SetupException", SetupException);
    OutputException = PyErr_NewException("PyA10.OutputException", NULL, NULL);
    PyModule_AddObject(module, "OutputException", OutputException);
    InputException = PyErr_NewException("PyA10.InputException", NULL, NULL);
    PyModule_AddObject(module, "InputException", InputException);



    high = Py_BuildValue("i", HIGH);
    PyModule_AddObject(module, "HIGH", high);

    low = Py_BuildValue("i", LOW);
    PyModule_AddObject(module, "LOW", low);

    inp = Py_BuildValue("i", INPUT);
    PyModule_AddObject(module, "INPUT", inp);

    out = Py_BuildValue("i", OUTPUT);
    PyModule_AddObject(module, "OUTPUT", out);

    per = Py_BuildValue("i", PER);
    PyModule_AddObject(module, "PER", per);


    // *** U14 ***
    // LCD
    PyModule_AddObject(module, "PD0", Py_BuildValue("i", PIN_PD0));
    PyModule_AddObject(module, "PD1", Py_BuildValue("i", PIN_PD1));
    PyModule_AddObject(module, "PD2", Py_BuildValue("i", PIN_PD2));
    PyModule_AddObject(module, "PD3", Py_BuildValue("i", PIN_PD3));
    PyModule_AddObject(module, "PD4", Py_BuildValue("i", PIN_PD4));
    PyModule_AddObject(module, "PD5", Py_BuildValue("i", PIN_PD5));
    PyModule_AddObject(module, "PD6", Py_BuildValue("i", PIN_PD6));
    PyModule_AddObject(module, "PD7", Py_BuildValue("i", PIN_PD7));
    PyModule_AddObject(module, "PD8", Py_BuildValue("i", PIN_PD8));
    PyModule_AddObject(module, "PD9", Py_BuildValue("i", PIN_PD9));
    PyModule_AddObject(module, "PD10", Py_BuildValue("i", PIN_PD10));
    PyModule_AddObject(module, "PD11", Py_BuildValue("i", PIN_PD11));
    PyModule_AddObject(module, "PD12", Py_BuildValue("i", PIN_PD12));
    PyModule_AddObject(module, "PD13", Py_BuildValue("i", PIN_PD13));
    PyModule_AddObject(module, "PD14", Py_BuildValue("i", PIN_PD14));
    PyModule_AddObject(module, "PD15", Py_BuildValue("i", PIN_PD15));
    PyModule_AddObject(module, "PD16", Py_BuildValue("i", PIN_PD16));
    PyModule_AddObject(module, "PD17", Py_BuildValue("i", PIN_PD17));
    PyModule_AddObject(module, "PD18", Py_BuildValue("i", PIN_PD18));
    PyModule_AddObject(module, "PD19", Py_BuildValue("i", PIN_PD19));
    PyModule_AddObject(module, "PD20", Py_BuildValue("i", PIN_PD20));
    PyModule_AddObject(module, "PD21", Py_BuildValue("i", PIN_PD21));
    PyModule_AddObject(module, "PD22", Py_BuildValue("i", PIN_PD22));
    PyModule_AddObject(module, "PD23", Py_BuildValue("i", PIN_PD23));
    PyModule_AddObject(module, "PD24", Py_BuildValue("i", PIN_PD24));
    PyModule_AddObject(module, "PD25", Py_BuildValue("i", PIN_PD25));
    PyModule_AddObject(module, "PD26", Py_BuildValue("i", PIN_PD26));
    PyModule_AddObject(module, "PD27", Py_BuildValue("i", PIN_PD27));
    PyModule_AddObject(module, "PB2", Py_BuildValue("i", PIN_PB2));
    PyModule_AddObject(module, "PB10", Py_BuildValue("i", PIN_PB10));
    PyModule_AddObject(module, "PB11", Py_BuildValue("i", PIN_PB11));
    PyModule_AddObject(module, "PH7", Py_BuildValue("i", PIN_PH7));
    // SPI0
    PyModule_AddObject(module, "PI10", Py_BuildValue("i", PIN_PI10));
    PyModule_AddObject(module, "PI11", Py_BuildValue("i", PIN_PI11));
    PyModule_AddObject(module, "PI12", Py_BuildValue("i", PIN_PI12));
    PyModule_AddObject(module, "PI13", Py_BuildValue("i", PIN_PI13));

    // *** U15 ***
    // CSI1/TS
    PyModule_AddObject(module, "PH14", Py_BuildValue("i", PIN_PH14));
    PyModule_AddObject(module, "PH15", Py_BuildValue("i", PIN_PH15));
    PyModule_AddObject(module, "PB18", Py_BuildValue("i", PIN_PB18));
    PyModule_AddObject(module, "PB19", Py_BuildValue("i", PIN_PB19));
    PyModule_AddObject(module, "PG0", Py_BuildValue("i", PIN_PG0));
    PyModule_AddObject(module, "PG1", Py_BuildValue("i", PIN_PG1));
    PyModule_AddObject(module, "PG2", Py_BuildValue("i", PIN_PG2));
    PyModule_AddObject(module, "PG3", Py_BuildValue("i", PIN_PG3));
    PyModule_AddObject(module, "PG4", Py_BuildValue("i", PIN_PG4));
    PyModule_AddObject(module, "PG5", Py_BuildValue("i", PIN_PG5));
    PyModule_AddObject(module, "PG6", Py_BuildValue("i", PIN_PG6));
    PyModule_AddObject(module, "PG7", Py_BuildValue("i", PIN_PG7));
    PyModule_AddObject(module, "PG8", Py_BuildValue("i", PIN_PG8));
    PyModule_AddObject(module, "PG9", Py_BuildValue("i", PIN_PG9));
    PyModule_AddObject(module, "PG10", Py_BuildValue("i", PIN_PG10));
    PyModule_AddObject(module, "PG11", Py_BuildValue("i", PIN_PG11));
    // SDIO3
    PyModule_AddObject(module, "PI4", Py_BuildValue("i", PIN_PI4));
    PyModule_AddObject(module, "PI5", Py_BuildValue("i", PIN_PI5));
    PyModule_AddObject(module, "PI6", Py_BuildValue("i", PIN_PI6));
    PyModule_AddObject(module, "PI7", Py_BuildValue("i", PIN_PI7));
    PyModule_AddObject(module, "PI8", Py_BuildValue("i", PIN_PI8));
    PyModule_AddObject(module, "PI9", Py_BuildValue("i", PIN_PI9));
    // CSI0/TS
    PyModule_AddObject(module, "PE4", Py_BuildValue("i", PIN_PE4));
    PyModule_AddObject(module, "PE5", Py_BuildValue("i", PIN_PE5));
    PyModule_AddObject(module, "PE6", Py_BuildValue("i", PIN_PE6));
    PyModule_AddObject(module, "PE7", Py_BuildValue("i", PIN_PE7));
    PyModule_AddObject(module, "PE8", Py_BuildValue("i", PIN_PE8));
    PyModule_AddObject(module, "PE9", Py_BuildValue("i", PIN_PE9));
    PyModule_AddObject(module, "PE10", Py_BuildValue("i", PIN_PE10));
    PyModule_AddObject(module, "PE11", Py_BuildValue("i", PIN_PE11));


    if(Py_AtExit(sunxi_gpio_cleanup) != 0){
        
        sunxi_gpio_cleanup();
        
#if PY_MAJOR_VERSION >= 3
        return NULL;
#else
        return;
#endif
    }



}

