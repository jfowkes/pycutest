"""
C source code of the CUTEst problem interface
"""
__all__ = ['itf_c_source']

# Because we dont want backslashes to be interpreted as escape characters, the string must be a raw string.
itf_c_source = r"""
/* CUTEst problem interface to Python and NumPy */
/* (c)2011 Arpad Buermen */
/* (c)2022 Jaroslav Fowkes, Lindon Roberts */
/* Licensed under GNU GPL V3 */

/* Unused CUTEst tools - sparse finite element matrices and banded matrices
     cdimse
     ceh
     csgreh
     ubandh
     udimse
     ueh
     ugreh

   CUTEst tools that are not used because they duplicate functionality or are obsolete
     cnames		... used pbname, varnames, connames
     udimen		... used cdimen
     ufn		... used uofg
     unames		... used pbname, varnames
     cscfg		... obsolete
     cscifg		... obsolete
*/
#define NPY_NO_DEPRECATED_API NPY_1_20_API_VERSION

#include <Python.h>
#include <cutest.h>
#include <numpy/arrayobject.h>
#include <math.h>
#include <stdio.h>


/* Module function prototypes */
static PyObject *cutest_dims(PyObject *self, PyObject *args);
static PyObject *cutest_setup(PyObject *self, PyObject *args);
static PyObject *cutest_varnames(PyObject *self, PyObject *args);
static PyObject *cutest_connames(PyObject *self, PyObject *args);
static PyObject *cutest_objcons(PyObject *self, PyObject *args);
static PyObject *cutest_obj(PyObject *self, PyObject *args);
static PyObject *cutest_grad(PyObject *self, PyObject *args);
static PyObject *cutest_cons(PyObject *self, PyObject *args);
static PyObject *cutest_lag(PyObject *self, PyObject *args);
static PyObject *cutest_lagjac(PyObject *self, PyObject *args);
static PyObject *cutest_jprod(PyObject *self, PyObject *args);
static PyObject *cutest_hess(PyObject *self, PyObject *args);
static PyObject *cutest_ihess(PyObject *self, PyObject *args);
static PyObject *cutest_hprod(PyObject *self, PyObject *args);
static PyObject *cutest_gradhess(PyObject *self, PyObject *args);
static PyObject *cutest_scons(PyObject *self, PyObject *args);
static PyObject *cutest_slagjac(PyObject *self, PyObject *args);
static PyObject *cutest_sphess(PyObject *self, PyObject *args);
static PyObject *cutest_isphess(PyObject *self, PyObject *args);
static PyObject *cutest_gradsphess(PyObject *self, PyObject *args);
static PyObject *cutest_report(PyObject *self, PyObject *args);
static PyObject *cutest_terminate(PyObject *self, PyObject *args);
/* CUTEst 2.2 function prototypes */
#ifdef CUTEST_VERSION
static PyObject *cutest_hessjohn(PyObject *self, PyObject *args);
static PyObject *cutest_hjprod(PyObject *self, PyObject *args);
static PyObject *cutest_sphessjohn(PyObject *self, PyObject *args);
static PyObject *cutest_shoprod(PyObject *self, PyObject *args);
#endif

/* Module global variables */
#define STR_LEN 10
static npy_int status = 0;              /* output status */
static npy_int CUTEst_nvar = 0;         /* number of variables */
static npy_int CUTEst_ncon = 0;         /* number of constraints */
static npy_int CUTEst_nnzj = 0;         /* nnz in Jacobian */
static npy_int CUTEst_nnzh = 0;         /* nnz in upper triangular Hessian */
static char CUTEst_probName[STR_LEN+1]; /* problem name */
static char setupCalled = 0;            /* Flag to indicate if setup was called */
static char dataFileOpen = 0;           /* Flag to indicate if OUTSDIF is open */

static npy_int funit = 42;              /* FORTRAN unit number for OUTSDIF.d */
static npy_int iout = 6;                /* FORTRAN unit number for error output */
static npy_int io_buffer = 11;          /* FORTRAN unit number for internal input/output */
static char  fName[] = "OUTSDIF.d";     /* Data file name */

/* Logical constants for FORTRAN calls */
static logical somethingFalse = FALSE_, somethingTrue = TRUE_;


/* Module helper functions */

/* Open data file, return 0 on error. */
int open_datafile(void) {
    npy_int  ioErr;					/* Exit flag from OPEN and CLOSE */

    ioErr = 0;
    if (! dataFileOpen)
        FORTRAN_open((integer *)&funit, fName, (integer *)&ioErr);
    if (ioErr) {
        PyErr_SetString(PyExc_Exception, "Failed to open data file");
        return 0;
    }
    dataFileOpen = 1;
    return 1;
}

/* Close data file, return 0 on error. */
int close_datafile(void) {
    npy_int ioErr;					/* Exit flag from OPEN and CLOSE */
    ioErr = 0;
    FORTRAN_close((integer *)&funit, (integer *)&ioErr);
    if (ioErr) {
        PyErr_SetString(PyExc_Exception, "Error closing data file");
        return 0;
    }
    dataFileOpen = 0;
    return 1;
}

/* Check if the problem is set up, return 0 if it is not. */
int check_setup(void) {
    if (!setupCalled) {
        PyErr_SetString(PyExc_Exception, "Problem is not set up");
        return 0;
    }
    return 1;
}

/* Trim trailing spaces from a string starting at index n. */
void trim_string(char *s, int n) {
    int i;

    for(i=n;i>=0;i--) {
        if (s[i]!=' ')
            break;
    }
    s[i+1]=0;
}

/* Decrease reference count for newly created dictionary members */
PyObject *decRefDict(PyObject *dict) {
    PyObject *key, *value;
    Py_ssize_t pos;
    pos=0;
    while (PyDict_Next(dict, &pos, &key, &value)) {
        Py_XDECREF(value);
    }
    return dict;
}

/* Extract sparse gradient and Jacobian in form of NumPy arrays */
void extract_sparse_gradient_jacobian(npy_int nnzjplusno, npy_int *sji, npy_int *sjfi, npy_double *sjv,
        PyArrayObject **Mgi, PyArrayObject **Mgv, PyArrayObject **MJi, PyArrayObject **MJfi, PyArrayObject **MJv) {
    npy_double *gv, *Jv;
    npy_int *gi, *Ji, *Jfi, nnzg, i, jg, jj;
    npy_intp dims[1];

    /* Get number of nonzeros in gradient vector */
    nnzg=0;
    for(i=0;i<nnzjplusno;i++) {
        if (sjfi[i]==0)
            nnzg++;
    }

    /* Alocate and fill objective/Lagrangian gradient data and Jacobian data,
       convert indices from FORTRAN to C. */
    dims[0]=nnzg;
    *Mgi=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_INT);
    *Mgv=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
    gi=(npy_int *)PyArray_DATA(*Mgi);
    gv=(npy_double *)PyArray_DATA(*Mgv);
    dims[0]=nnzjplusno-nnzg;
    *MJi=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_INT);
    *MJfi=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_INT);
    *MJv=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
    Ji=(npy_int *)PyArray_DATA(*MJi);
    Jfi=(npy_int *)PyArray_DATA(*MJfi);
    Jv=(npy_double *)PyArray_DATA(*MJv);
    jg=0;
    jj=0;
    for(i=0;i<nnzjplusno;i++) {
        if (sjfi[i]==0) {
            gi[jg]=sji[i]-1;
            gv[jg]=sjv[i];
            jg++;
        } else {
            Ji[jj]=sji[i]-1;
            Jfi[jj]=sjfi[i]-1;
            Jv[jj]=sjv[i];
            jj++;
        }
    }
}

/* Extract sparse Hessian in form of NumPy arrays
   from sparse ijv format of Hessian's upper triangle + diagonal.
   Add elements to lower triangle. */
void extract_sparse_hessian(npy_int nnzho, npy_int *si, npy_int *sj, npy_double *sv,
                    PyArrayObject **MHi, PyArrayObject **MHj, PyArrayObject **MHv) {
    npy_int *Hi, *Hj, nnzdiag, i, j;
    npy_double *Hv;
    npy_intp dims[1];


    /* Get number of nonzeros on the diagonal */
    nnzdiag=0;
    for(i=0;i<nnzho;i++) {
        if (si[i]==sj[i])
            nnzdiag++;
    }

    /* Alocate and fill objective/Lagrangian gradient data and Jacobian data,
       convert indices from FORTRAN to C, fill lower triangle. */
    dims[0]=2*nnzho-nnzdiag; /* Do not duplicate diagonal elements */
    *MHi=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_INT);
    *MHj=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_INT);
    *MHv=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
    Hi=(npy_int *)PyArray_DATA(*MHi);
    Hj=(npy_int *)PyArray_DATA(*MHj);
    Hv=(npy_double *)PyArray_DATA(*MHv);
    j=0;
    for(i=0;i<nnzho;i++) {
        Hi[j]=si[i]-1;
        Hj[j]=sj[i]-1;
        Hv[j]=sv[i];
        j++;
        if (si[i]!=sj[i]) {
            Hi[j]=sj[i]-1;
            Hj[j]=si[i]-1;
            Hv[j]=sv[i];
            j++;
        }
    }
}


/* Module Python Functions */

PyDoc_STRVAR(cutest_dims_doc,
"Returns the dimension of the problem and the number of constraints.\n"
"\n"
"(n, m)=dims()\n"
"\n"
"Output\n"
"n -- number of variables\n"
"m -- number of constraints\n"
"\n"
"This function is not supposed to be called by the user. It is called by the\n"
"__init__.py script when the test function interface is loaded.\n"
"If you decide to call it anyway, the working directory at the time of call\n"
"must be the one where the file OUTSIF.d can be found.\n"
"\n"
"CUTEst tools used: CUTEST_cdimen\n"
);

static PyObject *cutest_dims(PyObject *self, PyObject *args) {
    if (PyObject_Length(args)!=0)
        PyErr_SetString(PyExc_Exception, "dims() takes no arguments");

    if (!open_datafile())
        return NULL;

    CUTEST_cdimen((integer *)&status, (integer *)&funit, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon);

    return Py_BuildValue("ii", CUTEst_nvar, CUTEst_ncon);
}


PyDoc_STRVAR(cutest_setup_doc,
"Sets up the problem.\n"
"\n"
"data=setup(efirst, lfirst, nvfirst)\n"
"\n"
"Input\n"
"efirst  -- if True, equation constraints are ordered before inequations.\n"
"           Defaults to False.\n"
"lfirst  -- if True, linear constraints are ordered before nonlinear ones.\n"
"           Defaults to False.\n"
"nvfirst -- if True, nonlinear variables are ordered before linear ones.\n"
"           Defaults to False.\n"
"\n"
"Setting both efirst and lfirst to True results in the following ordering:\n"
"linear equations, followed by linear inequations, nonlinear equations,\n"
"and finally nonlinear inequations.\n"
"\n"
"Output\n"
"data -- dictionary with the summary of test function's properties\n"
"\n"
"The problem data dictionary has the following members:\n"
"name    -- problem name\n"
"n       -- number of variables\n"
"m       -- number of constraints (excluding bounds)\n"
"x       -- initial point (1D array of length n)\n"
"bl      -- vector of lower bounds on variables (1D array of length n)\n"
"bu      -- vector of upper bounds on variables (1D array of length n)\n"
"nnzh    -- number of nonzero elements in the diagonal and upper triangle of\n"
"           sparse Hessian\n"
"vartype -- 1D integer array of length n storing variable type\n"
"           0=real,  1=boolean (0 or 1), 2=integer\n"
"\n"
"For constrained problems the following additional members are available\n"
"nnzj    -- number of nonzero elements in sparse Jacobian of constraints\n"
"v       -- initial value of Lagrange multipliers (1D array of length m)\n"
"cl      -- lower bounds on constraint functions (1D array of length m)\n"
"cu      -- upper bounds on constraint functions (1D array of length m)\n"
"equatn  -- 1D boolean array of length m indicating whether a constraint\n"
"           is an equation constraint\n"
"linear  -- 1D boolean array of length m indicating whether a constraint\n"
"           is a linear constraint\n"
"\n"
"-1e+20 and 1e+20 in bl, bu, cl, and cu stand for -infinity and +infinity.\n"
"\n"
"This function must be called before any other CUTEst function is called.\n"
"The only exception is the dims() function.\n"
"\n"
"This function is not supposed to be called by the user. It is called by the\n"
"__init__.py script when the test function interface is loaded.\n"
"If you decide to call it anyway, the working directory at the time of call\n"
"must be the one where the file OUTSIF.d can be found.\n"
"\n"
"CUTEst tools used: CUTEST_cdimen, CUTEST_csetup, CUTEST_usetup, CUTEST_cvartype, CUTEST_uvartype, \n"
"                  CUTEST_cdimsh, CUTEST_udimsh, CUTEST_cdimsj, CUTEST_probname\n"
);

static PyObject *cutest_setup(PyObject *self, PyObject *args) {
    npy_bool  efirst = FALSE_, lfirst = FALSE_, nvfrst = FALSE_;
    int eFirst, lFirst, nvFirst;
    PyObject *dict;
    PyArrayObject *Mx, *Mbl, *Mbu, *Mv=NULL, *Mcl=NULL, *Mcu=NULL, *Meq=NULL, *Mlinear=NULL;
    PyArrayObject *Mvt;
    doublereal *x, *bl, *bu, *v=NULL, *cl=NULL, *cu=NULL;
    npy_int *vartypes;
    npy_bool *equatn=NULL, *linear=NULL;
    npy_intp dims[1];
    int i;

    if (PyObject_Length(args)!=0 && PyObject_Length(args)!=3) {
        PyErr_SetString(PyExc_Exception, "setup() takes 0 or 3 arguments");
        return NULL;
    }

    if (PyObject_Length(args)==3) {
        if (!PyArg_ParseTuple(args, "iii", &eFirst, &lFirst, &nvFirst)) {
            return NULL;
        }

        efirst = eFirst  ? TRUE_ : FALSE_;
        lfirst = lFirst  ? TRUE_ : FALSE_;
        nvfrst = nvFirst ? TRUE_ : FALSE_;
    }

    if (!open_datafile())
        return NULL;

    CUTEST_cdimen((integer *)&status, (integer *)&funit, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon);

    /* Numpy arrays */
    dims[0]=CUTEst_nvar;
    Mx=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
    Mbl=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
    Mbu=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
    Mvt=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_INT);
    if (CUTEst_ncon>0) {
        dims[0]=CUTEst_ncon;
        Mv=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
        Mcl=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
        Mcu=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
        Meq=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_BOOL);
        Mlinear=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_BOOL);
    }

    /* Get internal data buffers */
    /* Assume that npy_double is equivalent to double and npy_int is equivalent to integer */
    x = (npy_double *)PyArray_DATA(Mx);
    bl = (npy_double *)PyArray_DATA(Mbl);
    bu = (npy_double *)PyArray_DATA(Mbu);
    if (CUTEst_ncon>0) {
        v = (npy_double *)PyArray_DATA(Mv);
        cl = (npy_double *)PyArray_DATA(Mcl);
        cu = (npy_double *)PyArray_DATA(Mcu);

        /* Create temporary CUTEst logical arrays */
        equatn = (npy_bool *)malloc(CUTEst_ncon*sizeof(npy_bool));
        linear = (npy_bool *)malloc(CUTEst_ncon*sizeof(npy_bool));
    }
    vartypes=(npy_int *)malloc(CUTEst_nvar*sizeof(npy_int));

    if (CUTEst_ncon > 0)
        CUTEST_csetup((integer *)&status, (integer *)&funit, (integer *)&iout, (integer *)&io_buffer, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, x, bl, bu,
                v, cl, cu, (logical *)equatn, (logical *)linear,
                (integer *)&efirst, (integer *)&lfirst, (integer *)&nvfrst);
    else
        CUTEST_usetup((integer *)&status, (integer *)&funit, (integer *)&iout, (integer *)&io_buffer, (integer *)&CUTEst_nvar, x, bl, bu);

    if (CUTEst_ncon > 0)
        CUTEST_cvartype((integer *)&status, (integer *)&CUTEst_nvar, (integer *)vartypes);
    else
        CUTEST_uvartype((integer *)&status, (integer *)&CUTEst_nvar, (integer *)vartypes);

    /* Copy logical values to NumPy bool arrays and free temporary storage */
    if (CUTEst_ncon > 0) {
        for(i=0; i<CUTEst_ncon; i++) {
            *((npy_bool*)(PyArray_GETPTR1(Meq, i)))=equatn[i];
            *((npy_bool*)(PyArray_GETPTR1(Mlinear, i)))=linear[i];
        }
        free(equatn);
        free(linear);
    }

    /* Copy variable types to NumPy integer arrays and free temporary storage */
    for(i=0; i<CUTEst_nvar; i++) {
        *((npy_int*)PyArray_GETPTR1(Mvt, i))=vartypes[i];
    }
    free(vartypes);

    if (CUTEst_ncon>0)
        CUTEST_cdimsh((integer *)&status, (integer *)&CUTEst_nnzh);
    else
        CUTEST_udimsh((integer *)&status, (integer *)&CUTEst_nnzh);

    if (CUTEst_ncon > 0) {
        CUTEST_cdimsj((integer *)&status, (integer *)&CUTEst_nnzj);
        CUTEst_nnzj -= CUTEst_nvar;
    }

    CUTEST_probname((integer *)&status, CUTEst_probName);
    trim_string(CUTEst_probName, STR_LEN-1);

    close_datafile();

    dict=PyDict_New();
    PyDict_SetItemString(dict, "n", PyLong_FromLong((long)CUTEst_nvar));
    PyDict_SetItemString(dict, "m", PyLong_FromLong((long)CUTEst_ncon));
    PyDict_SetItemString(dict, "nnzh", PyLong_FromLong((long)CUTEst_nnzh));
    PyDict_SetItemString(dict, "x", (PyObject *)Mx);
    PyDict_SetItemString(dict, "bl", (PyObject *)Mbl);
    PyDict_SetItemString(dict, "bu", (PyObject *)Mbu);
    PyDict_SetItemString(dict, "name", PyUnicode_FromString(CUTEst_probName));
    PyDict_SetItemString(dict, "vartype", (PyObject *)Mvt);
    if (CUTEst_ncon > 0) {
        PyDict_SetItemString(dict, "nnzj", PyLong_FromLong((long)CUTEst_nnzj));
        PyDict_SetItemString(dict, "v", (PyObject*)Mv);
        PyDict_SetItemString(dict, "cl", (PyObject*)Mcl);
        PyDict_SetItemString(dict, "cu", (PyObject*)Mcu);
        PyDict_SetItemString(dict, "equatn", (PyObject*)Meq);
        PyDict_SetItemString(dict, "linear", (PyObject*)Mlinear);
    }

    setupCalled = 1;

    return decRefDict(dict);
}


PyDoc_STRVAR(cutest_varnames_doc,
"Returns the names of variables in the problem.\n"
"\n"
"namelist=varnames()\n"
"\n"
"Output\n"
"namelist -- list of length n holding strings holding names of variables\n"
"\n"
"The list reflects the ordering imposed by the nvfirst argument to setup().\n"
"\n"
"This function is not supposed to be called by the user. It is called by the\n"
"__init__.py script when the test function interface is loaded.\n"
"\n"
"CUTEst tools used: CUTEST_varnames\n"
);

static PyObject *cutest_varnames(PyObject *self, PyObject *args) {
    char *Fvnames, Fvname[STR_LEN+1], *ptr;
    PyObject *list;
    int i, j;

    if (!check_setup())
        return NULL;

    if (PyObject_Length(args)!=0) {
        PyErr_SetString(PyExc_Exception, "varnames() takes 0 arguments");
        return NULL;
    }

    Fvnames=(char *)malloc(CUTEst_nvar*STR_LEN*sizeof(char));
    list=PyList_New(0);

    CUTEST_varnames((integer *)&status, (integer *)&CUTEst_nvar, Fvnames);

    for(i=0;i<CUTEst_nvar;i++) {
        ptr=Fvnames+i*STR_LEN;
        for(j=0;j<STR_LEN;j++) {
            Fvname[j]=*ptr;
            ptr++;
        }
        trim_string(Fvname, STR_LEN-1);
        PyList_Append(list, PyUnicode_FromString(Fvname));
    }

    free(Fvnames);

    return list;
}


PyDoc_STRVAR(cutest_connames_doc,
"Returns the names of constraints in the problem.\n"
"\n"
"namelist=connames()\n"
"\n"
"Output\n"
"namelist -- list of length m holding strings holding names of constraints\n"
"\n"
"The list is ordered in the way specified by efirst and lfirst arguments to\n"
"setup().\n"
"\n"
"This function is not supposed to be called by the user. It is called by the\n"
"__init__.py script when the test function interface is loaded.\n"
"\n"
"CUTEst tools used: CUTEST_connames\n"
);

static PyObject *cutest_connames(PyObject *self, PyObject *args) {
    char *Fcnames, Fcname[STR_LEN+1], *ptr;
    PyObject *list;
    int i, j;

    if (!check_setup())
        return NULL;

    if (PyObject_Length(args)!=0) {
        PyErr_SetString(PyExc_Exception, "connames() takes 0 arguments");
        return NULL;
    }

    list=PyList_New(0);

    if (CUTEst_ncon>0) {

        Fcnames=(char *)malloc(CUTEst_ncon*STR_LEN*sizeof(char));

        CUTEST_connames((integer *)&status, (integer *)&CUTEst_ncon, Fcnames);

        for(i=0;i<CUTEst_ncon;i++) {
            ptr=Fcnames+i*STR_LEN;
            for(j=0;j<STR_LEN;j++) {
                Fcname[j]=*ptr;
                ptr++;
            }
            trim_string(Fcname, STR_LEN-1);
            PyList_Append(list, PyUnicode_FromString(Fcname));
        }

        free(Fcnames);
    }

    return list;
}


PyDoc_STRVAR(cutest_objcons_doc,
"Returns the value of objective and constraints at x.\n"
"\n"
"(f, c)=objcons(x)\n"
"\n"
"Input\n"
"x -- 1D array of length n with the values of variables\n"
"\n"
"Output\n"
"f -- float holding the value of the function at x\n"
"c -- 1D array of length m holding the values of constraints at x\n"
"\n"
"CUTEst tools used: CUTEST_cfn\n"
);

static PyObject *cutest_objcons(PyObject *self, PyObject *args) {
    PyArrayObject *arg1, *Mc;
    doublereal *x, *c;
    doublereal f;
    npy_intp dims[1];

    if (!check_setup())
        return NULL;

    if (!PyArg_ParseTuple(args, "O", &arg1))
        return NULL;

    /* Check if x is double and of correct length and shape */
    if (!(PyArray_Check(arg1) && PyArray_ISFLOAT(arg1)&& PyArray_TYPE(arg1)==NPY_DOUBLE && PyArray_NDIM(arg1)==1 && PyArray_DIM(arg1, 0)==CUTEst_nvar)) {
        PyErr_SetString(PyExc_Exception, "Argument 1 must be a 1D double array of length nvar");
        return NULL;
    }

    x=(npy_double *)PyArray_DATA(arg1);
    dims[0]=CUTEst_ncon;
    Mc=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
    c=(npy_double *)PyArray_DATA(Mc);

    CUTEST_cfn((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, x, &f, c);

    return Py_BuildValue("dO", f, Mc);
}


PyDoc_STRVAR(cutest_obj_doc,
"Returns the value of objective and its gradient at x.\n"
"\n"
"f=obj(x)\n"
"(f, g)=obj(x, gradFlag)\n"
"\n"
"Input\n"
"x        -- 1D array of length n with the values of variables\n"
"gradFlag -- if given the function returns f and g; can be anything\n"
"\n"
"Output\n"
"f -- float holding the value of the function at x\n"
"g -- 1D array of length n holding the value of the gradient of f at x\n"
"\n"
"CUTEst tools used: CUTEST_uofg, CUTEST_cofg\n"
);

static PyObject *cutest_obj(PyObject *self, PyObject *args) {
    PyArrayObject *arg1;
    PyObject *arg2;
    PyArrayObject *Mg=NULL;
    doublereal *x, *g=NULL;
    doublereal f;
    npy_intp dims[1];

    if (!check_setup())
        return NULL;

    if (!PyArg_ParseTuple(args, "O|O", &arg1, &arg2))
        return NULL;

    /* Check if x is double and of correct length and shape */
    if (!(PyArray_Check(arg1) && PyArray_ISFLOAT(arg1) && PyArray_TYPE(arg1)==NPY_DOUBLE && PyArray_NDIM(arg1)==1 && PyArray_DIM(arg1, 0)==CUTEst_nvar)) {
        PyErr_SetString(PyExc_Exception, "Argument 1 must be a 1D double array of length nvar");
        return NULL;
    }

    x=(npy_double *)PyArray_DATA(arg1);
    if (PyObject_Length(args)>1) {
        dims[0]=CUTEst_nvar;
        Mg=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
        g=(npy_double *)PyArray_DATA(Mg);
    }

    if (CUTEst_ncon == 0) {
        if (PyObject_Length(args)==1) {
            CUTEST_uofg((integer *)&status, (integer *)&CUTEst_nvar, x, &f, NULL, &somethingFalse);
            return Py_BuildValue("d", f);
        } else {
            CUTEST_uofg((integer *)&status, (integer *)&CUTEst_nvar, x, &f, g, &somethingTrue);
            return Py_BuildValue("dO", f, Mg);
        }
    } else {
        if (PyObject_Length(args)==1) {
            CUTEST_cofg((integer *)&status, (integer *)&CUTEst_nvar, x, &f, NULL, &somethingFalse);
            return Py_BuildValue("d", f);
        } else {
            CUTEST_cofg((integer *)&status, (integer *)&CUTEst_nvar, x, &f, g, &somethingTrue);
            return Py_BuildValue("dO", f, Mg);
        }
    }
}


PyDoc_STRVAR(cutest_grad_doc,
"Returns the gradient of the objective or gradient of the i-th constraint at x.\n"
"\n"
"g=grad(x)   -- objective gradient\n"       
"g=grad(x,i) -- i-th constraint gradient\n"
"\n"
"Input\n"
"x -- 1D array of length n with the values of variables\n"
"i -- integer index of constraint (between 0 and m-1)\n"
"\n"
"Output\n"
"g -- 1D array of length n holding the value of the gradient at x\n"
"\n"
"CUTEst tools used: CUTEST_ugr, CUTEST_cigr\n"
);

static PyObject *cutest_grad(PyObject *self, PyObject *args) {
    PyArrayObject *arg1;
    PyArrayObject *Mg=NULL;
    doublereal *x, *g=NULL;
    int index;
    npy_int icon;
    npy_intp dims[1];

    if (!check_setup())
        return NULL;

    if (!PyArg_ParseTuple(args, "O|i", &arg1, &index))
        return NULL;

    /* Check if x is double and of correct length and shape */
    if (!(PyArray_Check(arg1) && PyArray_ISFLOAT(arg1) && PyArray_TYPE(arg1)==NPY_DOUBLE && PyArray_NDIM(arg1)==1 && PyArray_DIM(arg1, 0)==CUTEst_nvar)) {
        PyErr_SetString(PyExc_Exception, "Argument 1 must be a 1D double array of length nvar");
        return NULL;
    }

    /* Check index */
    if (PyObject_Length(args)>1) {
        if (index<0 || index>=CUTEst_ncon) {
            PyErr_SetString(PyExc_Exception, "Argument 2 must be between 0 and ncon-1");
            return NULL;
        }
        icon=index+1;
    } else {
        icon=0;
    }

    x=(npy_double *)PyArray_DATA(arg1);
    dims[0]=CUTEst_nvar;
    Mg=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
    g=(npy_double *)PyArray_DATA(Mg);

    if (CUTEst_ncon == 0) {
        CUTEST_ugr((integer *)&status, (integer *)&CUTEst_nvar, x, g);
        return Py_BuildValue("O", Mg);
    } else {
        CUTEST_cigr((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&icon, x, g);
        return Py_BuildValue("O", Mg);
    }
}


PyDoc_STRVAR(cutest_cons_doc,
"Returns the value of constraints and the Jacobian of constraints at x.\n"
"\n"
"c=cons(x)                 -- constraints\n"
"ci=cons(x, False, i)      -- i-th constraint\n"
"(c, J)=cons(x, True)      -- Jacobian of constraints\n"
"(ci, Ji)=cons(x, True, i) -- i-th constraint and its gradient\n"
"\n"
"Input\n"
"x -- 1D array of length n with the values of variables\n"
"i -- integer index of constraint (between 0 and m-1)\n"
"\n"
"Output\n"
"c  -- 1D array of length m holding the values of constraints at x\n"
"ci -- 1D array of length 1 holding the value of i-th constraint at x\n"
"J  -- 2D array with m rows of n columns holding Jacobian of constraints at x\n"
"Ji -- 1D array of length n holding the gradient of i-th constraint\n"
"      (also equal to the i-th row of Jacobian)\n"
"\n"
"CUTEst tools used: CUTEST_ccfg, CUTEST_ccifg\n"
);

static PyObject *cutest_cons(PyObject *self, PyObject *args) {
    PyArrayObject *arg1, *Mc, *MJ;
    PyObject *arg2;
    doublereal *x, *c, *J;
    int derivs, index, wantSingle;
    npy_int icon;
    npy_int zero = 0;
    npy_intp dims[2];

    if (!check_setup())
        return NULL;

    arg2=NULL;
    if (!PyArg_ParseTuple(args, "O|Oi", &arg1, &arg2, &index))
        return NULL;

    /* Check if x is double and of correct length and shape */
    if (!(PyArray_Check(arg1) && PyArray_ISFLOAT(arg1) && PyArray_TYPE(arg1)==NPY_DOUBLE && PyArray_NDIM(arg1)==1 && PyArray_DIM(arg1, 0)==CUTEst_nvar)) {
        PyErr_SetString(PyExc_Exception, "Argument 1 must be a 1D double array of length nvar");
        return NULL;
    }

    /* Do we want derivatives */
    if (arg2!=NULL && arg2==Py_True)
        derivs=1;
    else
        derivs=0;

    /* Do we want a particular derivative */
    if (PyObject_Length(args)==3) {
        /* Check index */
        if (index<0 || index>=CUTEst_ncon) {
            PyErr_SetString(PyExc_Exception, "Argument 3 must be an integer between 0 and ncon-1");
            return NULL;
        }
        icon=index+1;
        wantSingle=1;
    } else {
        wantSingle=0;
    }

    x=(npy_double *)PyArray_DATA(arg1);
    if (!wantSingle) {
        dims[0]=CUTEst_ncon;
        Mc=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
        c=(npy_double *)PyArray_DATA(Mc);
        if (derivs) {
            dims[0]=CUTEst_ncon;
            dims[1]=CUTEst_nvar;
            /* Create a FORTRAN style array (first index stride is 1) */
            MJ=(PyArrayObject *)PyArray_New(&PyArray_Type, 2, dims, NPY_DOUBLE, NULL, NULL, 0, NPY_ARRAY_F_CONTIGUOUS, NULL);
            J=(npy_double *)PyArray_DATA(MJ);
        }
    } else {
        dims[0]=1;
        Mc=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
        c=(npy_double *)PyArray_DATA(Mc);
        if (derivs) {
            dims[0]=CUTEst_nvar;
            MJ=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
            J=(npy_double *)PyArray_DATA(MJ);
        }
    }

    if (!wantSingle) {
        if (!derivs) {
            CUTEST_ccfg((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, x, c,
                    &somethingFalse, (integer *)&zero, (integer *)&zero, NULL, &somethingFalse);
            return (PyObject *)Mc;
        } else {
            CUTEST_ccfg((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, x, c,
                    &somethingFalse, (integer *)&CUTEst_ncon, (integer *)&CUTEst_nvar, J,
                    &somethingTrue);
            return Py_BuildValue("OO", Mc, MJ);
        }
    } else {
        if (!derivs) {
            CUTEST_ccifg((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&icon, x, c, NULL, &somethingFalse);
            return (PyObject *)Mc;
        } else {
            CUTEST_ccifg((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&icon, x, c, J, &somethingTrue);
            return Py_BuildValue("OO", Mc, MJ);
        }
    }
}


PyDoc_STRVAR(cutest_lag_doc,
"Returns the Lagrangian function value and its gradient if requested at x.\n"
"The gradient is the gradient with respect to the problem variables (has n components).\n"
"\n"
"l=lag(x, v)                -- Lagrangian function value\n"
"(l, g)=lag(x, v, gradFlag) -- Lagrangian function value and the Lagrangian gradient\n"
"\n"
"Input\n"
"x        -- 1D array of length n with the values of variables\n"
"v        -- 1D array of length m with the Lagrange multipliers\n"
"gradFlag -- if given the function returns l and g; can be anything\n"
"\n"
"Output\n"
"l -- float holding the value of the Lagrangian function at x\n"
"g -- 1D array of length n holding the Lagrangian gradient at x\n"
"\n"
"CUTEst tools used: CUTEST_clfg\n"
);

static PyObject *cutest_lag(PyObject *self, PyObject *args) {
    PyArrayObject *arg1, *arg2, *Mg=NULL;
    PyObject *arg3;
    doublereal *x, *v, *g=NULL;
    doublereal f;
    npy_intp dims[1];

    if (!check_setup())
        return NULL;

    if (!PyArg_ParseTuple(args, "OO|O", &arg1, &arg2, &arg3))
        return NULL;

    /* Check if x is double and of correct length and shape */
    if (!(PyArray_Check(arg1) && PyArray_ISFLOAT(arg1) && PyArray_TYPE(arg1)==NPY_DOUBLE && PyArray_NDIM(arg1)==1 && PyArray_DIM(arg1, 0)==CUTEst_nvar)) {
        PyErr_SetString(PyExc_Exception, "Argument 1 must be a 1D double array of length nvar");
        return NULL;
    }

    /* Check if v is double and of correct length and shape */
    if (!(PyArray_Check(arg2) && PyArray_ISFLOAT(arg2) && PyArray_TYPE(arg2)==NPY_DOUBLE && PyArray_NDIM(arg2)==1 && PyArray_DIM(arg2, 0)==CUTEst_ncon)) {
        PyErr_SetString(PyExc_Exception, "Argument 2 must be a 1D double array of length ncon");
        return NULL;
    }

    x=(npy_double *)PyArray_DATA(arg1);
    v=(npy_double *)PyArray_DATA(arg2);
    if (PyObject_Length(args)>2) {
        dims[0]=CUTEst_nvar;
        Mg=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
        g=(npy_double *)PyArray_DATA(Mg);
    }

    if (PyObject_Length(args)==2) {
        CUTEST_clfg((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, x, v, &f, NULL, &somethingFalse);
        return Py_BuildValue("d", f);
    } else {
        CUTEST_clfg((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, x, v, &f, g, &somethingTrue);
        return Py_BuildValue("dO", f, Mg);
    }
}


PyDoc_STRVAR(cutest_lagjac_doc,
"Returns the gradient of the objective or Lagrangian, and the Jacobian of\n"
"constraints at x. The gradient is the gradient with respect to the problem's\n"
"variables (has n components).\n"
"\n"
"(g, J)=lagjac(x)    -- objective gradient and the Jacobian of constraints\n"
"(g, J)=lagjac(x, v) -- Lagrangian gradient and the Jacobian of constraints\n"
"\n"
"Input\n"
"x -- 1D array of length n with the values of variables\n"
"v -- 1D array of length m with the Lagrange multipliers\n"
"\n"
"Output\n"
"g  -- 1D array of length n holding the gradient at x\n"
"J  -- 2D array with m rows of n columns holding Jacobian of constraints at x\n"
"\n"
"CUTEst tools used: CUTEST_cgr\n"
);

static PyObject *cutest_lagjac(PyObject *self, PyObject *args) {
    PyArrayObject *arg1, *arg2, *Mg, *MJ;
    doublereal *x, *v=NULL, *g, *J;
    int lagrangian;
    npy_intp dims[2];

    if (!check_setup())
        return NULL;

    arg2=NULL;
    if (!PyArg_ParseTuple(args, "O|O", &arg1, &arg2))
        return NULL;

    /* Check if x is double and of correct length and shape */
    if (!(PyArray_Check(arg1) && PyArray_ISFLOAT(arg1) && PyArray_TYPE(arg1)==NPY_DOUBLE && PyArray_NDIM(arg1)==1 && PyArray_DIM(arg1, 0)==CUTEst_nvar)) {
        PyErr_SetString(PyExc_Exception, "Argument 1 must be a 1D double array of length nvar");
        return NULL;
    }

    /* Check if v is double and of correct length and shape. */
    if (arg2!=NULL) {
        if (!(PyArray_Check(arg2) && PyArray_ISFLOAT(arg2) && PyArray_TYPE(arg2)==NPY_DOUBLE && PyArray_NDIM(arg2)==1 && PyArray_DIM(arg2, 0)==CUTEst_ncon)) {
            PyErr_SetString(PyExc_Exception, "Argument 2 must be a 1D double array of length ncon");
            return NULL;
        }
        lagrangian=1;
    } else {
        lagrangian=0;
    }

    x=(npy_double *)PyArray_DATA(arg1);
    if (lagrangian)
        v=(npy_double *)PyArray_DATA(arg2);
    dims[0]=CUTEst_nvar;
    Mg=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
    g=(npy_double *)PyArray_DATA(Mg);
    dims[0]=CUTEst_ncon;
    dims[1]=CUTEst_nvar;
    /* Create a FORTRAN style array (first index stride is 1) */
    MJ=(PyArrayObject *)PyArray_New(&PyArray_Type, 2, dims, NPY_DOUBLE, NULL, NULL, 0, NPY_ARRAY_F_CONTIGUOUS, NULL);
    J=(npy_double *)PyArray_DATA(MJ);

    if (!lagrangian) {
        CUTEST_cgr((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, x, NULL, &somethingFalse,
            g, &somethingFalse, (integer *)&CUTEst_ncon, (integer *)&CUTEst_nvar, J);
    } else {
        CUTEST_cgr((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, x, v, &somethingTrue,
            g, &somethingFalse, (integer *)&CUTEst_ncon, (integer *)&CUTEst_nvar, J);
    }

    return Py_BuildValue("OO", Mg, MJ);
}


PyDoc_STRVAR(cutest_jprod_doc,
"Returns the product of constraints Jacobian at x with vector p\n"
"\n"
"r=jprod(transpose, p, x) -- computes Jacobian at x before product calculation\n"
"r=jprod(transpose, p)    -- uses last computed Jacobian\n"
"\n"
"Input\n"
"transpose -- boolean flag indicating that the Jacobian should be transposed\n"
"             before the product is calculated\n"
"p         -- the vector that will be multiplied with the Jacobian\n"
"             1D array of length n (m) if transpose if False (True)\n"
"x         -- 1D array of length n holding the values of variables used in the\n"
"             evaluation of the constraints Jacobian\n"
"\n"
"Output\n"
"r  -- 1D array of length m if transpose=False (or n if transpose=True)\n"
"      with the result\n"
"\n"
"CUTEst tools used: CUTEST_cjprod\n"
);

static PyObject *cutest_jprod(PyObject *self, PyObject *args) {
    PyArrayObject *arg2, *arg3, *Mr;
    PyObject *arg1;
    doublereal *p, *x, *r;
    int transpose;
    npy_intp dims[1];

    if (!check_setup())
        return NULL;

    arg3=NULL;
    if (!PyArg_ParseTuple(args, "OO|O", &arg1, &arg2, &arg3))
        return NULL;

    /* Check if arg1 is True */
    if (arg1==Py_True)
        transpose=1;
    else
        transpose=0;

    /* Check if p is double and of correct dimension */
    if (!(PyArray_Check(arg2) && PyArray_ISFLOAT(arg2) && PyArray_TYPE(arg2)==NPY_DOUBLE && PyArray_NDIM(arg2)==1)) {
        PyErr_SetString(PyExc_Exception, "Argument 2 must be a 1D double array");
        return NULL;
    }

    /* Check length of p when J is not transposed */
    if (!transpose && !(PyArray_DIM(arg2, 0)==CUTEst_nvar)) {
        PyErr_SetString(PyExc_Exception, "Argument 2 must be of length nvar (J is not transposed)");
        return NULL;
    }

    /* Check length of p when J is transposed */
    if (transpose && !(PyArray_DIM(arg2, 0)==CUTEst_ncon)) {
        PyErr_SetString(PyExc_Exception, "Argument 2 must be of length ncon (J is transposed)");
        return NULL;
    }

    /* Check if x is double and of correct length and shape. */
    if (arg3!=NULL) {
        if (!(arg3!=NULL && PyArray_Check(arg3) && PyArray_ISFLOAT(arg3) && PyArray_TYPE(arg3)==NPY_DOUBLE && PyArray_NDIM(arg3)==1 && PyArray_DIM(arg3, 0)==CUTEst_nvar)) {
            PyErr_SetString(PyExc_Exception, "Argument 3 must be a 1D double array of length nvar");
            return NULL;
        }
    }

    p=(npy_double *)PyArray_DATA(arg2);
    if (arg3!=NULL)
        x=(npy_double *)PyArray_DATA(arg3);
    else
        x=NULL;
    if (!transpose) {
        dims[0]=CUTEst_ncon;
    } else {
        dims[0]=CUTEst_nvar;
    }
    Mr=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
    r=(npy_double *)PyArray_DATA(Mr);

    if (!transpose) {
        if (arg3==NULL) {
            CUTEST_cjprod((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, &somethingTrue,
                    &somethingFalse, NULL, p, (integer *)&CUTEst_nvar, r, (integer *)&CUTEst_ncon);
        } else {
            CUTEST_cjprod((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, &somethingFalse,
                    &somethingFalse, x, p, (integer *)&CUTEst_nvar, r, (integer *)&CUTEst_ncon);
        }
    } else {
        if (arg3==NULL) {
            CUTEST_cjprod((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, &somethingTrue,
                    &somethingTrue, NULL, p, (integer *)&CUTEst_ncon, r, (integer *)&CUTEst_nvar);
        } else {
            CUTEST_cjprod((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, &somethingFalse,
                    &somethingTrue, x, p, (integer *)&CUTEst_ncon, r, (integer *)&CUTEst_nvar);
        }
    }

    return (PyObject *)Mr;
}


PyDoc_STRVAR(cutest_hess_doc,
"Returns the Hessian of the objective (for unconstrained problems) or the\n"
"Hessian of the Lagrangian (for constrained problems) at x.\n"
"\n"
"H=hess(x)    -- Hessian of objective at x for unconstrained problems\n"
"H=hess(x, v) -- Hessian of Lagrangian at (x, v) for constrained problems\n"
"\n"
"The first form can only be used for unconstrained problems. The second one\n"
"can only be used for constrained problems. For obtaining the Hessian of the\n"
"objective in case of a constrained problem use ihess().\n"
"\n"
"The Hessian is meant with respect to problem variables (has dimension n).\n"
"\n"
"Input\n"
"x         -- 1D array of length n holding the values of variables\n"
"v         -- 1D array of length m holding the values of Lagrange multipliers\n"
"\n"
"Output\n"
"H  -- 2D array with n rows of n columns holding the Hessian at x (or (x, v))\n"
"\n"
"CUTEst tools used: CUTEST_cdh, CUTEST_udh\n"
);

static PyObject *cutest_hess(PyObject *self, PyObject *args) {
    PyArrayObject *arg1, *arg2, *MH;
    doublereal *x, *v=NULL, *H;
    npy_intp dims[2];

    if (!check_setup())
        return NULL;

    arg2=NULL;
    if (!PyArg_ParseTuple(args, "O|O", &arg1, &arg2))
        return NULL;

    /* Check if x is double and of correct dimension */
    if (!(PyArray_Check(arg1) && PyArray_ISFLOAT(arg1) && PyArray_TYPE(arg1)==NPY_DOUBLE && PyArray_NDIM(arg1)==1 && PyArray_DIM(arg1, 0)==CUTEst_nvar)) {
        PyErr_SetString(PyExc_Exception, "Argument 1 must be a 1D double array of length nvar");
        return NULL;
    }

    if (CUTEst_ncon>0) {
        /* Check if v is double and of correct dimension */
        if (arg2!=NULL) {
            if (!(PyArray_Check(arg2) && PyArray_ISFLOAT(arg2) && PyArray_TYPE(arg2)==NPY_DOUBLE && PyArray_NDIM(arg2)==1 && PyArray_DIM(arg2, 0)==CUTEst_ncon)) {
                PyErr_SetString(PyExc_Exception, "Argument 2 must be a 1D double array of length ncon");
                return NULL;
            }
        } else {
            PyErr_SetString(PyExc_Exception, "Argument 2 must be specified for constrained problems. Use ihess().");
            return NULL;
        }
    }

    x=(npy_double *)PyArray_DATA(arg1);
    if (CUTEst_ncon>0)
        v=(npy_double *)PyArray_DATA(arg2);
    dims[0]=CUTEst_nvar;
    dims[1]=CUTEst_nvar;
    /* Create a FORTRAN style array (first index stride is 1) */
    MH=(PyArrayObject *)PyArray_New(&PyArray_Type, 2, dims, NPY_DOUBLE, NULL, NULL, 0, NPY_ARRAY_F_CONTIGUOUS, NULL);
    H=(npy_double *)PyArray_DATA(MH);

    if (CUTEst_ncon>0) {
        CUTEST_cdh((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, x, v, (integer *)&CUTEst_nvar, H);
    } else {
        CUTEST_udh((integer *)&status, (integer *)&CUTEst_nvar, x, (integer *)&CUTEst_nvar, H);
    }

    return (PyObject *)MH;
}


#ifdef CUTEST_VERSION
PyDoc_STRVAR(cutest_hessjohn_doc,
"Returns the Hessian of the (Fritz) John function at (x, y0, v).\n"
"\n"
"H=hessjohn(x, y0, v) -- Hessian of John function at (x, y0, v) (constrained problems)\n"
"\n"
"The Hessian is meant with respect to problem variables (has dimension n).\n"
"\n"
"Input\n"
"x         -- 1D array of length n holding the values of variables\n"
"y0        -- float holding the John scalar associated with the objective\n"
"v         -- 1D array of length m holding the values of Lagrange multipliers\n"
"\n"
"Output\n"
"H  -- 2D array with n rows of n columns holding the John function Hessian at (x, y0, v))\n"
"\n"
"CUTEst tools used: CUTEST_cdhj\n"
);

static PyObject *cutest_hessjohn(PyObject *self, PyObject *args) {
    PyArrayObject *arg1, *arg3, *MH;
    doublereal *x, *v=NULL, *H;
    doublereal y0;
    npy_intp dims[2];

    if (!check_setup())
        return NULL;

    if (CUTEst_ncon == 0) {
        PyErr_SetString(PyExc_Exception, "Unconstrained problems do not have a (Fritz) John function");
        return NULL;
    }

    if (!PyArg_ParseTuple(args, "OdO", &arg1, &y0, &arg3))
        return NULL;

    /* Check if x is double and of correct dimension */
    if (!(PyArray_Check(arg1) && PyArray_ISFLOAT(arg1) && PyArray_TYPE(arg1)==NPY_DOUBLE && PyArray_NDIM(arg1)==1 && PyArray_DIM(arg1, 0)==CUTEst_nvar)) {
        PyErr_SetString(PyExc_Exception, "Argument 1 must be a 1D double array of length nvar");
        return NULL;
    }

    /* Check if v is double and of correct dimension */
    if (!(PyArray_Check(arg3) && PyArray_ISFLOAT(arg3) && PyArray_TYPE(arg3)==NPY_DOUBLE && PyArray_NDIM(arg3)==1 && PyArray_DIM(arg3, 0)==CUTEst_ncon)) {
        PyErr_SetString(PyExc_Exception, "Argument 3 must be a 1D double array of length ncon");
        return NULL;
    }

    x=(npy_double *)PyArray_DATA(arg1);
    v=(npy_double *)PyArray_DATA(arg3);
    dims[0]=CUTEst_nvar;
    dims[1]=CUTEst_nvar;
    /* Create a FORTRAN style array (first index stride is 1) */
    MH=(PyArrayObject *)PyArray_New(&PyArray_Type, 2, dims, NPY_DOUBLE, NULL, NULL, 0, NPY_ARRAY_F_CONTIGUOUS, NULL);
    H=(npy_double *)PyArray_DATA(MH);

    CUTEST_cdhj((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, x, &y0, v, (integer *)&CUTEst_nvar, H);

    return (PyObject *)MH;
}
#endif


PyDoc_STRVAR(cutest_ihess_doc,
"Returns the Hessian of the objective or the Hessian of i-th constraint at x.\n"
"\n"
"H=ihess(x)    -- Hessian of the objective\n"
"H=ihess(x, i) -- Hessian of i-th constraint\n"
"\n"
"The Hessian is meant with respect to problem variables (has dimension n).\n"
"\n"
"Input\n"
"x -- 1D array of length n holding the values of variables\n"
"i -- integer holding the index of the constraint (between 0 and m-1)\n"
"\n"
"Output\n"
"H  -- 2D array with n rows of n columns holding the Hessian at x\n"
"\n"
"CUTEst tools used: CUTEST_cidh, CUTEST_udh\n"
);

static PyObject *cutest_ihess(PyObject *self, PyObject *args) {
    PyArrayObject *arg1, *MH;
    doublereal *x, *H;
    npy_intp dims[2];
    int i;
    npy_int icon;

    if (!check_setup())
        return NULL;

    if (!PyArg_ParseTuple(args, "O|i", &arg1, &i))
        return NULL;

    if (PyObject_Length(args)>1) {
        icon=i+1;
        if (i<0 || i>=CUTEst_ncon) {
            PyErr_SetString(PyExc_Exception, "Argument 2 must be between 0 and ncon-1");
            return NULL;
        }
    } else {
        icon=0;
    }

    /* Check if x is double and of correct dimension */
    if (!(PyArray_Check(arg1) && PyArray_ISFLOAT(arg1) && PyArray_TYPE(arg1)==NPY_DOUBLE && PyArray_NDIM(arg1)==1 && PyArray_DIM(arg1, 0)==CUTEst_nvar)) {
        PyErr_SetString(PyExc_Exception, "Argument 1 must be a 1D double array of length nvar");
        return NULL;
    }

    x=(npy_double *)PyArray_DATA(arg1);
    dims[0]=CUTEst_nvar;
    dims[1]=CUTEst_nvar;
    /* Create a FORTRAN style array (first index stride is 1) */
    MH=(PyArrayObject *)PyArray_New(&PyArray_Type, 2, dims, NPY_DOUBLE, NULL, NULL, 0, NPY_ARRAY_F_CONTIGUOUS, NULL);
    H=(npy_double *)PyArray_DATA(MH);

    if (CUTEst_ncon>0) {
        CUTEST_cidh((integer *)&status, (integer *)&CUTEst_nvar, x, (integer *)&icon, (integer *)&CUTEst_nvar, H);
    } else {
        CUTEST_udh((integer *)&status, (integer *)&CUTEst_nvar, x, (integer *)&CUTEst_nvar, H);
    }

    return (PyObject *)MH;
}


PyDoc_STRVAR(cutest_hprod_doc,
"Returns the product of Hessian at x and vector p.\n"
"The Hessian is either the Hessian of objective or the Hessian of Lagrangian.\n"
"\n"
"r=hprod(p, x, v) -- use Hessian of Lagrangian at x (constrained problem)\n"
"r=hprod(p, x)    -- use Hessian of objective at x (unconstrained problem)\n"
"r=hprod(p)       -- use last computed Hessian\n"
"\n"
"The first form can only be used for constrained problems. The second one\n"
"can only be used for unconstrained problems.\n"
"\n"
"The Hessian is meant with respect to problem variables (has dimension n).\n"
"\n"
"Input\n"
"p -- 1D array of length n holding the components of the vector\n"
"x -- 1D array of length n holding the values of variables\n"
"v -- 1D array of length m holding the values of Lagrange multipliers\n"
"\n"
"Output\n"
"r  -- 1D array of length n holding the result\n"
"\n"
"CUTEst tools used: CUTEST_chprod, CUTEST_uhprod\n"
);

static PyObject *cutest_hprod(PyObject *self, PyObject *args) {
    PyArrayObject *arg1, *arg2, *arg3, *Mr;
    doublereal *p, *x=NULL, *v=NULL, *r;
    npy_intp dims[1];

    if (!check_setup())
        return NULL;

    arg2=arg3=NULL;
    if (!PyArg_ParseTuple(args, "O|OO", &arg1, &arg2, &arg3))
        return NULL;

    if (CUTEst_ncon>0) {
        if (PyObject_Length(args)==2) {
            PyErr_SetString(PyExc_Exception, "Need 1 or 3 arguments for constrained problems");
            return NULL;
        }
    } else {
        if (PyObject_Length(args)==3) {
            PyErr_SetString(PyExc_Exception, "Need 1 or 2 arguments for unconstrained problems");
            return NULL;
        }
    }

    /* Check if p is double and of correct dimension */
    if (!(PyArray_Check(arg1) && PyArray_ISFLOAT(arg1) && PyArray_TYPE(arg1)==NPY_DOUBLE && PyArray_NDIM(arg1)==1 && PyArray_DIM(arg1, 0)==CUTEst_nvar)) {
        PyErr_SetString(PyExc_Exception, "Argument 1 must be a 1D double array of length nvar");
        return NULL;
    }

    /* Check if x is double and of correct dimension */
    if (arg2!=NULL && !(PyArray_Check(arg2) && PyArray_ISFLOAT(arg2) && PyArray_TYPE(arg2)==NPY_DOUBLE && PyArray_NDIM(arg2)==1 && PyArray_DIM(arg2, 0)==CUTEst_nvar)) {
        PyErr_SetString(PyExc_Exception, "Argument 2 must be a 1D double array of length nvar");
        return NULL;
    }

    /* Check if v is double and of correct dimension */
    if (arg3!=NULL && !(PyArray_Check(arg3) && PyArray_ISFLOAT(arg3) && PyArray_TYPE(arg3)==NPY_DOUBLE && PyArray_NDIM(arg3)==1 && PyArray_DIM(arg3, 0)==CUTEst_ncon)) {
        PyErr_SetString(PyExc_Exception, "Argument 3 must be a 1D double array of length ncon");
        return NULL;
    }

    p=(npy_double *)PyArray_DATA(arg1);
    if (arg2!=NULL)
        x=(npy_double *)PyArray_DATA(arg2);
    if (arg3!=NULL)
        v=(npy_double *)PyArray_DATA(arg3);
    dims[0]=CUTEst_nvar;
    Mr=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
    r=(npy_double *)PyArray_DATA(Mr);

    if (CUTEst_ncon>0) {
        if (arg2==NULL)
            CUTEST_chprod((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, &somethingTrue, NULL, NULL, p, r);
        else
            CUTEST_chprod((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, &somethingFalse, x, v, p, r);
    } else {
        if (arg2==NULL)
            CUTEST_uhprod((integer *)&status, (integer *)&CUTEst_nvar, &somethingTrue, NULL, p, r);
        else
            CUTEST_uhprod((integer *)&status, (integer *)&CUTEst_nvar, &somethingFalse, x, p, r);
    }

    return (PyObject *)Mr;
}


#ifdef CUTEST_VERSION
PyDoc_STRVAR(cutest_hjprod_doc,
"Returns the product of Hessian of the (Fritz) John function at (x,y0,v) and vector p.\n"
"\n"
"r=hprod(p, x, y0, v) -- use Hessian of John function at (x,y0,v) (constrained problem)\n"
"r=hprod(p)           -- use last computed John function Hessian (constrained problem)\n"
"\n"
"The Hessian is meant with respect to problem variables (has dimension n).\n"
"\n"
"Input\n"
"p -- 1D array of length n holding the components of the vector\n"
"x -- 1D array of length n holding the values of variables\n"
"y0 -- float holding the (Fritz) John scalar associated with the objective\n"
"v -- 1D array of length m holding the values of Lagrange multipliers\n"
"\n"
"Output\n"
"r  -- 1D array of length n holding the result\n"
"\n"
"CUTEst tools used: CUTEST_chjprod\n"
);

static PyObject *cutest_hjprod(PyObject *self, PyObject *args) {
    PyArrayObject *arg1, *arg2, *arg4, *Mr;
    doublereal *p, *x=NULL, *v=NULL, *r;
    doublereal y0;
    npy_intp dims[1];

    if (!check_setup())
        return NULL;

    if (CUTEst_ncon == 0) {
        PyErr_SetString(PyExc_Exception, "Unconstrained problems do not have a (Fritz) John function");
        return NULL;
    }

    arg2=arg4=NULL;
    if (!PyArg_ParseTuple(args, "O|OdO", &arg1, &arg2, &y0, &arg4))
        return NULL;

    if (PyObject_Length(args)!=1 && PyObject_Length(args)!=4) {
        PyErr_SetString(PyExc_Exception, "Need 1 or 4 arguments");
        return NULL;
    }

    /* Check if p is double and of correct dimension */
    if (!(PyArray_Check(arg1) && PyArray_ISFLOAT(arg1) && PyArray_TYPE(arg1)==NPY_DOUBLE && PyArray_NDIM(arg1)==1 && PyArray_DIM(arg1, 0)==CUTEst_nvar)) {
        PyErr_SetString(PyExc_Exception, "Argument 1 must be a 1D double array of length nvar");
        return NULL;
    }

    /* Check if x is double and of correct dimension */
    if (arg2!=NULL && !(PyArray_Check(arg2) && PyArray_ISFLOAT(arg2) && PyArray_TYPE(arg2)==NPY_DOUBLE && PyArray_NDIM(arg2)==1 && PyArray_DIM(arg2, 0)==CUTEst_nvar)) {
        PyErr_SetString(PyExc_Exception, "Argument 2 must be a 1D double array of length nvar");
        return NULL;
    }

    /* Check if v is double and of correct dimension */
    if (arg4!=NULL && !(PyArray_Check(arg4) && PyArray_ISFLOAT(arg4) && PyArray_TYPE(arg4)==NPY_DOUBLE && PyArray_NDIM(arg4)==1 && PyArray_DIM(arg4, 0)==CUTEst_ncon)) {
        PyErr_SetString(PyExc_Exception, "Argument 4 must be a 1D double array of length ncon");
        return NULL;
    }

    p=(npy_double *)PyArray_DATA(arg1);
    if (arg2!=NULL)
        x=(npy_double *)PyArray_DATA(arg2);
    if (arg4!=NULL)
        v=(npy_double *)PyArray_DATA(arg4);
    dims[0]=CUTEst_nvar;
    Mr=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
    r=(npy_double *)PyArray_DATA(Mr);

    if (arg2==NULL)
        CUTEST_chjprod((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, &somethingTrue, NULL, &y0, NULL, p, r);
    else
        CUTEST_chjprod((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, &somethingFalse, x, &y0, v, p, r);

    return (PyObject *)Mr;
}
#endif


PyDoc_STRVAR(cutest_gradhess_doc,
"Returns the Hessian of the Lagrangian, the Jacobian of constraints, and the\n"
"gradient of the objective or the gradient of the Lagrangian at x.\n"
"\n"
"(g, H)=gradhess(x)       -- for unconstrained problems\n"
"(g, J, H)=gradhess(x, v, gradl) -- for constrained problems\n"
"\n"
"The first form can only be used for unconstrained problems. The second one\n"
"can only be used for constrained problems.\n"
"\n"
"The Hessian is meant with respect to problem variables (has dimension n).\n"
"\n"
"Input\n"
"x     -- 1D array of length n holding the values of variables\n"
"v     -- 1D array of length m holding the values of Lagrange multipliers\n"
"gradl -- boolean flag. If False the gradient of the objective is returned, \n"
"         if True the gradient of the Lagrangian is returned.\n"
"         Default is False.\n"
"\n"
"Output\n"
"g  -- 1D array of length n holding\n"
"      the gradient of objective at x (for unconstrained problems) or\n"
"      the gradient of Lagrangian at (x, v) (for constrained problems)\n"
"J  -- 2D array with m rows and n columns holding the Jacobian of constraints\n"
"H  -- 2D array with n rows and n columns holding\n"
"      the Hessian of the objective (for unconstrained problems) or\n"
"      the Hessian of the Lagrangian (for constrained problems)\n"
"\n"
"CUTEst tools used: CUTEST_cgrdh, CUTEST_ugrdh\n"
);

static PyObject *cutest_gradhess(PyObject *self, PyObject *args) {
    PyArrayObject *arg1, *arg2, *Mg, *MH, *MJ;
    PyObject *arg3;
    doublereal *x, *v=NULL, *g, *H, *J;
    npy_bool grlagf;
    npy_intp dims[2];

    if (!check_setup())
        return NULL;

    arg2=NULL;
    arg3=NULL;
    if (!PyArg_ParseTuple(args, "O|OO", &arg1, &arg2, &arg3))
        return NULL;

    if (CUTEst_ncon>0) {
        if (PyObject_Length(args)<2) {
            PyErr_SetString(PyExc_Exception, "Need at least 2 arguments for constrained problems");
            return NULL;
        }
    } else {
        if (PyObject_Length(args)!=1) {
            PyErr_SetString(PyExc_Exception, "Need 1 argument for unconstrained problems");
            return NULL;
        }
    }

    /* Check if x is double and of correct dimension */
    if (!(PyArray_Check(arg1) && PyArray_ISFLOAT(arg1) && PyArray_TYPE(arg1)==NPY_DOUBLE && PyArray_NDIM(arg1)==1 && PyArray_DIM(arg1, 0)==CUTEst_nvar)) {
        PyErr_SetString(PyExc_Exception, "Argument 1 must be a 1D double array of length nvar");
        return NULL;
    }

    /* Check if v is double and of correct dimension */
    if (arg2!=NULL && !(PyArray_Check(arg2) && PyArray_ISFLOAT(arg2) && PyArray_TYPE(arg2)==NPY_DOUBLE && PyArray_NDIM(arg2)==1 && PyArray_DIM(arg2, 0)==CUTEst_ncon)) {
        PyErr_SetString(PyExc_Exception, "Argument 2 must be a 1D double array of length ncon");
        return NULL;
    }

    /* Are we computing the gradient of the Lagrangian */
    if (arg3!=NULL && arg3==Py_True) {
        grlagf=TRUE_;
    } else {
        grlagf=FALSE_;
    }

    x=(npy_double *)PyArray_DATA(arg1);
    if (arg2!=NULL)
        v=(npy_double *)PyArray_DATA(arg2);
    dims[0]=CUTEst_nvar;
    Mg=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
    g=(npy_double *)PyArray_DATA(Mg);
    dims[0]=CUTEst_nvar;
    dims[1]=CUTEst_nvar;
    /* Create a FORTRAN style array (first index stride is 1) */
    MH=(PyArrayObject *)PyArray_New(&PyArray_Type, 2, dims, NPY_DOUBLE, NULL, NULL, 0, NPY_ARRAY_F_CONTIGUOUS, NULL);
    H=(npy_double *)PyArray_DATA(MH);
    dims[0]=CUTEst_ncon;
    dims[1]=CUTEst_nvar;
    /* Create a FORTRAN style array (first index stride is 1) */
    MJ=(PyArrayObject *)PyArray_New(&PyArray_Type, 2, dims, NPY_DOUBLE, NULL, NULL, 0, NPY_ARRAY_F_CONTIGUOUS, NULL);
    J=(npy_double *)PyArray_DATA(MJ);

    if (CUTEst_ncon>0) {
        CUTEST_cgrdh((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, x, v, (logical *)&grlagf,
                g, &somethingFalse, (integer *)&CUTEst_ncon, (integer *)&CUTEst_nvar, J, (integer *)&CUTEst_nvar, H);
        return Py_BuildValue("OOO", Mg, MJ, MH);
    } else {
        CUTEST_ugrdh((integer *)&status, (integer *)&CUTEst_nvar, x, g, (integer *)&CUTEst_nvar, H);
        return Py_BuildValue("OO", Mg, MH);
    }
}


PyDoc_STRVAR(cutest_scons_doc,
"Returns the value of constraints and the sparse Jacobian of constraints at x.\n"
"\n"
"(c, Jvi, Jfi, Jv)=scons(x) -- Jacobian of constraints\n"
"(ci, gi, gv)=scons(x, i)   -- i-th constraint and its gradient\n"
"\n"
"Input\n"
"x -- 1D array of length n with the values of variables\n"
"i -- integer index of constraint (between 0 and m-1)\n"
"\n"
"Output\n"
"c   -- 1D array of length m holding the values of constraints at x\n"
"Jvi -- 1D array of integers holding the column indices (0 .. n-1)\n"
"       of nozero elements in sparse Jacobian of constraints\n"
"Jfi -- 1D array of integers holding the row indices (0 .. m-1)\n"
"       of nozero elements in sparse Jacobian of constraints\n"
"Jv  -- 1D array holding the values of nonzero elements in the sparse Jacobian\n"
"       of constraints at x. Has the same length as Jvi and Jfi.\n"
"ci  -- 1D array of length 1 with the value of i-th constraint at x\n"
"gi  -- 1D array of integers holding the indices (0 .. n-1) of nonzero\n"
"       elements in the sparse gradient vector of i-th constraint\n"
"gv  -- 1D array holding the values of nonzero elements in the sparse gradient\n"
"       vector representing the gradient of i-th constraint at x.\n"
"       Has the same length as gi. gi and gv corespond to the i-th row of\n"
"       constraints Jacobian at x.\n"
"\n"
"This function is not supposed to be called by the user. It is called by the\n"
"wrapper function scons().\n"
"\n"
"CUTEst tools used: CUTEST_ccfsg, CUTEST_ccifsg\n"
);

static PyObject *cutest_scons(PyObject *self, PyObject *args) {
    PyArrayObject *arg1, *Mc, *MJi, *MJfi, *MJv, *Mgi, *Mgv;
    doublereal *c, *Jv, *gv, *x, *sv;
    npy_int *Ji, *Jfi, *gi, *si;
    npy_int index, nnzsgc, lj;
    int i;
    npy_intp dims[1];

    if (!check_setup())
        return NULL;

    if (!PyArg_ParseTuple(args, "O|i", &arg1, &i))
        return NULL;

    /* Check if x is double and of correct dimension */
    if (!(PyArray_Check(arg1) && PyArray_ISFLOAT(arg1) && PyArray_TYPE(arg1)==NPY_DOUBLE && PyArray_NDIM(arg1)==1 && PyArray_DIM(arg1, 0)==CUTEst_nvar)) {
        PyErr_SetString(PyExc_Exception, "Argument 1 must be a 1D double array of length nvar");
        return NULL;
    }

    if (PyObject_Length(args)==2) {
        if (i<0 || i>=CUTEst_ncon) {
            PyErr_SetString(PyExc_Exception, "Argument 2 must be an integer between 0 and ncon-1");
            return NULL;
        }
        index=i+1;
    }

    if (PyObject_Length(args)==1) {
        x=(npy_double *)PyArray_DATA(arg1);
        dims[0]=CUTEst_nnzj;
        MJi=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_INT);
        MJfi=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_INT);
        MJv=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
        Ji=(npy_int *)PyArray_DATA(MJi);
        Jfi=(npy_int *)PyArray_DATA(MJfi);
        Jv=(npy_double *)PyArray_DATA(MJv);
        dims[0]=CUTEst_ncon;
        Mc=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
        c=(npy_double *)PyArray_DATA(Mc);
        lj=CUTEst_nnzj;

        CUTEST_ccfsg((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, x, c, (integer *)&CUTEst_nnzj,
              (integer *)&lj, Jv, (integer *)Ji, (integer *)Jfi, &somethingTrue);

        /* Convert FORTRAN indices to C indices */
        for(i=0;i<CUTEst_nnzj;i++) {
            Ji[i]--;
            Jfi[i]--;
        }

        return Py_BuildValue("OOOO", Mc, MJi, MJfi, MJv);
    } else {
        x=(npy_double *)PyArray_DATA(arg1);
        si=(npy_int *)malloc(CUTEst_nvar*sizeof(npy_int));
        sv=(npy_double *)malloc(CUTEst_nvar*sizeof(npy_double));
        dims[0]=1;
        Mc=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
        c=(npy_double *)PyArray_DATA(Mc);

        CUTEST_ccifsg((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&index, x, c, (integer *)&nnzsgc, (integer *)&CUTEst_nvar, sv, (integer *)si, &somethingTrue);

        /* Allocate and copy results, convert indices from FORTRAN to C, free storage */
        dims[0]=nnzsgc;
        Mgi=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_INT);
        Mgv=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
        gi=(npy_int *)PyArray_DATA(Mgi);
        gv=(npy_double *)PyArray_DATA(Mgv);
        for (i=0;i<nnzsgc;i++) {
            gi[i]=si[i]-1;
            gv[i]=sv[i];
        }
        free(si);
        free(sv);

        return Py_BuildValue("OOO", Mc, Mgi, Mgv);
    }
}


PyDoc_STRVAR(cutest_slagjac_doc,
"Returns the sparse gradient of objective at x or Lagrangian at (x, v), \n"
"and the sparse Jacobian of constraints at x.\n"
"\n"
"(gi, gv, Jvi, Jfi, Jv)=slagjac(x)    -- objective gradient and Jacobian\n"
"(gi, gv, Jvi, Jfi, Jv)=slagjac(x, v) -- Lagrangian gradient and Jacobian\n"
"\n"
"Input\n"
"x -- 1D array of length n with the values of variables\n"
"v -- 1D array of length m with the values of Lagrange multipliers\n"
"\n"
"Output\n"
"gi  -- 1D array of integers holding the indices (0 .. n-1) of nonzero\n"
"       elements in the sparse gradient vector\n"
"gv  -- 1D array holding the values of nonzero elements in the sparse gradient\n"
"       vector. Has the same length as gi.\n"
"Jvi -- 1D array of integers holding the column indices (0 .. n-1)\n"
"       of nozero elements in sparse Jacobian of constraints\n"
"Jfi -- 1D array of integers holding the row indices (0 .. m-1)\n"
"       of nozero elements in sparse Jacobian of constraints\n"
"Jv  -- 1D array holding the values of nonzero elements in the sparse Jacobian\n"
"       of constraints at x. Has the same length as Jvi and Jfi.\n"
"\n"
"This function is not supposed to be called by the user. It is called by the\n"
"wrapper function slagjac().\n"
"\n"
"CUTEst tools used: CUTEST_csgr\n"
);

static PyObject *cutest_slagjac(PyObject *self, PyObject *args) {
    PyArrayObject *arg1, *arg2, *Mgi, *Mgv, *MJi, *MJfi, *MJv;
    doublereal *x, *v=NULL, *sv;
    npy_int *si, *sfi;
    npy_int nnzjplusn, nnzjplusno;
    int lagrangian;

    if (!check_setup())
        return NULL;

    arg2=NULL;
    if (!PyArg_ParseTuple(args, "O|O", &arg1, &arg2))
        return NULL;

    /* Check if x is double and of correct length and shape */
    if (!(PyArray_Check(arg1) && PyArray_ISFLOAT(arg1) && PyArray_TYPE(arg1)==NPY_DOUBLE && PyArray_NDIM(arg1)==1 && PyArray_DIM(arg1, 0)==CUTEst_nvar)) {
        PyErr_SetString(PyExc_Exception, "Argument 1 must be a 1D double array of length nvar");
        return NULL;
    }

    /* Check if v is double and of correct length and shape. */
    if (arg2!=NULL) {
        if (!(PyArray_Check(arg2) && PyArray_ISFLOAT(arg2) && PyArray_TYPE(arg2)==NPY_DOUBLE && PyArray_NDIM(arg2)==1 && PyArray_DIM(arg2, 0)==CUTEst_ncon)) {
            PyErr_SetString(PyExc_Exception, "Argument 2 must be a 1D double array of length ncon");
            return NULL;
        }
        lagrangian=1;
    } else {
        lagrangian=0;
    }

    x=(npy_double *)PyArray_DATA(arg1);
    if (lagrangian)
        v=(npy_double *)PyArray_DATA(arg2);
    nnzjplusn=CUTEst_nnzj+CUTEst_nvar;
    si=(npy_int *)malloc(nnzjplusn*sizeof(npy_int));
    sfi=(npy_int *)malloc(nnzjplusn*sizeof(npy_int));
    sv=(npy_double *)malloc(nnzjplusn*sizeof(npy_double));

    /* Must use different variable for output NNZJ and input LCJAC */
    if (!lagrangian) {
        CUTEST_csgr((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, x, NULL, &somethingFalse,
                (integer *)&nnzjplusno, (integer *)&nnzjplusn, sv, (integer *)si, (integer *)sfi);
    } else {
        CUTEST_csgr((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, x, v, &somethingTrue,
                (integer *)&nnzjplusno, (integer *)&nnzjplusn, sv, (integer *)si, (integer *)sfi);
    }

    extract_sparse_gradient_jacobian(nnzjplusno, si, sfi, sv, (PyArrayObject **)&Mgi, (PyArrayObject **)&Mgv, (PyArrayObject **)&MJi, (PyArrayObject **)&MJfi, (PyArrayObject **)&MJv);

    /* Free temporary storage */
    free(si);
    free(sfi);
    free(sv);

    return Py_BuildValue("OOOOO", Mgi, Mgv, MJi, MJfi, MJv);
}


PyDoc_STRVAR(cutest_sphess_doc,
"Returns the sparse Hessian of the objective at x (unconstrained problems) or\n"
"the sparse Hessian of the Lagrangian (constrained problems) at (x, v).\n"
"\n"
"(Hi, Hj, Hv)=sphess(x)    -- Hessian of objective (unconstrained problems)\n"
"(Hi, Hj, Hv)=sphess(x, v) -- Hessian of Lagrangian (constrained problems)\n"
"\n"
"Input\n"
"x -- 1D array of length n with the values of variables\n"
"v -- 1D array of length m with the values of Lagrange multipliers\n"
"\n"
"Output\n"
"Hi -- 1D array of integers holding the row indices (0 .. n-1)\n"
"      of nozero elements in sparse Hessian\n"
"Hj -- 1D array of integers holding the column indices (0 .. n-1)\n"
"      of nozero elements in sparse Hessian\n"
"Hv -- 1D array holding the values of nonzero elements in the sparse Hessian\n"
"      Has the same length as Hi and Hj.\n"
"\n"
"Hi, Hj, and Hv represent the full Hessian and not only the diagonal and the\n"
"upper triangle. To obtain the Hessian of the objective of constrained\n"
"problems use isphess().\n"
"\n"
"This function is not supposed to be called by the user. It is called by the\n"
"wrapper function sphess().\n"
"\n"
"CUTEst tools used: CUTEST_csh, CUTEST_ush\n"
);

static PyObject *cutest_sphess(PyObject *self, PyObject *args) {
    PyArrayObject *arg1, *arg2, *MHi, *MHj, *MHv;
    doublereal *x, *v=NULL, *sv;
    npy_int *si, *sj, nnzho;

    if (!check_setup())
        return NULL;

    arg2=NULL;
    if (!PyArg_ParseTuple(args, "O|O", &arg1, &arg2))
        return NULL;

    /* Check if x is double and of correct dimension */
    if (!(PyArray_Check(arg1) && PyArray_ISFLOAT(arg1) && PyArray_TYPE(arg1)==NPY_DOUBLE && PyArray_NDIM(arg1)==1 && PyArray_DIM(arg1, 0)==CUTEst_nvar)) {
        PyErr_SetString(PyExc_Exception, "Argument 1 must be a 1D double array of length nvar");
        return NULL;
    }

    if (CUTEst_ncon>0) {
        /* Check if v is double and of correct dimension */
        if (arg2!=NULL) {
            if (!(PyArray_Check(arg2) && PyArray_ISFLOAT(arg2) && PyArray_TYPE(arg2)==NPY_DOUBLE && PyArray_NDIM(arg2)==1 && PyArray_DIM(arg2, 0)==CUTEst_ncon)) {
                PyErr_SetString(PyExc_Exception, "Argument 2 must be a 1D double array of length ncon");
                return NULL;
            }
        } else {
            PyErr_SetString(PyExc_Exception, "Argument 2 must be specified for constrained problems. Use isphess().");
            return NULL;
        }
    }

    x=(npy_double *)PyArray_DATA(arg1);
    if (CUTEst_ncon>0)
        v=(npy_double *)PyArray_DATA(arg2);
    si=(npy_int *)malloc(CUTEst_nnzh*sizeof(npy_int));
    sj=(npy_int *)malloc(CUTEst_nnzh*sizeof(npy_int));
    sv=(npy_double *)malloc(CUTEst_nnzh*sizeof(npy_double));

    if (CUTEst_ncon>0) {
        CUTEST_csh((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, x, v, (integer *)&nnzho, (integer *)&CUTEst_nnzh,
            sv, (integer *)si, (integer *)sj);
    } else {
        CUTEST_ush((integer *)&status, (integer *)&CUTEst_nvar, x, (integer *)&nnzho, (integer *)&CUTEst_nnzh,
            sv, (integer *)si, (integer *)sj);
    }

    extract_sparse_hessian(nnzho, si, sj, sv, (PyArrayObject **)&MHi, (PyArrayObject **)&MHj, (PyArrayObject **)&MHv);

    /* Free temporary storage */
    free(si);
    free(sj);
    free(sv);

    return Py_BuildValue("OOO", MHi, MHj, MHv);
}


#ifdef CUTEST_VERSION
PyDoc_STRVAR(cutest_sphessjohn_doc,
"Returns the sparse Hessian of the (Fritz) John function at (x, y0, v).\n"
"\n"
"(Hi, Hj, Hv)=sphessjohn(x, y0, v) -- Hessian of John function (constrained problems)\n"
"\n"
"Input\n"
"x -- 1D array of length n with the values of variables\n"
"y0 -- float holding the (Fritz) John scalar associated with the objective\n"
"v -- 1D array of length m with the values of Lagrange multipliers\n"
"\n"
"Output\n"
"Hi -- 1D array of integers holding the row indices (0 .. n-1)\n"
"      of nozero elements in sparse Hessian\n"
"Hj -- 1D array of integers holding the column indices (0 .. n-1)\n"
"      of nozero elements in sparse Hessian\n"
"Hv -- 1D array holding the values of nonzero elements in the sparse Hessian\n"
"      Has the same length as Hi and Hj.\n"
"\n"
"Hi, Hj, and Hv represent the full Hessian and not only the diagonal and the\n"
"upper triangle.\n"
"\n"
"This function is not supposed to be called by the user. It is called by the\n"
"wrapper function sphessjohn().\n"
"\n"
"CUTEst tools used: CUTEST_cshj\n"
);

static PyObject *cutest_sphessjohn(PyObject *self, PyObject *args) {
    PyArrayObject *arg1, *arg3, *MHi, *MHj, *MHv;
    doublereal *x, *v=NULL, *sv;
    doublereal y0;
    npy_int *si, *sj, nnzho;

    if (!check_setup())
        return NULL;

    if (CUTEst_ncon == 0) {
        PyErr_SetString(PyExc_Exception, "Unconstrained problems do not have a (Fritz) John function");
        return NULL;
    }

    if (!PyArg_ParseTuple(args, "OdO", &arg1, &y0, &arg3))
        return NULL;

    /* Check if x is double and of correct dimension */
    if (!(PyArray_Check(arg1) && PyArray_ISFLOAT(arg1) && PyArray_TYPE(arg1)==NPY_DOUBLE && PyArray_NDIM(arg1)==1 && PyArray_DIM(arg1, 0)==CUTEst_nvar)) {
        PyErr_SetString(PyExc_Exception, "Argument 1 must be a 1D double array of length nvar");
        return NULL;
    }

    /* Check if v is double and of correct dimension */
    if (!(PyArray_Check(arg3) && PyArray_ISFLOAT(arg3) && PyArray_TYPE(arg3)==NPY_DOUBLE && PyArray_NDIM(arg3)==1 && PyArray_DIM(arg3, 0)==CUTEst_ncon)) {
        PyErr_SetString(PyExc_Exception, "Argument 3 must be a 1D double array of length ncon");
        return NULL;
    }

    x=(npy_double *)PyArray_DATA(arg1);
    v=(npy_double *)PyArray_DATA(arg3);
    si=(npy_int *)malloc(CUTEst_nnzh*sizeof(npy_int));
    sj=(npy_int *)malloc(CUTEst_nnzh*sizeof(npy_int));
    sv=(npy_double *)malloc(CUTEst_nnzh*sizeof(npy_double));

    CUTEST_cshj((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, x, &y0, v, (integer *)&nnzho, (integer *)&CUTEst_nnzh,
        sv, (integer *)si, (integer *)sj);
    extract_sparse_hessian(nnzho, si, sj, sv, (PyArrayObject **)&MHi, (PyArrayObject **)&MHj, (PyArrayObject **)&MHv);

    /* Free temporary storage */
    free(si);
    free(sj);
    free(sv);

    return Py_BuildValue("OOO", MHi, MHj, MHv);
}
#endif

#ifdef CUTEST_VERSION
PyDoc_STRVAR(cutest_shoprod_doc,
"Returns the sparse product of the Hessian of the objective function at x and vector p.\n"
"\n"
"(ri, rv)=shoprod(p, x) -- use Hessian of objective function at x (constrained problem)\n"
"(ri, rv)=shoprod(p)    -- use last computed objective function Hessian (constrained problem)\n"
"\n"
"The Hessian is meant with respect to problem variables (has dimension n).\n"
"\n"
"Input\n"
"p -- 1D array of length n holding the components of the vector\n"
"x -- 1D array of length n holding the values of variables\n"
"\n"
"Output\n"
"ri  -- 1D array of length nnzohp holding the indices of the nonzeros of the sparse result\n"
"rv  -- 1D array of length nnzohp holding the values of the nonzeros of the sparse result\n"
"\n"
"CUTEst tools used: CUTEST_cohprods, CUTEST_cdimohp, CUTEST_cohprodsp\n"
);

static PyObject *cutest_shoprod(PyObject *self, PyObject *args) {
    PyArrayObject *arg1, *arg2, *Mri, *Mrv;
    doublereal *p, *x=NULL, *rv, *sv;
    npy_int *ri, *si;
    npy_int nnzohp, lohp;
    int i;
    npy_intp dims[1];

    if (!check_setup())
        return NULL;

    if (CUTEst_ncon == 0) {
        PyErr_SetString(PyExc_Exception, "For unconstrained problems please use hprod()");
        return NULL;
    }

    arg2=NULL;
    if (!PyArg_ParseTuple(args, "O|O", &arg1, &arg2))
        return NULL;

    if (PyObject_Length(args)!=1 && PyObject_Length(args)!=2) {
        PyErr_SetString(PyExc_Exception, "Need 1 or 2 arguments");
        return NULL;
    }

    /* Check if p is double and of correct dimension */
    if (!(PyArray_Check(arg1) && PyArray_ISFLOAT(arg1) && PyArray_TYPE(arg1)==NPY_DOUBLE && PyArray_NDIM(arg1)==1 && PyArray_DIM(arg1, 0)==CUTEst_nvar)) {
        PyErr_SetString(PyExc_Exception, "Argument 1 must be a 1D double array of length nvar");
        return NULL;
    }

    /* Check if x is double and of correct dimension */
    if (arg2!=NULL && !(PyArray_Check(arg2) && PyArray_ISFLOAT(arg2) && PyArray_TYPE(arg2)==NPY_DOUBLE && PyArray_NDIM(arg2)==1 && PyArray_DIM(arg2, 0)==CUTEst_nvar)) {
        PyErr_SetString(PyExc_Exception, "Argument 2 must be a 1D double array of length nvar");
        return NULL;
    }

    /* Get number of nonzeros in Hessian vector product */
    CUTEST_cdimohp((integer *)&status, (integer *)&lohp);

    p=(npy_double *)PyArray_DATA(arg1);
    if (arg2!=NULL)
        x=(npy_double *)PyArray_DATA(arg2);
    si=(npy_int *)malloc(lohp*sizeof(npy_int));
    sv=(npy_double *)malloc(lohp*sizeof(npy_double));

    /* Must use different variable for output NNZOHP and input LOHP */
    if (arg2==NULL) {
        CUTEST_cohprodsp((integer *)&status, (integer *)&nnzohp, (integer *)&lohp, (integer *)si);
        CUTEST_cohprods((integer *)&status, (integer *)&CUTEst_nvar, &somethingTrue, NULL, p, (integer *)&nnzohp, (integer *)&lohp, sv, (integer *)si);
    } else {
        CUTEST_cohprods((integer *)&status, (integer *)&CUTEst_nvar, &somethingFalse, x, p, (integer *)&nnzohp, (integer *)&lohp, sv, (integer *)si);
    }
        
    /* Allocate and copy results, convert indices from FORTRAN to C, free storage */
    dims[0]=nnzohp;
    Mri=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_INT);
    Mrv=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
    ri=(npy_int *)PyArray_DATA(Mri);
    rv=(npy_double *)PyArray_DATA(Mrv);
    for (i=0;i<nnzohp;i++) {
            ri[i]=si[i]-1;
            rv[i]=sv[i];
    }
    free(si);
    free(sv);

    return Py_BuildValue("OO", Mri, Mrv);
}
#endif


PyDoc_STRVAR(cutest_isphess_doc,
"Returns the sparse Hessian of the objective or the sparse Hessian of i-th\n"
"constraint at x.\n"
"\n"
"(Hi, Hj, Hv)=isphess(x)    -- Hessian of objective\n"
"(Hi, Hj, Hv)=isphess(x, i) -- Hessian of i-th constraint\n"
"\n"
"Input\n"
"x -- 1D array of length n with the values of variables\n"
"i -- integer holding the index of constraint (between 0 and m-1)\n"
"\n"
"Output\n"
"Hi -- 1D array of integers holding the row indices (0 .. n-1)\n"
"      of nozero elements in sparse Hessian\n"
"Hj -- 1D array of integers holding the column indices (0 .. n-1)\n"
"      of nozero elements in sparse Hessian\n"
"Hv -- 1D array holding the values of nonzero elements in the sparse Hessian\n"
"      Has the same length as Hi and Hj.\n"
"\n"
"Hi, Hj, and Hv represent the full Hessian and not only the diagonal and the\n"
"upper triangle.\n"
"\n"
"This function is not supposed to be called by the user. It is called by the\n"
"wrapper function isphess().\n"
"\n"
"CUTEst tools used: CUTEST_cish, CUTEST_ush\n"
);

static PyObject *cutest_isphess(PyObject *self, PyObject *args) {
    PyArrayObject *arg1, *MHi, *MHj, *MHv;
    doublereal *x, *sv;
    npy_int *si, *sj, nnzho, i;
    npy_int icon;

    if (!check_setup())
        return NULL;

    if (!PyArg_ParseTuple(args, "O|i", &arg1, &i))
        return NULL;

    if (PyObject_Length(args)>1) {
        icon=i+1;
        if (i<0 || i>=CUTEst_ncon) {
            PyErr_SetString(PyExc_Exception, "Argument 2 must be between 0 and ncon-1");
            return NULL;
        }
    } else {
        icon=0;
    }

    /* Check if x is double and of correct dimension */
    if (!(PyArray_Check(arg1) && PyArray_ISFLOAT(arg1) && PyArray_TYPE(arg1)==NPY_DOUBLE && PyArray_NDIM(arg1)==1 && PyArray_DIM(arg1, 0)==CUTEst_nvar)) {
        PyErr_SetString(PyExc_Exception, "Argument 1 must be a 1D double array of length nvar");
        return NULL;
    }

    x=(npy_double *)PyArray_DATA(arg1);
    si=(npy_int *)malloc(CUTEst_nnzh*sizeof(npy_int));
    sj=(npy_int *)malloc(CUTEst_nnzh*sizeof(npy_int));
    sv=(npy_double *)malloc(CUTEst_nnzh*sizeof(npy_double));

    if (CUTEst_ncon>0) {
        CUTEST_cish((integer *)&status, (integer *)&CUTEst_nvar, x, (integer *)&icon, (integer *)&nnzho, (integer *)&CUTEst_nnzh, sv, (integer *)si, (integer *)sj);
    } else {
        CUTEST_ush((integer *)&status, (integer *)&CUTEst_nvar, x, (integer *)&nnzho, (integer *)&CUTEst_nnzh, sv, (integer *)si, (integer *)sj);
    }

    extract_sparse_hessian(nnzho, si, sj, sv, (PyArrayObject **)&MHi, (PyArrayObject **)&MHj, (PyArrayObject **)&MHv);

    /* Free temporary storage */
    free(si);
    free(sj);
    free(sv);

    return Py_BuildValue("OOO", MHi, MHj, MHv);
}


PyDoc_STRVAR(cutest_gradsphess_doc,
"Returns the sparse Hessian of the Lagrangian, the sparse Jacobian of\n"
"constraints, and the gradient of the objective or Lagrangian.\n"
"\n"
"(g, Hi, Hj, Hv)=gradsphess(x) -- unconstrained problems\n"
"(gi, gv, Jvi, Jfi, Jv, Hi, Hj, Hv)=gradsphess(x, v, gradl)\n"
"                               -- constrained problems\n"
"\n"
"Input\n"
"x     -- 1D array of length n with the values of variables\n"
"v     -- 1D array of length m holding the values of Lagrange multipliers\n"
"gradl -- boolean flag. If False the gradient of the objective is returned, \n"
"         if True the gradient of the Lagrangian is returned. Default is False.\n"
"\n"
"Output\n"
"g   -- 1D array of length n with the gradient of objective or Lagrangian\n"
"Hi  -- 1D array of integers holding the row indices (0 .. n-1)\n"
"       of nozero elements in sparse Hessian\n"
"Hj  -- 1D array of integers holding the column indices (0 .. n-1)\n"
"       of nozero elements in sparse Hessian\n"
"Hv  -- 1D array holding the values of nonzero elements in the sparse Hessian\n"
"       Has the same length as Hi and Hj.\n"
"gi  -- 1D array of integers holding the indices (0 .. n-1) of nonzero\n"
"       elements in the sparse gradient vector\n"
"gv  -- 1D array holding the values of nonzero elements in the sparse gradient\n"
"       vector. Has the same length as gi.\n"
"Jvi -- 1D array of integers holding the column indices (0 .. n-1)\n"
"       of nozero elements in sparse Jacobian of constraints\n"
"Jfi -- 1D array of integers holding the row indices (0 .. m-1)\n"
"       of nozero elements in sparse Jacobian of constraints\n"
"Jv  -- 1D array holding the values of nonzero elements in the sparse Jacobian\n"
"       of constraints at x. Has the same length as Jvi and Jfi.\n"
"\n"
"For constrained problems the gradient is returned in sparse format.\n"
"\n"
"Hi, Hj, and Hv represent the full Hessian and not only the diagonal and the\n"
"upper triangle.\n"
"\n"
"This function is not supposed to be called by the user. It is called by the\n"
"wrapper function gradsphess().\n"
"\n"
"CUTEst tools used: CUTEST_csgrsh, CUTEST_ugrsh\n"
);

static PyObject *cutest_gradsphess(PyObject *self, PyObject *args) {
    PyArrayObject *arg1, *arg2, *Mg=NULL, *Mgi, *Mgv, *MJi, *MJfi, *MJv, *MHi, *MHj, *MHv;
    PyObject *arg3;
    doublereal *x, *v, *g, *sv, *sjv;
    npy_int lagrangian;
    npy_int *si, *sj, *sji, *sjfi, nnzho, nnzjplusn, nnzjplusno;
    npy_intp dims[1];

    if (!check_setup())
        return NULL;

    arg2=NULL;
    arg3=NULL;
    if (!PyArg_ParseTuple(args, "O|OO", &arg1, &arg2, &arg3))
        return NULL;

    /* Check bool argument */
    if (arg3!=NULL && arg3==Py_True)
        lagrangian=1;
    else
        lagrangian=0;

    /* Check if x is double and of correct dimension */
    if (!(PyArray_Check(arg1) && PyArray_ISFLOAT(arg1) && PyArray_TYPE(arg1)==NPY_DOUBLE && PyArray_NDIM(arg1)==1 && PyArray_DIM(arg1, 0)==CUTEst_nvar)) {
        PyErr_SetString(PyExc_Exception, "Argument 1 must be a 1D double array of length nvar");
        return NULL;
    }

    if (CUTEst_ncon>0) {
        /* Check if v is double and of correct dimension */
        if (arg2!=NULL) {
            /* Check if v is double and of correct dimension */
            if (!(PyArray_Check(arg2) && PyArray_ISFLOAT(arg2) && PyArray_TYPE(arg2)==NPY_DOUBLE && PyArray_NDIM(arg2)==1 && PyArray_DIM(arg2, 0)==CUTEst_ncon)) {
                PyErr_SetString(PyExc_Exception, "Argument 2 must be a 1D double array of length ncon");
                return NULL;
            }
        } else {
            PyErr_SetString(PyExc_Exception, "Argument 2 must be specified for constrained problems.");
            return NULL;
        }
    }

    x=(npy_double *)PyArray_DATA(arg1);
    si=(npy_int *)malloc(CUTEst_nnzh*sizeof(npy_int));
    sj=(npy_int *)malloc(CUTEst_nnzh*sizeof(npy_int));
    sv=(npy_double *)malloc(CUTEst_nnzh*sizeof(npy_double));

    if (CUTEst_ncon>0) {
        v=(npy_double *)PyArray_DATA(arg2);
        nnzjplusn=CUTEst_nnzj+CUTEst_nvar;
        sji=(npy_int *)malloc(nnzjplusn*sizeof(npy_int));
        sjfi=(npy_int *)malloc(nnzjplusn*sizeof(npy_int));
        sjv=(npy_double *)malloc(nnzjplusn*sizeof(npy_double));

        if (lagrangian) {
            CUTEST_csgrsh((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, x, v, &somethingTrue,
                    (integer *)&nnzjplusno, (integer *)&nnzjplusn, sjv, (integer *)sji, (integer *)sjfi,
                    (integer *)&nnzho, (integer *)&CUTEst_nnzh, sv, (integer *)si, (integer *)sj);
        } else {
            CUTEST_csgrsh((integer *)&status, (integer *)&CUTEst_nvar, (integer *)&CUTEst_ncon, x, v, &somethingFalse,
                    (integer *)&nnzjplusno, (integer *)&nnzjplusn, sjv, (integer *)sji, (integer *)sjfi,
                    (integer *)&nnzho, (integer *)&CUTEst_nnzh, sv, (integer *)si, (integer *)sj);
        }

        extract_sparse_gradient_jacobian(nnzjplusno, sji, sjfi, sjv, (PyArrayObject **)&Mgi, (PyArrayObject **)&Mgv, (PyArrayObject **)&MJi, (PyArrayObject **)&MJfi, (PyArrayObject **)&MJv);

        /* Free temporary storage - Jacobian */
        free(sji);
        free(sjfi);
        free(sjv);
    } else {
        dims[0]=CUTEst_nvar;
        Mg=(PyArrayObject *)PyArray_SimpleNew(1, dims, NPY_DOUBLE);
        g=(npy_double *)PyArray_DATA(Mg);

        CUTEST_ugrsh((integer *)&status, (integer *)&CUTEst_nvar, x, g, (integer *)&nnzho, (integer *)&CUTEst_nnzh, sv, (integer *)si, (integer *)sj);
    }

    extract_sparse_hessian(nnzho, si, sj, sv, (PyArrayObject **)&MHi, (PyArrayObject **)&MHj, (PyArrayObject **)&MHv);

    /* Free temporary storage - Hessian */
    free(si);
    free(sj);
    free(sv);

    if (CUTEst_ncon>0) {
        return Py_BuildValue("OOOOOOOO", Mgi, Mgv, MJi, MJfi, MJv, MHi, MHj, MHv);
    } else {
        return Py_BuildValue("OOOO", Mg, MHi, MHj, MHv);
    }
}


PyDoc_STRVAR(cutest_report_doc,
"Reports usage statistics.\n"
"\n"
"stat=report()\n"
"\n"
"Output\n"
"stat -- dictionary with the usage statistics\n"
"\n"
"The usage statistics dictionary has the following members:\n"
"f      -- number of objective evaluations\n"
"g      -- number of objective gradient evaluations\n"
"H      -- number of objective Hessian evaluations\n"
"Hprod  -- number of Hessian multiplications with a vector\n"
"tsetup -- CPU time used in setup\n"
"trun   -- CPU time used in run\n"
"\n"
"For constrained problems the following additional members are available\n"
"c      -- number of constraint evaluations\n"
"cg     -- number of constraint gradient evaluations\n"
"cH     -- number of constraint Hessian evaluations\n"
"\n"
"CUTEst tools used: CUTEST_creport, CUTEST_ureport\n"
);

static PyObject *cutest_report(PyObject *self, PyObject *args) {
    doublereal calls[7], time[2];
    PyObject *dict;

    if (!check_setup())
        return NULL;

    if (PyObject_Length(args)!=0) {
        PyErr_SetString(PyExc_Exception, "report() takes no arguments");
        return NULL;
    }

    if (CUTEst_ncon>0)
        CUTEST_creport((integer *)&status, calls, time);
    else
        CUTEST_ureport((integer *)&status, calls, time);

    dict=PyDict_New();
    PyDict_SetItemString(dict, "f", PyLong_FromLong((long)(calls[0])));
    PyDict_SetItemString(dict, "g", PyLong_FromLong((long)(calls[1])));
    PyDict_SetItemString(dict, "H", PyLong_FromLong((long)(calls[2])));
    PyDict_SetItemString(dict, "Hprod", PyLong_FromLong((long)(calls[3])));
    if (CUTEst_ncon>0) {
        PyDict_SetItemString(dict, "c", PyLong_FromLong((long)(calls[4])));
        PyDict_SetItemString(dict, "cg", PyLong_FromLong((long)(calls[5])));
        PyDict_SetItemString(dict, "cH", PyLong_FromLong((long)(calls[6])));
    }
    PyDict_SetItemString(dict, "tsetup", PyFloat_FromDouble((long)(time[0])));
    PyDict_SetItemString(dict, "trun", PyFloat_FromDouble((long)(time[1])));

    return decRefDict(dict);
}


PyDoc_STRVAR(cutest_terminate_doc,
"Deallocate all internal private storage.\n"
"\n"
"terminate()\n"
"\n"
"CUTEst tools used: CUTEST_cterminate, CUTEST_uterminate\n"
);

static PyObject *cutest_terminate(PyObject *self, PyObject *args) {

    if (!check_setup())
        return NULL;

    if (PyObject_Length(args)!=0) {
        PyErr_SetString(PyExc_Exception, "terminate() takes no arguments");
        return NULL;
    }

    if (CUTEst_ncon>0)
        CUTEST_cterminate((integer *)&status);
    else
        CUTEST_uterminate((integer *)&status);

    /* Problem is no longer set up */
    setupCalled = 0;

    /* Return None boilerplate */
    Py_INCREF(Py_None);
    return Py_None;
}


/* Python Module */

/* Module method table */
static PyMethodDef _methods[] = {
    {"dims", cutest_dims, METH_VARARGS, cutest_dims_doc},
    {"setup", cutest_setup, METH_VARARGS, cutest_setup_doc},
    {"varnames", cutest_varnames, METH_VARARGS, cutest_varnames_doc},
    {"connames", cutest_connames, METH_VARARGS, cutest_connames_doc},
    {"objcons", cutest_objcons, METH_VARARGS, cutest_objcons_doc},
    {"obj", cutest_obj, METH_VARARGS, cutest_obj_doc},
    {"grad", cutest_grad, METH_VARARGS, cutest_grad_doc},
    {"cons", cutest_cons, METH_VARARGS, cutest_cons_doc},
    {"lag", cutest_lag, METH_VARARGS, cutest_lag_doc},
    {"lagjac", cutest_lagjac, METH_VARARGS, cutest_lagjac_doc},
    {"jprod", cutest_jprod, METH_VARARGS, cutest_jprod_doc},
    {"hess", cutest_hess, METH_VARARGS, cutest_hess_doc},
    {"ihess", cutest_ihess, METH_VARARGS, cutest_ihess_doc},
    {"hprod", cutest_hprod, METH_VARARGS, cutest_hprod_doc},
    {"gradhess", cutest_gradhess, METH_VARARGS, cutest_gradhess_doc},
    {"scons", cutest_scons, METH_VARARGS, cutest_scons_doc},
    {"slagjac", cutest_slagjac, METH_VARARGS, cutest_slagjac_doc},
    {"sphess", cutest_sphess, METH_VARARGS, cutest_sphess_doc},
    {"isphess", cutest_isphess, METH_VARARGS, cutest_isphess_doc},
    {"gradsphess", cutest_gradsphess, METH_VARARGS, cutest_gradsphess_doc},
    {"report", cutest_report, METH_VARARGS, cutest_report_doc},
    {"terminate", cutest_terminate, METH_VARARGS, cutest_terminate_doc},
    #ifdef CUTEST_VERSION
    {"hessjohn", cutest_hessjohn, METH_VARARGS, cutest_hessjohn_doc},
    {"hjprod", cutest_hjprod, METH_VARARGS, cutest_hjprod_doc},
    {"sphessjohn", cutest_sphessjohn, METH_VARARGS, cutest_sphessjohn_doc},
    {"shoprod", cutest_shoprod, METH_VARARGS, cutest_shoprod_doc},
    #endif
    {NULL, NULL, 0, NULL}  /* Sentinel, marks the end of this structure */
};

/* Python module definition */
static struct PyModuleDef module = {
   PyModuleDef_HEAD_INIT,
   "_pycutestitf",  /* name of module */
   NULL,           /* module documentation, may be NULL */
   -1,              /* size of per-interpreter state of the module,
                       or -1 if the module keeps state in global variables */
   _methods         /* module methods */
};

/* Python module initialization */
PyMODINIT_FUNC PyInit__pycutestitf(void) { // must be same as module name above
    import_array();  // for NumPy arrays
    return PyModule_Create(&module);
}
"""
# end of raw string
