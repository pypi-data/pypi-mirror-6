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
* Bindings to the PeakProfile class.  The business methods can be overloaded
* from Python to create custom peak profiles.  This may be however quite slow.
*
*****************************************************************************/

#include <boost/python.hpp>
#include <string>

#include <diffpy/srreal/PeakProfile.hpp>
#include <diffpy/srreal/GaussianProfile.hpp>
#include <diffpy/srreal/CroppedGaussianProfile.hpp>

#include "srreal_converters.hpp"
#include "srreal_pickling.hpp"

namespace srrealmodule {
namespace nswrap_PeakProfile {

using namespace boost;
using namespace boost::python;
using namespace diffpy::srreal;

// docstrings ----------------------------------------------------------------

const char* doc_PeakProfile = "\
Base class and registry for PDF peak profile functions.\n\
The peak profile functions must be centered at 0 and their integrated\n\
area must be 1.\n\
";

const char* doc_PeakProfile_create = "\
Return a new default instance of the same type as self.\n\
\n\
This method must be overloaded in a derived class.\n\
";

const char* doc_PeakProfile_clone = "\
Return a new instance that is a copy of self.\n\
\n\
This method must be overloaded in a derived class.\n\
";

const char* doc_PeakProfile_type = "\
Return a unique string type that identifies a PeakProfile-derived class.\n\
The string type is used for class registration and in the createByType\n\
function.\n\
\n\
This method must be overloaded in a derived class.\n\
";

const char* doc_PeakProfile___call__ = "\
Evaluate peak profile function for a given position and peak width.\n\
\n\
x    -- coordinate where the profile function is evaluated.\n\
        x is always relative to the peak center, i.e., the profile function\n\
        must be centered at 0.\n\
fwhm -- Full Width at Half Maximum of the profile function.\n\
\n\
Return float.\n\
";

const char* doc_PeakProfile_xboundlo = "\
Lower x-bound where profile function becomes smaller than precision.\n\
The bound is evaluated relative to profile maximum, i.e., for each x below\n\
xboundlo the profile function must be smaller than (peakprecision * maximum).\n\
\n\
fwhm -- Full Width at Half Maximum of the profile function\n\
\n\
Return float.  See also the peakprecision property.\n\
";

const char* doc_PeakProfile_xboundhi = "\
Upper x-bound where profile function becomes smaller than precision.\n\
The bound is evaluated relative to profile maximum, i.e., for each x above\n\
xboundhi the profile function must be smaller than (peakprecision * maximum).\n\
\n\
fwhm -- Full Width at Half Maximum of the profile function\n\
\n\
Return float.  See also the peakprecision property.\n\
";

const char* doc_PeakProfile_ticker = "\
Return EventTicker that marks last modification time of this object.\n\
This ticker object is used in fast PDF update, to check if PeakProfile\n\
has changed since the last calculation.  The ticker.click() method needs\n\
to be therefore called after every change in PeakProfile configuration.\n\
\n\
Return EventTicker object.\n\
This method may be overloaded in a Python derived class.\n\
";

const char* doc_PeakProfile__registerThisType = "\
Add this class to the global registry of PeakProfile types.\n\
\n\
This method must be called once after definition of the derived\n\
class to support pickling and the createByType factory.\n\
";

const char* doc_PeakProfile_createByType = "\
Return a new PeakProfile instance of the specified string type.\n\
\n\
tp   -- string type identifying a registered PeakProfile class\n\
        See getRegisteredTypes for the allowed values.\n\
\n\
Return a new instance of the PeakProfile-derived class.\n\
";

const char* doc_PeakProfile_getRegisteredTypes = "\
Set of string identifiers for registered PeakProfile classes.\n\
These are allowed arguments for the createByType static method.\n\
";

const char* doc_GaussianProfile = "\
Gaussian profile function.\n\
";

const char* doc_CroppedGaussianProfile = "\
Gaussian function cropped to zero at its crossing with peakprecision.\n\
\n\
The profile is also rescaled to keep the integrated area of 1.\n\
";

// wrappers ------------------------------------------------------------------

DECLARE_PYSET_FUNCTION_WRAPPER(PeakProfile::getRegisteredTypes,
        getPeakProfileTypes_asset)

// Helper class allows overload of the PeakProfile methods from Python.

class PeakProfileWrap :
    public PeakProfile,
    public wrapper_srreal<PeakProfile>
{
    public:

        // HasClassRegistry methods

        PeakProfilePtr create() const
        {
            object rv = this->get_pure_virtual_override("create")();
            return mconfigurator.fetch(rv);
        }

        PeakProfilePtr clone() const
        {
            return this->get_pure_virtual_override("clone")();
        }


        const std::string& type() const
        {
            python::object tp = this->get_pure_virtual_override("type")();
            mtype = python::extract<std::string>(tp);
            return mtype;
        }

        // own methods

        double operator()(double x, double fwhm) const
        {
            return this->get_pure_virtual_override("__call__")(x, fwhm);
        }

        double xboundlo(double fwhm) const
        {
            return this->get_pure_virtual_override("xboundlo")(fwhm);
        }

        double xboundhi(double fwhm) const
        {
            return this->get_pure_virtual_override("xboundhi")(fwhm);
        }

        // Make the ticker method overloadable from Python

        diffpy::eventticker::EventTicker& ticker() const
        {
            override f = this->get_override("ticker");
            if (f)  return f();
            return this->default_ticker();
        }

        diffpy::eventticker::EventTicker& default_ticker() const
        {
            return this->PeakProfile::ticker();
        }

    protected:

        // HasClassRegistry method

        void setupRegisteredObject(PeakProfilePtr p) const
        {
            mconfigurator.setup(p);
        }

    private:

        mutable std::string mtype;
        wrapper_registry_configurator<PeakProfile> mconfigurator;

};  // class PeakProfileWrap

std::string peakprofile_tostring(PeakProfilePtr obj)
{
    return diffpy::serialization_tostring(obj);
}


PeakProfilePtr peakprofile_fromstring(const std::string& content)
{
    PeakProfilePtr rv;
    diffpy::serialization_fromstring(rv, content);
    return rv;
}


}   // namespace nswrap_PeakProfile

// Wrapper definition --------------------------------------------------------

void wrap_PeakProfile()
{
    using namespace nswrap_PeakProfile;
    using diffpy::Attributes;
    namespace bp = boost::python;

    class_<PeakProfileWrap, bases<Attributes>,
        noncopyable>("PeakProfile", doc_PeakProfile)
        .def("create", &PeakProfile::create, doc_PeakProfile_create)
        .def("clone", &PeakProfile::clone, doc_PeakProfile_clone)
        .def("type", &PeakProfile::type,
                return_value_policy<copy_const_reference>(),
                doc_PeakProfile_type)
        .def("__call__", &PeakProfile::operator(),
                (bp::arg("x"), bp::arg("fwhm")), doc_PeakProfile___call__)
        .def("xboundlo", &PeakProfile::xboundlo,
                bp::arg("fwhm"), doc_PeakProfile_xboundlo)
        .def("xboundhi", &PeakProfile::xboundhi,
                bp::arg("fwhm"), doc_PeakProfile_xboundhi)
        .def("ticker",
                &PeakProfile::ticker,
                return_internal_reference<>(),
                doc_PeakProfile_ticker)
        .def("_registerThisType", &PeakProfile::registerThisType,
                doc_PeakProfile__registerThisType)
        .def("createByType", &PeakProfile::createByType,
                bp::arg("tp"), doc_PeakProfile_createByType)
        .staticmethod("createByType")
        .def("getRegisteredTypes", getPeakProfileTypes_asset,
                doc_PeakProfile_getRegisteredTypes)
        .staticmethod("getRegisteredTypes")
        .enable_pickling()
        ;

    register_ptr_to_python<PeakProfilePtr>();

    class_<GaussianProfile, bases<PeakProfile> >(
            "GaussianProfile", doc_GaussianProfile)
        ;

    class_<CroppedGaussianProfile, bases<GaussianProfile> >(
            "CroppedGaussianProfile", doc_CroppedGaussianProfile)
        ;

    // pickling support functions
    def("_PeakProfile_tostring", peakprofile_tostring);
    def("_PeakProfile_fromstring", peakprofile_fromstring);

}

}   // namespace srrealmodule

// End of file
