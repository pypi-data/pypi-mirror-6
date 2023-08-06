/*
 * PSVIHandler.cpp
 *
 *  Created on: 2013/02/23
 *      Author: mugwort_rc
 */

#include "PSVIHandler.h"

#include <boost/python.hpp>

//! for forward declaration
#include <xercesc/framework/psvi/PSVIElement.hpp>
#include <xercesc/framework/psvi/PSVIAttributeList.hpp>

#include <xercesc/framework/psvi/PSVIHandler.hpp>

#include "../../util/XMLString.h"

namespace pyxerces {

class PSVIHandlerDefVisitor
: public boost::python::def_visitor<PSVIHandlerDefVisitor>
{
friend class def_visitor_access;
public:
template <class T>
void visit(T& class_) const {
	class_
	.def("handleElementPSVI", &PSVIHandlerDefVisitor::handleElementPSVI)
	.def("handlePartialElementPSVI", &PSVIHandlerDefVisitor::handlePartialElementPSVI)
	.def("handleAttributesPSVI", &PSVIHandlerDefVisitor::handleAttributesPSVI)
	;
}

static void handleElementPSVI(xercesc::PSVIHandler& self, const XMLString& localName, const XMLString& uri, xercesc::PSVIElement* elementInfo) {
	self.handleElementPSVI(localName.ptr(), uri.ptr(), elementInfo);
}

static void handlePartialElementPSVI(xercesc::PSVIHandler& self, const XMLString& localName, const XMLString& uri, xercesc::PSVIElement* elementInfo) {
	self.handlePartialElementPSVI(localName.ptr(), uri.ptr(), elementInfo);
}

static void handleAttributesPSVI(xercesc::PSVIHandler& self, const XMLString& localName, const XMLString& uri, xercesc::PSVIAttributeList* psviAttributes) {
	self.handleAttributesPSVI(localName.ptr(), uri.ptr(), psviAttributes);
}

};

class PSVIHandlerWrapper
: public xercesc::PSVIHandler, public boost::python::wrapper<xercesc::PSVIHandler>
{
public:
void handleElementPSVI(const XMLCh* const localName, const XMLCh* const uri, xercesc::PSVIElement* elementInfo) {
	this->get_override("handleElementPSVI")(XMLString(localName), XMLString(uri), boost::python::ptr(elementInfo));
}

void handlePartialElementPSVI(const XMLCh* const localName, const XMLCh* const uri, xercesc::PSVIElement* elementInfo) {
	if(boost::python::override handlePartialElementPSVI = this->get_override("handlePartialElementPSVI")){
		handlePartialElementPSVI(XMLString(localName), XMLString(uri), boost::python::ptr(elementInfo));
	}else{
		xercesc::PSVIHandler::handlePartialElementPSVI(localName, uri, elementInfo);
	}
}

void handleAttributesPSVI(const XMLCh* const localName, const XMLCh* const uri, xercesc::PSVIAttributeList* psviAttributes) {
	this->get_override("handleAttributesPSVI")(XMLString(localName), XMLString(uri), boost::python::ptr(psviAttributes));
}

};

void PSVIHandler_init(void) {
	//! xercesc::PSVIHandler
	boost::python::class_<PSVIHandlerWrapper, boost::noncopyable>("PSVIHandler")
			.def(PSVIHandlerDefVisitor())
			.def("handleElementPSVI", boost::python::pure_virtual(&xercesc::PSVIHandler::handleElementPSVI))
			.def("handlePartialElementPSVI", &xercesc::PSVIHandler::handlePartialElementPSVI)
			.def("handleAttributesPSVI", boost::python::pure_virtual(&xercesc::PSVIHandler::handleAttributesPSVI))
			;
}

} /* namespace pyxerces */
