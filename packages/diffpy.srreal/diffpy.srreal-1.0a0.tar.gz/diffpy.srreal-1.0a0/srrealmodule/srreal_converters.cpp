/*****************************************************************************
*
* diffpy.srreal     by DANSE Diffraction group
*                   Simon J. L. Billinge
*                   (c) 2009 The Trustees of Columbia University
*                   in the City of New York.  All rights reserved.
*
* File coded by:    Pavol Juhas
*
* See AUTHORS.txt for a list of people who contributed.
* See LICENSE_DANSE.txt for license information.
*
******************************************************************************
*
* utilities for conversion between C++ and Python types.
* boost python converters are prone to conflicts.
*
*****************************************************************************/

#include <boost/python/def.hpp>
#include <boost/python/stl_iterator.hpp>
#include <boost/python/exception_translator.hpp>
#include <string>
#include <valarray>
#include <stdexcept>
#include <cassert>

#include <diffpy/Attributes.hpp>
#include <diffpy/srreal/StructureAdapter.hpp>

#include "srreal_converters.hpp"
// numpy/arrayobject.h needs to be included after srreal_converters.hpp,
// which defines PY_ARRAY_UNIQUE_SYMBOL.  NO_IMPORT_ARRAY indicates
// import_array will be called in the extension module initializer.
#define NO_IMPORT_ARRAY
#include <numpy/arrayobject.h>


namespace {

// exception translations ----------------------------------------------------

using diffpy::attributes::DoubleAttributeError;
using std::invalid_argument;

void translate_DoubleAttributeError(const DoubleAttributeError& e)
{
    PyErr_SetString(PyExc_AttributeError, e.what());
}


void translate_invalid_argument(const invalid_argument& e)
{
    PyErr_SetString(PyExc_ValueError, e.what());
}


boost::python::object newNumPyArray(int dim, const int* sz, int typenum)
{
    using namespace std;
    using namespace boost;
    // copy the size information to an array of npy_intp
    valarray<npy_intp> npsza(dim);
    npy_intp& npsz = npsza[0];
    copy(sz, sz + dim, &npsz);
    // create numpy array
    python::object rv(
            python::handle<>(PyArray_SimpleNew(dim, &npsz, typenum)));
    return rv;
}


bool isiterable(boost::python::object obj)
{
    using namespace boost::python;
    object Iterable = import("collections").attr("Iterable");
    bool rv = (1 == PyObject_IsInstance(obj.ptr(), Iterable.ptr()));
    return rv;
}

}   // namespace

namespace srrealmodule {

/// this function registers all exception translators
void wrap_exceptions()
{
    using boost::python::register_exception_translator;
    register_exception_translator<DoubleAttributeError>(
            &translate_DoubleAttributeError);
    register_exception_translator<invalid_argument>(
            &translate_invalid_argument);
}


/// helper for creating numpy array of doubles
NumPyArray_DoublePtr createNumPyDoubleArray(int dim, const int* sz)
{
    boost::python::object rvobj = newNumPyArray(dim, sz, PyArray_DOUBLE);
    double* rvdata = static_cast<double*>(PyArray_DATA(rvobj.ptr()));
    NumPyArray_DoublePtr rv(rvobj, rvdata);
    return rv;
}


/// helper for creating a numpy array view on a double array
boost::python::object
createNumPyDoubleView(double* data, int dim, const int* sz)
{
    using namespace std;
    using namespace boost;
    valarray<npy_intp> npsza(dim);
    npy_intp* npsz = &(npsza[0]);
    copy(sz, sz + dim, npsz);
    python::object rv(
            python::handle<>(
                PyArray_SimpleNewFromData(dim, npsz, PyArray_DOUBLE, data)));
    return rv;
}


/// NumPy array view specializations for R3::Vector
boost::python::object viewAsNumPyArray(::diffpy::srreal::R3::Vector& v)
{
    using namespace diffpy::srreal;
    double* data = &(v[0]);
    int sz = R3::Ndim;
    return createNumPyDoubleView(data, 1, &sz);
}


/// NumPy array view specializations for R3::Matrix
boost::python::object viewAsNumPyArray(::diffpy::srreal::R3::Matrix& mx)
{
    using namespace diffpy::srreal;
    double* data = &(mx(0, 0));
    int sz[2] = {R3::Ndim, R3::Ndim};
    return createNumPyDoubleView(data, 2, sz);
}


/// helper for creating a 2D numpy array view on a 2D double buffer
boost::python::object
viewAs2DNumPyDoubleArray(double* data, int rows, int cols);


/// helper for creating numpy array of integers
NumPyArray_IntPtr createNumPyIntArray(int dim, const int* sz)
{
    boost::python::object rvobj = newNumPyArray(dim, sz, PyArray_INT);
    int* rvdata = static_cast<int*>(PyArray_DATA(rvobj.ptr()));
    NumPyArray_IntPtr rv(rvobj, rvdata);
    return rv;
}


/// efficient conversion of Python object to a QuantityType
diffpy::srreal::QuantityType&
extractQuantityType(
        boost::python::object obj,
        diffpy::srreal::QuantityType& rv)
{
    using namespace boost;
    // extract QuantityType directly
    python::extract<diffpy::srreal::QuantityType&> getqt(obj);
    if (getqt.check())  return getqt();
    // copy data directly if it is a numpy array of doubles
    PyObject* pobj = obj.ptr();
    bool isdoublenumpyarray = PyArray_Check(pobj) &&
        (1 == PyArray_NDIM(pobj)) &&
        (PyArray_DOUBLE == PyArray_TYPE(pobj));
    if (isdoublenumpyarray)
    {
        double* pfirst = static_cast<double*>(PyArray_DATA(pobj));
        double* plast = pfirst + PyArray_SIZE(pobj);
        rv.assign(pfirst, plast);
        return rv;
    }
    // otherwise copy elementwise converting each element to a double
    python::stl_input_iterator<double> begin(obj), end;
    rv.assign(begin, end);
    return rv;
}


/// extract integer with a support for numpy.int types
int extractint(boost::python::object obj)
{
    using namespace boost;
    python::extract<int> geti(obj);
    if (geti.check())  return geti();
    PyObject* pobj = obj.ptr();
    if (PyArray_CheckScalar(pobj))
    {
        int rv = PyArray_PyIntAsInt(pobj);
        return rv;
    }
    // nothing worked, call geti which will raise an exception
    return geti();
}


/// extract a vector of integers from a numpy array, iterable or scalar
std::vector<int> extractintvector(boost::python::object obj)
{
    using namespace boost::python;
    std::vector<int> rv;
    // iterable of integers
    if (isiterable(obj))
    {
        PyObject* pobj = obj.ptr();
        // handle numpy array of integers
        bool isintegernumpyarray = PyArray_Check(pobj) &&
            (1 == PyArray_NDIM(pobj)) && PyArray_ISINTEGER(pobj);
        if (isintegernumpyarray)
        {
            object aobj = obj;
            if (PyArray_INT != PyArray_TYPE(pobj))
            {
                object a1(handle<>(PyArray_Cast(
                                reinterpret_cast<PyArrayObject*>(pobj),
                                PyArray_INT)));
                aobj = a1;
            }
            PyObject* pa = aobj.ptr();
            assert(PyArray_INT == PyArray_TYPE(pa));
            int* pfirst = static_cast<int*>(PyArray_DATA(pa));
            int* plast = pfirst + PyArray_SIZE(pa);
            rv.assign(pfirst, plast);
            return rv;
        }
        // otherwise translate every item in the iterable
        stl_input_iterator<object> ii(obj), end;
        rv.reserve(len(obj));
        for (; ii != end; ++ii)
        {
            int idx = extractint(*ii);
            rv.push_back(idx);
        }
        return rv;
    }
    // try to handle it as a scalar
    int idx = extractint(obj);
    rv.push_back(idx);
    return rv;
}


/// helper for raising RuntimeError on a call of pure virtual function
void throwPureVirtualCalled(const char* fncname)
{
    std::string emsg = "Pure virtual function '";
    emsg += fncname;
    emsg += "' called.";
    PyErr_SetString(PyExc_RuntimeError, emsg.c_str());
    boost::python::throw_error_already_set();
}

}   // namespace srrealmodule


namespace diffpy {
namespace srreal {

/// shared converter that first tries to extract the pointer and then calls
/// diffpy.srreal.structureadapter.createStructureAdapter
StructureAdapterPtr createStructureAdapter(::boost::python::object stru)
{
    using namespace boost::python;
    StructureAdapterPtr adpt;
    extract<StructureAdapterPtr> getadpt(stru);
    if (getadpt.check())  adpt = getadpt();
    else
    {
        object mod = import("diffpy.srreal.structureadapter");
        object convertinpython = mod.attr("createStructureAdapter");
        adpt = extract<StructureAdapterPtr>(convertinpython(stru));
    }
    return adpt;
}

}   // namespace srreal
}   // namespace diffpy

// End of file
