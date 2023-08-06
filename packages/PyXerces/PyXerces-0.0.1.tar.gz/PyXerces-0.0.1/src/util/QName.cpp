/*
 * QName.cpp
 *
 *  Created on: 2013/02/23
 *      Author: mugwort_rc
 */

#include "QName.h"

#include <boost/python.hpp>
#include <xercesc/util/QName.hpp>

#include "../internal/XSerializable.h"
#include "XMLString.h"

namespace pyxerces {

class QNameDefVisitor
: public boost::python::def_visitor<QNameDefVisitor> {
friend class def_visitor_access;

public:
template <class T>
void visit(T& class_) const {
	class_
	.def("setName", static_cast<void(*)(xercesc::QName&, const XMLString&, const XMLString&, const unsigned int)>(&QNameDefVisitor::setName))
	.def("setName", static_cast<void(*)(xercesc::QName&, const XMLString&, const unsigned int)>(&QNameDefVisitor::setName))
	.def("setPrefix", &QNameDefVisitor::setPrefix)
	.def("setLocalPart", &QNameDefVisitor::setLocalPart)
	;
}

static void setName(xercesc::QName& self, const XMLString& prefix, const XMLString& localPart, const unsigned int uriId) {
	self.setName(prefix.ptr(), localPart.ptr(), uriId);
}

static void setName(xercesc::QName& self, const XMLString& rawName, const unsigned int uriId) {
	self.setName(rawName.ptr(), uriId);
}

static void setPrefix(xercesc::QName& self, const XMLString& prefix) {
	self.setPrefix(prefix.ptr());
}

static void setLocalPart(xercesc::QName& self, const XMLString& localPart) {
	self.setLocalPart(localPart.ptr());
}

};

xercesc::QName* QName_fromstring_manager(const XMLString& prefix, const XMLString& localPart, const unsigned int uriId, xercesc::MemoryManager* const manager) {
	return new xercesc::QName(prefix.ptr(), localPart.ptr(), uriId, manager);
}

xercesc::QName* QName_fromstring(const XMLString& prefix, const XMLString& localPart, const unsigned int uriId) {
	return QName_fromstring_manager(prefix, localPart, uriId, xercesc::XMLPlatformUtils::fgMemoryManager);
}

void QName_init(void) {
	//! xercesc::QName
	boost::python::class_<xercesc::QName, boost::noncopyable, boost::python::bases<xercesc::XSerializable> >("QName", boost::python::init<boost::python::optional<xercesc::MemoryManager* const> >())
			.def(QNameDefVisitor())
			.def(boost::python::init<const XMLCh* const, const XMLCh* const, const unsigned int, boost::python::optional<xercesc::MemoryManager* const> >())
			.def(boost::python::init<const XMLCh* const, const unsigned int, boost::python::optional<xercesc::MemoryManager* const> >())
			.def(boost::python::init<const xercesc::QName&>())
			.def("__init__", boost::python::make_constructor(&QName_fromstring_manager))
			.def("__init__", boost::python::make_constructor(&QName_fromstring))
			.def("getPrefix", static_cast<const XMLCh*(xercesc::QName::*)(void) const>(&xercesc::QName::getPrefix), boost::python::return_value_policy<boost::python::return_by_value>())
			.def("getLocalPart", static_cast<const XMLCh*(xercesc::QName::*)(void) const>(&xercesc::QName::getLocalPart), boost::python::return_value_policy<boost::python::return_by_value>())
			.def("getURI", &xercesc::QName::getURI)
			.def("getRawName", static_cast<const XMLCh*(xercesc::QName::*)(void) const>(&xercesc::QName::getRawName), boost::python::return_value_policy<boost::python::return_by_value>())
			.def("getMemoryManager", &xercesc::QName::getMemoryManager, boost::python::return_value_policy<boost::python::reference_existing_object>())
			.def("setName", static_cast<void(xercesc::QName::*)(const XMLCh* const, const XMLCh* const, const unsigned int)>(&xercesc::QName::setName))
			.def("setName", static_cast<void(xercesc::QName::*)(const XMLCh* const, const unsigned int)>(&xercesc::QName::setName))
			.def("setPrefix", &xercesc::QName::setPrefix)
			.def("setLocalPart", &xercesc::QName::setLocalPart)
			.def("setNPrefix", &xercesc::QName::setNPrefix)
			.def("setNLocalPart", &xercesc::QName::setNLocalPart)
			.def("setURI", &xercesc::QName::setURI)
			.def("setValues", &xercesc::QName::setValues)
			.def("__eq__", &xercesc::QName::operator==)
			.def("cleanUp", &xercesc::QName::cleanUp)
			PyDECL_XSERIALIZABLE(QName)
			;
}

} /* namespace pyxerces */
