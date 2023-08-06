/*
 * XSAnnotation.cpp
 *
 *  Created on: 2013/03/04
 *      Author: mugwort_rc
 */

#include "XSAnnotation.h"

#include <boost/python.hpp>

//! for forward declaration
#include <xercesc/dom/DOMNode.hpp>
#include <xercesc/sax2/ContentHandler.hpp>

#include <xercesc/framework/psvi/XSAnnotation.hpp>

#include "../../internal/XSerializable.h"
#include "../../util/XMLString.h"

namespace pyxerces {

class XSAnnotationDefVisitor
: public boost::python::def_visitor<XSAnnotationDefVisitor>
{
friend class def_visitor_access;
public:
template <class T>
void visit(T& class_) const {
	class_
	.def("__init__", boost::python::make_constructor(static_cast<xercesc::XSAnnotation*(*)(const XMLString&, xercesc::MemoryManager* const)>(&XSAnnotation_fromstring)))
	.def("__init__", boost::python::make_constructor(static_cast<xercesc::XSAnnotation*(*)(const XMLString&)>(&XSAnnotation_fromstring)))
	;
}

static xercesc::XSAnnotation* XSAnnotation_fromstring(const XMLString& contents, xercesc::MemoryManager* const manager) {
	return new xercesc::XSAnnotation(contents.ptr(), manager);
}

static xercesc::XSAnnotation* XSAnnotation_fromstring(const XMLString& contents) {
	return XSAnnotation_fromstring(contents, xercesc::XMLPlatformUtils::fgMemoryManager);
}

};

void XSAnnotation_init(void) {
	//! xercesc::XSAnnotation
	auto XSAnnotation = boost::python::class_<xercesc::XSAnnotation, boost::noncopyable, boost::python::bases<xercesc::XSerializable, xercesc::XSObject> >("XSAnnotation", boost::python::init<const XMLCh* const, boost::python::optional<xercesc::MemoryManager* const> >())
			.def(boost::python::init<xercesc::MemoryManager* const>())
			.def(XSAnnotationDefVisitor())
			.def("writeAnnotation", static_cast<void(xercesc::XSAnnotation::*)(xercesc::DOMNode*, xercesc::XSAnnotation::ANNOTATION_TARGET)>(&xercesc::XSAnnotation::writeAnnotation))
			.def("writeAnnotation", static_cast<void(xercesc::XSAnnotation::*)(xercesc::ContentHandler*)>(&xercesc::XSAnnotation::writeAnnotation))
			.def("getAnnotationString", static_cast<const XMLCh*(xercesc::XSAnnotation::*)(void) const>(&xercesc::XSAnnotation::getAnnotationString), boost::python::return_value_policy<boost::python::return_by_value>())
			.def("setNext", &xercesc::XSAnnotation::setNext)
			.def("getNext", &xercesc::XSAnnotation::getNext, boost::python::return_value_policy<boost::python::reference_existing_object>())
			.def("getLineCol", &xercesc::XSAnnotation::getLineCol)
			.def("getSystemId", &xercesc::XSAnnotation::getSystemId, boost::python::return_value_policy<boost::python::return_by_value>())
			.def("setLineCol", &xercesc::XSAnnotation::setLineCol)
			.def("setSystemId", &xercesc::XSAnnotation::setSystemId)
			PyDECL_XSERIALIZABLE(XSAnnotation)
			;
	boost::python::scope XSAnnotationScope = XSAnnotation;
	//! xercesc::XSAnnotation::ANNOTATION_TARGET
	boost::python::enum_<xercesc::XSAnnotation::ANNOTATION_TARGET>("ANNOTATION_TARGET")
			.value("W3C_DOM_ELEMENT", xercesc::XSAnnotation::W3C_DOM_ELEMENT)
			.value("W3C_DOM_DOCUMENT", xercesc::XSAnnotation::W3C_DOM_DOCUMENT)
			.export_values()
			;
}

} /* namespace pyxerces */
