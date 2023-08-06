/*
 * XMLResourceIdentifier.cpp
 *
 *  Created on: 2013/03/14
 *      Author: mugwort_rc
 */

#include "XMLResourceIdentifier.h"

#include <boost/python.hpp>

//! for forward declaration
#include <xercesc/sax/Locator.hpp>

#include <xercesc/util/XMLResourceIdentifier.hpp>

#include "XMLString.h"

namespace pyxerces {

class XMLResourceIdentifierDefVisitor
: public boost::python::def_visitor<XMLResourceIdentifierDefVisitor>
{
friend class def_visitor_access;
public:
template <class T>
void visit(T& class_) const {
	class_
	.def("__init__", boost::python::make_constructor(static_cast<xercesc::XMLResourceIdentifier*(*)(const xercesc::XMLResourceIdentifier::ResourceIdentifierType, const XMLString&, const XMLString&, const XMLString&, const XMLString&, const xercesc::Locator*)>(&XMLResourceIdentifier_fromstring)))
	.def("__init__", boost::python::make_constructor(static_cast<xercesc::XMLResourceIdentifier*(*)(const xercesc::XMLResourceIdentifier::ResourceIdentifierType, const XMLString&, const XMLString&, const XMLString&, const XMLString&)>(&XMLResourceIdentifier_fromstring)))
	.def("__init__", boost::python::make_constructor(static_cast<xercesc::XMLResourceIdentifier*(*)(const xercesc::XMLResourceIdentifier::ResourceIdentifierType, const XMLString&, const XMLString&, const XMLString&)>(&XMLResourceIdentifier_fromstring)))
	.def("__init__", boost::python::make_constructor(static_cast<xercesc::XMLResourceIdentifier*(*)(const xercesc::XMLResourceIdentifier::ResourceIdentifierType, const XMLString&, const XMLString&)>(&XMLResourceIdentifier_fromstring)))
	.def("__init__", boost::python::make_constructor(static_cast<xercesc::XMLResourceIdentifier*(*)(const xercesc::XMLResourceIdentifier::ResourceIdentifierType, const XMLString&)>(&XMLResourceIdentifier_fromstring)))
	;
}

static xercesc::XMLResourceIdentifier* XMLResourceIdentifier_fromstring(const xercesc::XMLResourceIdentifier::ResourceIdentifierType resourceIdentitiferType, const XMLString& systemId, const XMLString& nameSpace, const XMLString& publicId, const XMLString& baseURI, const xercesc::Locator* locator) {
	return new xercesc::XMLResourceIdentifier(resourceIdentitiferType, systemId.ptr(), nameSpace.ptr(), publicId.ptr(), baseURI.ptr(), locator);
}

static xercesc::XMLResourceIdentifier* XMLResourceIdentifier_fromstring(const xercesc::XMLResourceIdentifier::ResourceIdentifierType resourceIdentitiferType, const XMLString& systemId, const XMLString& nameSpace, const XMLString& publicId, const XMLString& baseURI) {
	return XMLResourceIdentifier_fromstring(resourceIdentitiferType, systemId, nameSpace, publicId, baseURI, nullptr);
}

static xercesc::XMLResourceIdentifier* XMLResourceIdentifier_fromstring(const xercesc::XMLResourceIdentifier::ResourceIdentifierType resourceIdentitiferType, const XMLString& systemId, const XMLString& nameSpace, const XMLString& publicId) {
	return XMLResourceIdentifier_fromstring(resourceIdentitiferType, systemId, nameSpace, publicId, nullptr);
}

static xercesc::XMLResourceIdentifier* XMLResourceIdentifier_fromstring(const xercesc::XMLResourceIdentifier::ResourceIdentifierType resourceIdentitiferType, const XMLString& systemId, const XMLString& nameSpace) {
	return XMLResourceIdentifier_fromstring(resourceIdentitiferType, systemId, nameSpace, nullptr);
}

static xercesc::XMLResourceIdentifier* XMLResourceIdentifier_fromstring(const xercesc::XMLResourceIdentifier::ResourceIdentifierType resourceIdentitiferType, const XMLString& systemId) {
	return XMLResourceIdentifier_fromstring(resourceIdentitiferType, systemId, nullptr);
}

};

void XMLResourceIdentifier_init(void) {
	//! xercesc::XMLResourceIdentifier
	auto XMLResourceIdentifier = boost::python::class_<xercesc::XMLResourceIdentifier, boost::noncopyable>("XMLResourceIdentifier", boost::python::init<const xercesc::XMLResourceIdentifier::ResourceIdentifierType, const XMLCh* const, boost::python::optional<const XMLCh* const, const XMLCh* const, const XMLCh* const, const xercesc::Locator*> >())
			.def(XMLResourceIdentifierDefVisitor())
			.def("getResourceIdentifierType", &xercesc::XMLResourceIdentifier::getResourceIdentifierType)
			.def("getPublicId", &xercesc::XMLResourceIdentifier::getPublicId, boost::python::return_value_policy<boost::python::return_by_value>())
			.def("getSystemId", &xercesc::XMLResourceIdentifier::getSystemId, boost::python::return_value_policy<boost::python::return_by_value>())
			.def("getSchemaLocation", &xercesc::XMLResourceIdentifier::getSchemaLocation, boost::python::return_value_policy<boost::python::return_by_value>())
			.def("getBaseURI", &xercesc::XMLResourceIdentifier::getBaseURI, boost::python::return_value_policy<boost::python::return_by_value>())
			.def("getNameSpace", &xercesc::XMLResourceIdentifier::getNameSpace, boost::python::return_value_policy<boost::python::return_by_value>())
			.def("getLocator", &xercesc::XMLResourceIdentifier::getLocator, boost::python::return_value_policy<boost::python::reference_existing_object>())
			;
	boost::python::scope XMLResourceIdentifierScope = XMLResourceIdentifier;
	//! xercesc::XMLResourceIdentifier::ResourceIdentifierType
	boost::python::enum_<xercesc::XMLResourceIdentifier::ResourceIdentifierType>("ResourceIdentifierType")
			.value("SchemaGrammar", xercesc::XMLResourceIdentifier::SchemaGrammar)
			.value("SchemaImport", xercesc::XMLResourceIdentifier::SchemaImport)
			.value("SchemaInclude", xercesc::XMLResourceIdentifier::SchemaInclude)
			.value("SchemaRedefine", xercesc::XMLResourceIdentifier::SchemaRedefine)
			.value("ExternalEntity", xercesc::XMLResourceIdentifier::ExternalEntity)
			.value("UnKnown", xercesc::XMLResourceIdentifier::UnKnown)
			.export_values()
			;
}

} /* namespace pyxerces */
