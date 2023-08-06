/*
# This file is part of PyORTHPOL.
#
# PyORTHPOL is free software: you can redistribute it and/or modify
# it under the terms of the LGNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyORTHPOL is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# LGNU Lesser General Public License for more details.
#
# You should have received a copy of the LGNU Lesser General Public License
# along with PyORTHPOL.  If not, see <http://www.gnu.org/licenses/>.
#
# DTU UQ Library
# Copyright (C) 2014 The Technical University of Denmark
# Scientific Computing Section
# Department of Applied Mathematics and Computer Science
#
# Author: Daniele Bigoni
*/

#include <Python.h>
#include <numpy/ndarrayobject.h>
#include <numpy/ndarraytypes.h>

#include <ORTHPOLxx/ORTHPOLPP.hpp>

static PyObject *ORTHPOLError;

/* Auxiliary functions declarations */
double *pyvector_to_Carrayptrs(PyArrayObject *arrayin);
int  not_doublevector(PyArrayObject *vec);

/* ORTHPOL functions declaration */
static PyObject* Py_r1mach (PyObject *self, PyObject *args);
static PyObject* Py_d1mach (PyObject *self, PyObject *args);
static PyObject* Py_dcheb  (PyObject *self, PyObject *args);
static PyObject* Py_dchri  (PyObject *self, PyObject *args);
static PyObject* Py_dgauss (PyObject *self, PyObject *args);
static PyObject* Py_dgchri (PyObject *self, PyObject *args);
static PyObject* Py_dlancz (PyObject *self, PyObject *args);
static PyObject* Py_dlob   (PyObject *self, PyObject *args);
static PyObject* Py_dmcheb (PyObject *self, PyObject *args);
static PyObject* Py_dmcdis (PyObject *self, PyObject *args);
static PyObject* Py_dradau (PyObject *self, PyObject *args);
static PyObject* Py_drecur (PyObject *self, PyObject *args);
static PyObject* Py_dsti   (PyObject *self, PyObject *args);

/* PyORTHPOL set callback functions declarations */
static PyObject* set_dquad_callback(PyObject *self, PyObject *args);
static PyObject* set_dwf_callback(PyObject *self, PyObject *args);

/* ORTHPOL Python callback functions declarations */
static PyObject *dquad_callback = NULL;
static PyObject *dwf_callback = NULL;

/* C++ callback functions declaration */
void dquad_callback_func(int& n, double* x, double* w, int& i, int& ierr);
double dwf_callback_func(double& x, int& i);

/* PyORTHPOL list of methods definition */
static PyMethodDef ORTHPOLMethods[] = {
  {"r1mach", Py_r1mach, METH_VARARGS, "Retrive single machine precision."},
  {"d1mach", Py_d1mach, METH_VARARGS, "Retrive double machine precision."},
  {"dcheb",  Py_dcheb,  METH_VARARGS, "Use the modified Chebyshev algorithm to compute moment-related coefficients."},
  {"dchri",  Py_dchri,  METH_VARARGS, "Applies the Nonlinear recurrence algorithm for modified measures."},
  {"dgauss", Py_dgauss, METH_VARARGS, "Computes the Gauss quadrature nodes and weights using the recursion coefficients alpha and beta."},
  {"dgchri", Py_dgchri, METH_VARARGS, "Applies the Modified Chebyshev algorithm for modified measures."},
  {"dlancz", Py_dlancz, METH_VARARGS, "Applies the Orthogonal Reduction method."},
  {"dlob",   Py_dlob,   METH_VARARGS, "Computes the Gauss-Lobatto quadrature nodes and weights using the recursion coefficients alpha and beta."},
  {"dmcheb", Py_dmcheb, METH_VARARGS, "Discretized Modified Chebyshev Algorithm."},
  {"dmcdis", Py_dmcdis, METH_VARARGS, "Multiple-Component discretization procedure."},
  {"dradau", Py_dradau,  METH_VARARGS, "Computes the Gauss-Radau quadrature nodes and weights using the recursion coefficients alpha and beta."},
  {"drecur", Py_drecur, METH_VARARGS, "Retrive recursion coefficients for standard polynomial classes."},
  {"dsti",   Py_dsti,   METH_VARARGS, "Applies the Stieltjes procedure."},
  {"set_dquad_callback", set_dquad_callback, METH_VARARGS, "Set the dquad callback function"},
  {"set_dwf_callback", set_dwf_callback, METH_VARARGS, "Set the dwf callback function"},
  {NULL, NULL, 0, NULL}        /* Sentinel */
};

/* Init Package function definition */
PyMODINIT_FUNC
initorthpol(void)
{
    PyObject *m;

    m = Py_InitModule("orthpol", ORTHPOLMethods);
    if (m == NULL)
        return;

    import_array();

    ORTHPOLError = PyErr_NewException("orthpol.error", NULL, NULL);
    Py_INCREF(ORTHPOLError);
    PyModule_AddObject(m, "error", ORTHPOLError);

    // Set callbacks functions for orthpol package
    orthpol::set_dquad_callback(dquad_callback_func);
    orthpol::set_dwf_callback(dwf_callback_func);
}

/* ORTHPOL functions definitions */
static PyObject *
Py_r1mach(PyObject *self, PyObject *args)
{
  int I;
  float result;

  if (!PyArg_ParseTuple(args, "i", &I))
    return NULL;
    
  result = orthpol::r1mach(I);
  return Py_BuildValue("f",result);
}

static PyObject *
Py_d1mach(PyObject *self, PyObject *args)
{
  int I;
  double result;

  if (!PyArg_ParseTuple(args, "i", &I))
    return NULL;
    
  result = orthpol::d1mach(I);
  return Py_BuildValue("d",result);
}

static PyObject *
Py_dcheb(PyObject *self, PyObject *args)
{
  /* VARIABLES */
  // INPUT
  int n;
  PyArrayObject *py_a, *py_b, *py_fnu;
  double *a, *b, *fnu;
  // OUTPUT
  PyArrayObject *py_alpha, *py_beta, *py_s;
  double *alpha, *beta, *s;
  int ierr;
  // INTERNAL
  double *s0, *s1, *s2;
  
  if (!PyArg_ParseTuple(args, "iO!O!O!", &n, &PyArray_Type, &py_a, &PyArray_Type, &py_b, &PyArray_Type, &py_fnu))
    return NULL;
  if (NULL == py_a) return NULL;
  if (NULL == py_b) return NULL;
  if (NULL == py_fnu) return NULL;

  // Check double type
  if (not_doublevector(py_a)) return NULL;
  if (not_doublevector(py_b)) return NULL;
  if (not_doublevector(py_fnu)) return NULL;

  int nd = 1;
  int dims[2];
  dims[0] = n;
  // PyArray to C
  a = pyvector_to_Carrayptrs(py_a);
  b = pyvector_to_Carrayptrs(py_b);
  fnu = pyvector_to_Carrayptrs(py_fnu);
  // Allocate output variables
  py_alpha = (PyArrayObject*) PyArray_FromDims(nd, dims, NPY_DOUBLE);
  py_beta = (PyArrayObject*) PyArray_FromDims(nd, dims, NPY_DOUBLE);
  py_s = (PyArrayObject*) PyArray_FromDims(nd, dims, NPY_DOUBLE);
  alpha = pyvector_to_Carrayptrs(py_alpha);
  beta = pyvector_to_Carrayptrs(py_beta);
  s = pyvector_to_Carrayptrs(py_s);
  // Allocate internal variables
  s0 = new double[n];
  s1 = new double[n];
  s2 = new double[n];
  
  // Call ORTHPOL library function
  orthpol::dcheb(n, a, b, fnu, alpha, beta, s, ierr, s0, s1, s2);

  return Py_BuildValue("OOOi", py_alpha, py_beta, py_s, ierr);
}

static PyObject *
Py_dchri(PyObject *self, PyObject *args)
{
  /* VARIABLES */
  // INPUT
  int n;
  int iopt;
  PyArrayObject *py_a, *py_b;
  double *a, *b;
  double x, y, hr, hi;
  // OUTPUT
  PyArrayObject *py_alpha, *py_beta;
  double *alpha, *beta;
  int ierr;
  
  if (!PyArg_ParseTuple(args, "iiO!O!dddd", &n, &iopt, &PyArray_Type, &py_a, &PyArray_Type, &py_b, &x, &y, &hr, &hi))
    return NULL;
  if (NULL == py_a) return NULL;
  if (NULL == py_b) return NULL;

  // Check double type
  if (not_doublevector(py_a)) return NULL;
  if (not_doublevector(py_b)) return NULL;

  int nd = 1;
  int dims[2];
  dims[0] = n;
  // PyArray to C
  a = pyvector_to_Carrayptrs(py_a);
  b = pyvector_to_Carrayptrs(py_b);
  // Allocate output variables
  py_alpha = (PyArrayObject*) PyArray_FromDims(nd, dims, NPY_DOUBLE);
  py_beta = (PyArrayObject*) PyArray_FromDims(nd, dims, NPY_DOUBLE);
  alpha = pyvector_to_Carrayptrs(py_alpha);
  beta = pyvector_to_Carrayptrs(py_beta);
  
  // Call ORTHPOL library function
  orthpol::dchri(n, iopt, a, b, x, y, hr, hi, alpha, beta, ierr);

  return Py_BuildValue("OOi", py_alpha, py_beta, ierr);
}

static PyObject *
Py_dgauss(PyObject *self, PyObject *args)
{
  /* VARIABLES */
  // INPUT
  int n;
  PyArrayObject *py_a, *py_b;
  double *a, *b;
  double eps;
  // OUTPUT
  PyArrayObject *py_zero, *py_weight;
  double *zero, *weight;
  int ierr;
  // INTERNAL
  double *e;
  
  if (!PyArg_ParseTuple(args, "iO!O!d", &n, &PyArray_Type, &py_a, &PyArray_Type, &py_b, &eps))
    return NULL;
  if (NULL == py_a) return NULL;
  if (NULL == py_b) return NULL;

  // Check double type
  if (not_doublevector(py_a)) return NULL;
  if (not_doublevector(py_b)) return NULL;

  int nd = 1;
  int dims[2];
  dims[0] = n;
  // PyArray to C
  a = pyvector_to_Carrayptrs(py_a);
  b = pyvector_to_Carrayptrs(py_b);
  // Allocate output variables
  py_zero = (PyArrayObject*) PyArray_FromDims(nd, dims, NPY_DOUBLE);
  py_weight = (PyArrayObject*) PyArray_FromDims(nd, dims, NPY_DOUBLE);
  zero = pyvector_to_Carrayptrs(py_zero);
  weight = pyvector_to_Carrayptrs(py_weight);
  // Allocate internal variables
  e = new double[n];
  
  // Call ORTHPOL library function
  orthpol::dgauss(n, a, b, eps, zero, weight, ierr, e);

  return Py_BuildValue("OOi", py_zero, py_weight, ierr);
}

static PyObject *
Py_dgchri(PyObject *self, PyObject *args)
{
  /* VARIABLES */
  // INPUT
  int n;
  int iopt;
  int nu0;
  int numax;
  double eps;
  PyArrayObject *py_a, *py_b;
  double *a, *b;
  double x, y;
  // OUTPUT
  PyArrayObject *py_alpha, *py_beta;
  double *alpha, *beta;
  int nu;
  int ierr;
  int ierrc;
  // INTERNAL
  double *fnu;
  double *s;
  double *s0;
  double *s1;
  double *s2;
  
  if (!PyArg_ParseTuple(args, "iiiidO!O!dd", &n, &iopt, &nu0, &numax, &eps, &PyArray_Type, &py_a, &PyArray_Type, &py_b, &x, &y))
    return NULL;
  if (NULL == py_a) return NULL;
  if (NULL == py_b) return NULL;

  // Check double type
  if (not_doublevector(py_a)) return NULL;
  if (not_doublevector(py_b)) return NULL;

  int nd = 1;
  int dims[2];
  dims[0] = n;
  // PyArray to C
  a = pyvector_to_Carrayptrs(py_a);
  b = pyvector_to_Carrayptrs(py_b);
  // Allocate output variables
  py_alpha = (PyArrayObject*) PyArray_FromDims(nd, dims, NPY_DOUBLE);
  py_beta = (PyArrayObject*) PyArray_FromDims(nd, dims, NPY_DOUBLE);
  alpha = pyvector_to_Carrayptrs(py_alpha);
  beta = pyvector_to_Carrayptrs(py_beta);
  // Allocate internal variables
  fnu = new double[2*n];
  s = new double[n];
  s0 = new double[2*n];
  s1 = new double[2*n];
  s2 = new double[2*n];

  
  // Call ORTHPOL library function
  orthpol::dgchri(n, iopt, nu0, numax, eps, a, b, x, y, alpha, beta, nu, ierr, ierrc, fnu, s, s0, s1, s2);

  return Py_BuildValue("OOiii", py_alpha, py_beta, nu, ierr, ierrc);
}

static PyObject *
Py_dlancz(PyObject *self, PyObject *args)
{
  /* VARIABLES */
  // INPUT
  int n;
  int ncap;
  PyArrayObject *py_x, *py_y;
  double *x, *y;
  // OUTPUT
  PyArrayObject *py_alpha, *py_beta;
  double *alpha, *beta;
  int ierr;
  // INTERNAL
  double *p0;
  double *p1;
  
  if (!PyArg_ParseTuple(args, "iiO!O!", &n, &ncap, &PyArray_Type, &py_x, &PyArray_Type, &py_y))
    return NULL;
  if (NULL == py_x) return NULL;
  if (NULL == py_y) return NULL;

  // Check double type
  if (not_doublevector(py_x)) return NULL;
  if (not_doublevector(py_y)) return NULL;

  int nd = 1;
  int dims[2];
  dims[0] = n;
  // PyArray to C
  x = pyvector_to_Carrayptrs(py_x);
  y = pyvector_to_Carrayptrs(py_y);
  // Allocate output variables
  py_alpha = (PyArrayObject*) PyArray_FromDims(nd, dims, NPY_DOUBLE);
  py_beta = (PyArrayObject*) PyArray_FromDims(nd, dims, NPY_DOUBLE);
  alpha = pyvector_to_Carrayptrs(py_alpha);
  beta = pyvector_to_Carrayptrs(py_beta);
  // Allocate internal variables
  p0 = new double[ncap];
  p1 = new double[ncap];
  
  // Call ORTHPOL library function
  orthpol::dlancz(n, ncap, x, y, alpha, beta, ierr, p0, p1);

  return Py_BuildValue("OOi", py_alpha, py_beta, ierr);
}

static PyObject *
Py_dlob(PyObject *self, PyObject *args)
{
  /* VARIABLES */
  // INPUT
  int n;
  PyArrayObject *py_alpha, *py_beta;
  double *alpha, *beta;
  double aleft, right;
  // OUTPUT
  PyArrayObject *py_zero, *py_weight;
  double *zero, *weight;
  int ierr;
  // INTERNAL
  double *e;
  double *a;
  double *b;
  
  if (!PyArg_ParseTuple(args, "iO!O!dd", &n, &PyArray_Type, &py_alpha, &PyArray_Type, &py_beta, &aleft, &right))
    return NULL;
  if (NULL == py_alpha) return NULL;
  if (NULL == py_beta) return NULL;

  // Check double type
  if (not_doublevector(py_alpha)) return NULL;
  if (not_doublevector(py_beta)) return NULL;

  int nd = 1;
  int dims[2];
  dims[0] = n+2;
  // PyArray to C
  alpha = pyvector_to_Carrayptrs(py_alpha);
  beta = pyvector_to_Carrayptrs(py_beta);
  // Allocate output variables
  py_zero = (PyArrayObject*) PyArray_FromDims(nd, dims, NPY_DOUBLE);
  py_weight = (PyArrayObject*) PyArray_FromDims(nd, dims, NPY_DOUBLE);
  zero = pyvector_to_Carrayptrs(py_zero);
  weight = pyvector_to_Carrayptrs(py_weight);
  // Allocate internal variables
  e = new double[n+2];
  a = new double[n+2];
  b = new double[n+2];
  
  // Call ORTHPOL library function
  orthpol::dlob(n, alpha, beta, aleft, right, zero, weight, ierr, e, a, b);

  return Py_BuildValue("OOi", py_zero, py_weight, ierr);
}

static PyObject *
Py_dmcheb(PyObject *self, PyObject *args)
{
  /* VARIABLES */
  // INPUT
  int n, ncapm, mc, mp;
  PyArrayObject *py_xp, *py_yp;
  double *xp, *yp;
  PyObject *py_callback_func;
  double eps;
  int iq, idelta;
  int finl, finr;
  PyArrayObject *py_endl, *py_endr;
  double *endl, *endr;
  PyArrayObject *py_a, *py_b, *py_fnu;
  double *a, *b, *fnu;
  // OUTPUT
  PyArrayObject *py_alpha, *py_beta;
  double *alpha, *beta;
  int ncap, kount, ierr;
  // INTERNAL
  double *xfer, *wfer;
  double *be, *x, *w, *xm, *wm, *s, *s0, *s1, *s2;
  
  if (!PyArg_ParseTuple(args, "iiiiO!O!O!diiiiO!O!O!O!O!", &n, &ncapm, &mc, &mp, 
			&PyArray_Type, &py_xp, 
			&PyArray_Type, &py_yp,
			&py_callback_func,
			&eps, &iq, &idelta, &finl, &finr,
			&PyArray_Type, &py_endl, 
			&PyArray_Type, &py_endr, 
			&PyArray_Type, &py_a, 
			&PyArray_Type, &py_b, 
			&PyArray_Type, &py_fnu))
    return NULL;
  if (NULL == py_xp) return NULL;
  if (NULL == py_yp) return NULL;
  if (NULL == py_callback_func) return NULL;
  if (NULL == py_endl) return NULL;
  if (NULL == py_endr) return NULL;
  if (NULL == py_a) return NULL;
  if (NULL == py_b) return NULL;
  if (NULL == py_fnu) return NULL;

  // Check double type
  if (not_doublevector(py_xp)) return NULL;
  if (not_doublevector(py_yp)) return NULL;
  if (!PyCallable_Check(py_callback_func)) {
    PyErr_SetString(PyExc_TypeError, "Parameter must be callable");
    return NULL;
  }
  if (not_doublevector(py_endl)) return NULL;
  if (not_doublevector(py_endr)) return NULL;
  if (not_doublevector(py_a)) return NULL;
  if (not_doublevector(py_b)) return NULL;
  if (not_doublevector(py_fnu)) return NULL;

  int nd = 1;
  int dims[2];
  dims[0] = n;
  // Set callback functions
  if (iq == 1) set_dquad_callback(self,Py_BuildValue("(O)",py_callback_func));
  else set_dwf_callback(self,Py_BuildValue("(O)",py_callback_func));
  // PyArray to C
  xp = pyvector_to_Carrayptrs(py_xp);
  yp = pyvector_to_Carrayptrs(py_yp);
  endl = pyvector_to_Carrayptrs(py_endl);
  endr = pyvector_to_Carrayptrs(py_endr);
  a = pyvector_to_Carrayptrs(py_a);
  b = pyvector_to_Carrayptrs(py_b);
  fnu = pyvector_to_Carrayptrs(py_fnu);
  // Allocate output variables
  py_alpha = (PyArrayObject*) PyArray_FromDims(nd, dims, NPY_DOUBLE);
  py_beta = (PyArrayObject*) PyArray_FromDims(nd, dims, NPY_DOUBLE);
  alpha = pyvector_to_Carrayptrs(py_alpha);
  beta = pyvector_to_Carrayptrs(py_beta);
  // Allocate internal variables
  xfer = new double[ncapm];
  wfer = new double[ncapm];
  be = new double[n];
  x = new double[ncapm];
  w = new double[ncapm];
  xm = new double[mc*ncapm+mp];
  wm = new double[mc*ncapm+mp];
  s = new double[mc*ncapm+mp];
  s0 = new double[mc*ncapm+mp];
  s1 = new double[mc*ncapm+mp];
  s2 = new double[mc*ncapm+mp];
  
  // Call ORTHPOL library function
  orthpol::dmcheb(n, ncapm, mc, mp, xp, yp, eps, iq, idelta, finl, finr, endl, endr, xfer, wfer, a, b, fnu, alpha, beta, ncap, kount, ierr, be, x, w, xm, wm, s, s0, s1, s2);

  return Py_BuildValue("OOiii", py_alpha, py_beta, ncap, kount, ierr);
}

static PyObject *
Py_dmcdis(PyObject *self, PyObject *args)
{
  /* VARIABLES */
  // INPUT
  int n, ncapm, mc, mp;
  PyArrayObject *py_xp, *py_yp;
  double *xp, *yp;
  PyObject *py_callback_func;
  double eps;
  int iq, idelta, irout;
  int finl, finr;
  PyArrayObject *py_endl, *py_endr;
  double *endl, *endr;
  // OUTPUT
  PyArrayObject *py_alpha, *py_beta;
  double *alpha, *beta;
  int ncap, kount, ierr, ie;
  // INTERNAL
  double *xfer, *wfer;
  double *be, *x, *w, *xm, *wm, *p0, *p1, *p2;
  
  if (!PyArg_ParseTuple(args, "iiiiO!O!OdiiiiiO!O!", 
			&n, &ncapm, &mc, &mp, 
			&PyArray_Type, &py_xp, 
			&PyArray_Type, &py_yp,
			&py_callback_func,
			&eps, &iq, &idelta, &irout, &finl, &finr,
			&PyArray_Type, &py_endl, 
			&PyArray_Type, &py_endr))			
    return NULL;
  if (NULL == py_xp) return NULL;
  if (NULL == py_yp) return NULL;
  if (NULL == py_callback_func) return NULL;
  if (NULL == py_endl) return NULL;
  if (NULL == py_endr) return NULL;

  // Check double type
  if (not_doublevector(py_xp)) return NULL;
  if (not_doublevector(py_yp)) return NULL;
  if (!PyCallable_Check(py_callback_func)) {
    PyErr_SetString(PyExc_TypeError, "Parameter must be callable");
    return NULL;
  }
  if (not_doublevector(py_endl)) return NULL;
  if (not_doublevector(py_endr)) return NULL;

  int nd = 1;
  int dims[2];
  dims[0] = n;
  // Set callback functions
  if (iq == 1) set_dquad_callback(self,Py_BuildValue("(O)",py_callback_func));
  else set_dwf_callback(self,Py_BuildValue("(O)",py_callback_func));
  // PyArray to C
  xp = pyvector_to_Carrayptrs(py_xp);
  yp = pyvector_to_Carrayptrs(py_yp);
  endl = pyvector_to_Carrayptrs(py_endl);
  endr = pyvector_to_Carrayptrs(py_endr);
  // Allocate output variables
  py_alpha = (PyArrayObject*) PyArray_FromDims(nd, dims, NPY_DOUBLE);
  py_beta = (PyArrayObject*) PyArray_FromDims(nd, dims, NPY_DOUBLE);
  alpha = pyvector_to_Carrayptrs(py_alpha);
  beta = pyvector_to_Carrayptrs(py_beta);
  // Allocate internal variables
  xfer = new double[ncapm];
  wfer = new double[ncapm];
  be = new double[n];
  x = new double[ncapm];
  w = new double[ncapm];
  xm = new double[mc*ncapm+mp];
  wm = new double[mc*ncapm+mp];
  p0 = new double[mc*ncapm+mp];
  p1 = new double[mc*ncapm+mp];
  p2 = new double[mc*ncapm+mp];
  
  // Call ORTHPOL library function
  orthpol::dmcdis(n, ncapm, mc, mp, xp, yp, eps, iq, idelta, irout, finl, finr, endl, endr, xfer, wfer, alpha, beta, ncap, kount, ierr, ie, be, x, w, xm, wm, p0, p1, p2);

  return Py_BuildValue("OOiiii", py_alpha, py_beta, ncap, kount, ierr, ie);
}

static PyObject *
Py_dradau(PyObject *self, PyObject *args)
{
  /* VARIABLES */
  // INPUT
  int n;
  PyArrayObject *py_alpha, *py_beta;
  double *alpha, *beta;
  double end;
  // OUTPUT
  PyArrayObject *py_zero, *py_weight;
  double *zero, *weight;
  int ierr;
  // INTERNAL
  double *e;
  double *a;
  double *b;
  
  if (!PyArg_ParseTuple(args, "iO!O!d", &n, &PyArray_Type, &py_alpha, &PyArray_Type, &py_beta, &end))
    return NULL;
  if (NULL == py_alpha) return NULL;
  if (NULL == py_beta) return NULL;

  // Check double type
  if (not_doublevector(py_alpha)) return NULL;
  if (not_doublevector(py_beta)) return NULL;

  int nd = 1;
  int dims[2];
  dims[0] = n+2;
  // PyArray to C
  alpha = pyvector_to_Carrayptrs(py_alpha);
  beta = pyvector_to_Carrayptrs(py_beta);
  // Allocate output variables
  py_zero = (PyArrayObject*) PyArray_FromDims(nd, dims, NPY_DOUBLE);
  py_weight = (PyArrayObject*) PyArray_FromDims(nd, dims, NPY_DOUBLE);
  zero = pyvector_to_Carrayptrs(py_zero);
  weight = pyvector_to_Carrayptrs(py_weight);
  // Allocate internal variables
  e = new double[n+2];
  a = new double[n+2];
  b = new double[n+2];
  
  // Call ORTHPOL library function
  orthpol::dradau(n, alpha, beta, end, zero, weight, ierr, e, a, b);

  return Py_BuildValue("OOi", py_zero, py_weight, ierr);
}

static PyObject *
Py_drecur(PyObject *self, PyObject *args)
{
  // INPUT
  int n;
  int ipoly;
  double al;
  double be;
  double *a, *b;
  PyArrayObject *alpha, *beta;
  
  if (!PyArg_ParseTuple(args, "iidd", &n, &ipoly, &al, &be))
    return NULL;

  // OUTPUT
  int nd = 1;
  int dims[2];
  dims[0] = n;
  alpha = (PyArrayObject*) PyArray_FromDims(nd, dims, NPY_DOUBLE);
  beta = (PyArrayObject*) PyArray_FromDims(nd, dims, NPY_DOUBLE);
  a = pyvector_to_Carrayptrs(alpha);
  b = pyvector_to_Carrayptrs(beta);
  int ierr;
  
  orthpol::drecur(n, ipoly, al, be, a, b, ierr);

  return Py_BuildValue("OOi", alpha, beta, ierr);
}

static PyObject *
Py_dsti(PyObject *self, PyObject *args)
{
  /* VARIABLES */
  // INPUT
  int n;
  int ncap;
  PyArrayObject *py_x, *py_y;
  double *x, *y;
  // OUTPUT
  PyArrayObject *py_alpha, *py_beta;
  double *alpha, *beta;
  int ierr;
  // INTERNAL
  double *p0;
  double *p1;
  double *p2;
  
  if (!PyArg_ParseTuple(args, "iiO!O!", &n, &ncap, &PyArray_Type, &py_x, &PyArray_Type, &py_y))
    return NULL;
  if (NULL == py_x) return NULL;
  if (NULL == py_y) return NULL;

  // Check double type
  if (not_doublevector(py_x)) return NULL;
  if (not_doublevector(py_y)) return NULL;

  int nd = 1;
  int dims[2];
  dims[0] = n;
  // PyArray to C
  x = pyvector_to_Carrayptrs(py_x);
  y = pyvector_to_Carrayptrs(py_y);
  // Allocate output variables
  py_alpha = (PyArrayObject*) PyArray_FromDims(nd, dims, NPY_DOUBLE);
  py_beta = (PyArrayObject*) PyArray_FromDims(nd, dims, NPY_DOUBLE);
  alpha = pyvector_to_Carrayptrs(py_alpha);
  beta = pyvector_to_Carrayptrs(py_beta);
  // Allocate internal variables
  p0 = new double[ncap];
  p1 = new double[ncap];
  p2 = new double[ncap];
  
  // Call ORTHPOL library function
  orthpol::dsti(n, ncap, x, y, alpha, beta, ierr, p0, p1, p2);

  return Py_BuildValue("OOi", py_alpha, py_beta, ierr);
}

/* Auxiliary functions declarations */

/* ==== Create 1D Carray from PyArray ======================
     Assumes PyArray is contiguous in memory.             */
double *pyvector_to_Carrayptrs(PyArrayObject *arrayin)  {
  return (double *) arrayin->data;  /* pointer to arrayin data as double */
}

/* ==== Check that PyArrayObject is a double (Float) type and a vector ==============
   return 1 if an error and raise exception */ 
int  not_doublevector(PyArrayObject *vec)  {
  if (vec->descr->type_num != NPY_DOUBLE || vec->nd != 1)  {
    PyErr_SetString(PyExc_ValueError,
		    "In not_doublevector: array must be of type Float and 1 dimensional (n).");
    return 1;  }
  return 0;
}

/* PyORTHPOL set callback functions declarations */
static PyObject* set_dquad_callback(PyObject *self, PyObject *args)
{
    PyObject *result = NULL;
    PyObject *temp;

    if (PyArg_ParseTuple(args, "O:set_callback", &temp)) {
      if (!PyCallable_Check(temp)) {
	PyErr_SetString(PyExc_TypeError, "parameter must be callable");
	return NULL;
      }
      Py_XINCREF(temp);         /* Add a reference to new callback */
      Py_XDECREF(dquad_callback);  /* Dispose of previous callback */
      dquad_callback = temp;       /* Remember new callback */
      /* Boilerplate to return "None" */
      Py_INCREF(Py_None);
      result = Py_None;
    }

    return result;
}

static PyObject* set_dwf_callback(PyObject *self, PyObject *args)
{
    PyObject *result = NULL;
    PyObject *temp;

    if (PyArg_ParseTuple(args, "O:set_callback", &temp)) {
      if (!PyCallable_Check(temp)) {
	PyErr_SetString(PyExc_TypeError, "parameter must be callable");
	return NULL;
      }
      Py_XINCREF(temp);         /* Add a reference to new callback */
      Py_XDECREF(dwf_callback);  /* Dispose of previous callback */
      dwf_callback = temp;       /* Remember new callback */
      /* Boilerplate to return "None" */
      Py_INCREF(Py_None);
      result = Py_None;
    }

    return result;
}

/* ORTHPOL FORTRAN callback functions definitions */
void dquad_callback_func(int& n, double* x, double* w, int& i, int& ierr){
  PyObject *arglist;
  PyObject *returnlist;

  // INPUT args to Python callback function
  // n, i

  // OUTPUT args from Python callback function
  PyArrayObject *py_x, *py_w;

  // Prepare input arglist
  arglist = Py_BuildValue("ii", n, i);

  // Run Python callback function
  returnlist = PyObject_CallObject(dquad_callback, arglist);

  if (returnlist == NULL) {
    PyErr_SetString(PyExc_TypeError, "Null value returned by user defined function.");
    return;
  }

  // Retrive output and set values
  if (!PyArg_ParseTuple(returnlist, "O!O!i", 
			&PyArray_Type, &py_x, 
			&PyArray_Type, &py_w, 
			&ierr))
    return ;
  if (NULL == py_x) return ;
  if (NULL == py_w) return ;
  // Check double type
  if (not_doublevector(py_x)) return ;
  if (not_doublevector(py_w)) return ;
  // Set FORTRAN x,w
  memcpy(x,pyvector_to_Carrayptrs(py_x),n*sizeof(double));
  memcpy(w,pyvector_to_Carrayptrs(py_w),n*sizeof(double));
}

double dwf_callback_func(double& x, int& i){
  PyObject *arglist = NULL;
  PyObject *returnlist = NULL;

  // OUTPUT args from Python callback function
  double w;

  // Prepare input arglist
  arglist = Py_BuildValue("di", x, i);

  // Run Python callback function
  returnlist = PyObject_CallObject(dwf_callback, arglist);
  Py_DECREF(arglist);

  // int dummy;
  // Retrive output and set values
  if (returnlist == NULL) {
    PyErr_SetString(PyExc_TypeError, "Null value returned by user defined function.");
    return NULL;
  }
  if (!PyArg_ParseTuple(Py_BuildValue("(O)",returnlist), "d", &w)){
    PyErr_SetString(PyExc_TypeError, "Wrong type returned by user defined function.");
    return NULL;
  }
  Py_DECREF(returnlist);

  // RETURN
  return w;
}
