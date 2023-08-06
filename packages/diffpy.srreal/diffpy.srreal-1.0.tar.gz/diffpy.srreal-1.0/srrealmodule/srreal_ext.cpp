/*****************************************************************************
*
* diffpy.srreal     by DANSE Diffraction group
*                   Simon J. L. Billinge
*                   (c) 2010 The Trustees of Columbia University
*                   in the City of New York.  All rights reserved.
*
* File coded by:    Pavol Juhas
*
* See AUTHORS.txt for a list of people who contributed.
* See LICENSE_DANSE.txt for license information.
*
******************************************************************************
*
* srreal_ext - boost python interface to the srreal C++ codes in libdiffpy
*
*****************************************************************************/

#include <boost/python/module.hpp>
#include <boost/python/import.hpp>
#include "srreal_numpy_symbol.hpp"
#include <numpy/arrayobject.h>

// Declaration of the external wrappers --------------------------------------

namespace srrealmodule {

void wrap_exceptions();
void wrap_EventTicker();
void wrap_Attributes();
void wrap_StructureDifference();
void wrap_StructureAdapter();
void wrap_AtomicStructureAdapter();
void wrap_ObjCrystAdapters();
void wrap_BaseBondGenerator();
void wrap_PairQuantity();
void wrap_PeakWidthModel();
void wrap_ScatteringFactorTable();
void wrap_PeakProfile();
void wrap_BVParametersTable();
void wrap_BVSCalculator();
void wrap_PDFBaseline();
void wrap_PDFEnvelope();
void wrap_PDFCalculators();
void wrap_BondCalculator();
void wrap_AtomRadiiTable();
void wrap_OverlapCalculator();

}   // namespace srrealmodule

// Module Definitions --------------------------------------------------------

BOOST_PYTHON_MODULE(srreal_ext)
{
    using namespace srrealmodule;
    // initialize numpy module
    import_array();
    // execute external wrappers
    wrap_exceptions();
    wrap_EventTicker();
    wrap_Attributes();
    wrap_StructureDifference();
    wrap_StructureAdapter();
    wrap_AtomicStructureAdapter();
    wrap_ObjCrystAdapters();
    wrap_BaseBondGenerator();
    wrap_PairQuantity();
    wrap_PeakWidthModel();
    wrap_ScatteringFactorTable();
    wrap_PeakProfile();
    wrap_BVParametersTable();
    wrap_BVSCalculator();
    wrap_PDFBaseline();
    wrap_PDFEnvelope();
    wrap_PDFCalculators();
    wrap_BondCalculator();
    wrap_AtomRadiiTable();
    wrap_OverlapCalculator();
    // load structure converters
    using boost::python::import;
    import("diffpy.srreal.structureconverters");
}

// End of file
