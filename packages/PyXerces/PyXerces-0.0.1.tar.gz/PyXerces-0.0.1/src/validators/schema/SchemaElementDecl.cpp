/*
 * SchemaElementDecl.cpp
 *
 *  Created on: 2013/03/03
 *      Author: mugwort_rc
 */

#include "SchemaElementDecl.h"

#include <boost/python.hpp>

//! for forward declaration
#include <xercesc/validators/common/ContentSpecNode.hpp>
#include <xercesc/validators/schema/SchemaAttDefList.hpp>

#include <xercesc/validators/schema/SchemaElementDecl.hpp>

#include "../../internal/XSerializable.h"
#include "../../util/XMLString.h"

namespace pyxerces {

class SchemaElementDeclDefVisitor
: public boost::python::def_visitor<SchemaElementDeclDefVisitor>
{
friend class def_visitor_access;
public:
template <class T>
void visit(T& class_) const {
	class_
	.def("__init__", boost::python::make_constructor(static_cast<xercesc::SchemaElementDecl*(*)(const XMLString&, const XMLString&, const int, const xercesc::SchemaElementDecl::ModelTypes, const unsigned int, xercesc::MemoryManager* const)>(&SchemaElementDecl_fromstring)))
	.def("__init__", boost::python::make_constructor(static_cast<xercesc::SchemaElementDecl*(*)(const XMLString&, const XMLString&, const int, const xercesc::SchemaElementDecl::ModelTypes, const unsigned int)>(&SchemaElementDecl_fromstring)))
	.def("__init__", boost::python::make_constructor(static_cast<xercesc::SchemaElementDecl*(*)(const XMLString&, const XMLString&, const int, const xercesc::SchemaElementDecl::ModelTypes)>(&SchemaElementDecl_fromstring)))
	.def("__init__", boost::python::make_constructor(static_cast<xercesc::SchemaElementDecl*(*)(const XMLString&, const XMLString&, const int)>(&SchemaElementDecl_fromstring)))
	.def("getAttDef", &SchemaElementDeclDefVisitor::getAttDef, boost::python::return_value_policy<boost::python::reference_existing_object>())
	.def("setDefaultValue", &SchemaElementDeclDefVisitor::setDefaultValue)
	;
}

static xercesc::SchemaElementDecl* SchemaElementDecl_fromstring(const XMLString& prefix, const XMLString& localPart, const int uriId, const xercesc::SchemaElementDecl::ModelTypes modelType, const unsigned int enclosingScope, xercesc::MemoryManager* const manager) {
	return new xercesc::SchemaElementDecl(prefix.ptr(), localPart.ptr(), uriId, modelType, enclosingScope, manager);
}

static xercesc::SchemaElementDecl* SchemaElementDecl_fromstring(const XMLString& prefix, const XMLString& localPart, const int uriId, const xercesc::SchemaElementDecl::ModelTypes modelType, const unsigned int enclosingScope) {
	return SchemaElementDecl_fromstring(prefix, localPart, uriId, modelType, enclosingScope, xercesc::XMLPlatformUtils::fgMemoryManager);
}

static xercesc::SchemaElementDecl* SchemaElementDecl_fromstring(const XMLString& prefix, const XMLString& localPart, const int uriId, const xercesc::SchemaElementDecl::ModelTypes modelType) {
	return SchemaElementDecl_fromstring(prefix, localPart, uriId, modelType, xercesc::Grammar::TOP_LEVEL_SCOPE);
}

static xercesc::SchemaElementDecl* SchemaElementDecl_fromstring(const XMLString& prefix, const XMLString& localPart, const int uriId) {
	return SchemaElementDecl_fromstring(prefix, localPart, uriId, xercesc::SchemaElementDecl::Any);
}

static xercesc::SchemaAttDef* getAttDef(xercesc::SchemaElementDecl& self, const XMLString& baseName, const int uriId) {
	return self.getAttDef(baseName.ptr(), uriId);
}

static void setDefaultValue(xercesc::SchemaElementDecl& self, const XMLString& value) {
	self.setDefaultValue(value.ptr());
}

};

void SchemaElementDecl_init(void) {
	//! xercesc::SchemaElementDecl
	auto SchemaElementDecl = boost::python::class_<xercesc::SchemaElementDecl, boost::noncopyable, boost::python::bases<xercesc::XMLElementDecl> >("SchemaElementDecl", boost::python::init<boost::python::optional<xercesc::MemoryManager* const> >())
			.def(boost::python::init<const XMLCh* const, const XMLCh* const, const int, boost::python::optional<const xercesc::SchemaElementDecl::ModelTypes, const unsigned int, xercesc::MemoryManager* const> >())
			.def(boost::python::init<const xercesc::QName* const, boost::python::optional<const xercesc::SchemaElementDecl::ModelTypes, const unsigned int, xercesc::MemoryManager* const> >())
			.def(SchemaElementDeclDefVisitor())
			.def("getAttDefList", &xercesc::SchemaElementDecl::getAttDefList, boost::python::return_internal_reference<>())
			.def("getCharDataOpts", &xercesc::SchemaElementDecl::getCharDataOpts)
			.def("hasAttDefs", &xercesc::SchemaElementDecl::hasAttDefs)
			.def("getContentSpec", static_cast<xercesc::ContentSpecNode*(xercesc::SchemaElementDecl::*)(void)>(&xercesc::SchemaElementDecl::getContentSpec), boost::python::return_value_policy<boost::python::reference_existing_object>())
			.def("setContentSpec", &xercesc::SchemaElementDecl::setContentSpec)
			.def("getContentModel", &xercesc::SchemaElementDecl::getContentModel, boost::python::return_value_policy<boost::python::reference_existing_object>())
			.def("setContentModel", &xercesc::SchemaElementDecl::setContentModel)
			.def("getFormattedContentModel", &xercesc::SchemaElementDecl::getFormattedContentModel, boost::python::return_value_policy<boost::python::return_by_value>())
			.def("getAttDef", static_cast<xercesc::SchemaAttDef*(xercesc::SchemaElementDecl::*)(const XMLCh* const, const int)>(&xercesc::SchemaElementDecl::getAttDef), boost::python::return_value_policy<boost::python::reference_existing_object>())
			.def("getAttWildCard", static_cast<xercesc::SchemaAttDef*(xercesc::SchemaElementDecl::*)()>(&xercesc::SchemaElementDecl::getAttWildCard), boost::python::return_value_policy<boost::python::reference_existing_object>())
			.def("getModelType", &xercesc::SchemaElementDecl::getModelType)
			.def("getPSVIScope", &xercesc::SchemaElementDecl::getPSVIScope)
			.def("getDatatypeValidator", &xercesc::SchemaElementDecl::getDatatypeValidator, boost::python::return_value_policy<boost::python::reference_existing_object>())
			.def("getEnclosingScope", &xercesc::SchemaElementDecl::getEnclosingScope)
			.def("getFinalSet", &xercesc::SchemaElementDecl::getFinalSet)
			.def("getBlockSet", &xercesc::SchemaElementDecl::getBlockSet)
			.def("getMiscFlags", &xercesc::SchemaElementDecl::getMiscFlags)
			.def("getDefaultValue", &xercesc::SchemaElementDecl::getDefaultValue, boost::python::return_value_policy<boost::python::return_by_value>())
			.def("getComplexTypeInfo", &xercesc::SchemaElementDecl::getComplexTypeInfo, boost::python::return_value_policy<boost::python::reference_existing_object>())
			.def("isGlobalDecl", &xercesc::SchemaElementDecl::isGlobalDecl)
			.def("getSubstitutionGroupElem", &xercesc::SchemaElementDecl::getSubstitutionGroupElem, boost::python::return_value_policy<boost::python::reference_existing_object>())
			.def("setModelType", &xercesc::SchemaElementDecl::setModelType)
			.def("setPSVIScope", &xercesc::SchemaElementDecl::setPSVIScope)
			.def("setDatatypeValidator", &xercesc::SchemaElementDecl::setDatatypeValidator)
			.def("setEnclosingScope", &xercesc::SchemaElementDecl::setEnclosingScope)
			.def("setFinalSet", &xercesc::SchemaElementDecl::setFinalSet)
			.def("setBlockSet", &xercesc::SchemaElementDecl::setBlockSet)
			.def("setMiscFlags", &xercesc::SchemaElementDecl::setMiscFlags)
			.def("setDefaultValue", &xercesc::SchemaElementDecl::setDefaultValue)
			.def("setComplexTypeInfo", &xercesc::SchemaElementDecl::setComplexTypeInfo)
			.def("setAttWildCard", &xercesc::SchemaElementDecl::setAttWildCard)
			.def("setSubstitutionGroupElem", &xercesc::SchemaElementDecl::setSubstitutionGroupElem)
			.def("addIdentityConstraint", &xercesc::SchemaElementDecl::addIdentityConstraint)
			.def("getIdentityConstraintCount", &xercesc::SchemaElementDecl::getIdentityConstraintCount)
			.def("getIdentityConstraintAt", &xercesc::SchemaElementDecl::getIdentityConstraintAt, boost::python::return_value_policy<boost::python::reference_existing_object>())
			PyDECL_XSERIALIZABLE(SchemaElementDecl)
			.def("getObjectType", &xercesc::SchemaElementDecl::getObjectType)
			;
	boost::python::scope SchemaElementDeclScope = SchemaElementDecl;
	//! xercesc::SchemaElementDecl::ModelTypes
	boost::python::enum_<xercesc::SchemaElementDecl::ModelTypes>("ModelTypes")
			.value("Empty", xercesc::SchemaElementDecl::Empty)
			.value("Any", xercesc::SchemaElementDecl::Any)
			.value("Mixed_Simple", xercesc::SchemaElementDecl::Mixed_Simple)
			.value("Mixed_Complex", xercesc::SchemaElementDecl::Mixed_Complex)
			.value("Children", xercesc::SchemaElementDecl::Children)
			.value("Simple", xercesc::SchemaElementDecl::Simple)
			.value("ElementOnlyEmpty", xercesc::SchemaElementDecl::ElementOnlyEmpty)
			.value("ModelTypes_Count", xercesc::SchemaElementDecl::ModelTypes_Count)
			.export_values()
			;
}

} /* namespace pyxerces */
