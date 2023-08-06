/*
 * SAXParseException.cpp
 *
 *  Created on: 2013/02/28
 *      Author: mugwort_rc
 */

#include "SAXParseException.h"

#include <boost/python.hpp>

//!< for forward declaration
#include <xercesc/sax/Locator.hpp>

#include <xercesc/sax/SAXParseException.hpp>

#include "../common/Exception.h"
#include "../util/XMLString.h"

namespace pyxerces {

//! SAXParseException
PyObject* pyXercesSAXParseExceptionType = nullptr;

void translateSAXParseException(const xercesc::SAXParseException& e) {
	assert(pyXercesSAXParseExceptionType != nullptr);
	boost::python::object instance(e);

	boost::python::object exceptionType(boost::python::handle<>(boost::python::borrowed(pyXercesSAXParseExceptionType)));
	exceptionType.attr("cause") = instance;

	PyErr_SetString(pyXercesSAXParseExceptionType, XMLString(e.getMessage()).toString().c_str());
}

void SAXParseException_init(void) {
	//! xercesc::SAXParseException
	auto SAXParseException = boost::python::class_<xercesc::SAXParseException, boost::python::bases<xercesc::SAXException> >("SAXParseException", boost::python::init<const XMLCh* const, const xercesc::Locator&, boost::python::optional<xercesc::MemoryManager* const> >())
			.def(boost::python::init<const XMLCh* const, const XMLCh* const, const XMLCh* const, const XMLFileLoc, const XMLFileLoc, boost::python::optional<xercesc::MemoryManager* const> >())
			.def("getColumnNumber", &xercesc::SAXParseException::getColumnNumber)
			.def("getLineNumber", &xercesc::SAXParseException::getLineNumber)
			.def("getPublicId", &xercesc::SAXParseException::getPublicId, boost::python::return_value_policy<boost::python::return_by_value>())
			.def("getSystemId", &xercesc::SAXParseException::getSystemId, boost::python::return_value_policy<boost::python::return_by_value>())
			;
	pyXercesSAXParseExceptionType = createException("SAXParseException");
	boost::python::register_exception_translator<xercesc::SAXParseException>(&translateSAXParseException);
}

} /* namespace pyxerces */
