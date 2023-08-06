/*
 * Attributes.cpp
 *
 *  Created on: 2013/03/14
 *      Author: mugwort_rc
 */

#include "Attributes.h"

#include <boost/python.hpp>
#include <xercesc/sax2/Attributes.hpp>

#include "../util/XMLString.h"

namespace pyxerces {

class AttributesDefVisitor
: public boost::python::def_visitor<AttributesDefVisitor>
{
friend class def_visitor_access;
public:
template <class T>
void visit(T& class_) const {
	class_
	.def("getIndex", static_cast<boost::python::tuple(*)(xercesc::Attributes&, const XMLString&, const XMLString&)>(&AttributesDefVisitor::getIndex))
	.def("getIndex", static_cast<boost::python::tuple(*)(xercesc::Attributes&, const XMLString&)>(&AttributesDefVisitor::getIndex))
	.def("getType", static_cast<const XMLCh*(*)(xercesc::Attributes&, const XMLString&, const XMLString&)>(&AttributesDefVisitor::getType), boost::python::return_value_policy<boost::python::return_by_value>())
	.def("getType", static_cast<const XMLCh*(*)(xercesc::Attributes&, const XMLString&)>(&AttributesDefVisitor::getType), boost::python::return_value_policy<boost::python::return_by_value>())
	.def("getValue", static_cast<const XMLCh*(*)(xercesc::Attributes&, const XMLString&, const XMLString&)>(&AttributesDefVisitor::getValue), boost::python::return_value_policy<boost::python::return_by_value>())
	.def("getValue", static_cast<const XMLCh*(*)(xercesc::Attributes&, const XMLString&)>(&AttributesDefVisitor::getValue), boost::python::return_value_policy<boost::python::return_by_value>())
	;
}

static boost::python::tuple getIndex(xercesc::Attributes& self, const XMLString& uri, const XMLString& localPart ) {
	XMLSize_t ind;
	bool ret =  self.getIndex(uri.ptr(), localPart.ptr(), ind);
	return boost::python::make_tuple(ret, ind);
}

static boost::python::tuple getIndex(xercesc::Attributes& self, const XMLString& qName ) {
	XMLSize_t ind;
	bool ret = self.getIndex(qName.ptr(), ind);
	return boost::python::make_tuple(ret, ind);
}

static const XMLCh* getType(xercesc::Attributes& self, const XMLString& uri, const XMLString& localPart ) {
	return self.getType(uri.ptr(), localPart.ptr());
}

static const XMLCh* getType(xercesc::Attributes& self, const XMLString& qName) {
	return self.getType(qName.ptr());
}

static const XMLCh* getValue(xercesc::Attributes& self, const XMLString& uri, const XMLString& localPart ) {
	return self.getValue(uri.ptr(), localPart.ptr());
}

static const XMLCh* getValue(xercesc::Attributes& self, const XMLString& qName) {
	return self.getValue(qName.ptr());
}

};

class AttributesWrapper
: public xercesc::Attributes, public boost::python::wrapper<xercesc::Attributes>
{
public:
XMLSize_t getLength() const {
	return this->get_override("getLength")();
}

const XMLCh* getURI(const XMLSize_t index) const {
	return this->get_override("getURI")(index);
}

const XMLCh* getLocalName(const XMLSize_t index) const {
	return this->get_override("getLocalName")(index);
}

const XMLCh* getQName(const XMLSize_t index) const {
	return this->get_override("getQName")(index);
}

const XMLCh* getType(const XMLSize_t index) const {
	return this->get_override("getType")(index);
}

const XMLCh* getValue(const XMLSize_t index) const {
	return this->get_override("getValue")(index);
}

bool getIndex(const XMLCh* const uri, const XMLCh* const localPart, XMLSize_t& index) const {
	boost::python::tuple ret = this->get_override("getIndex")(XMLString(uri), XMLString(localPart));
	index = boost::python::extract<XMLSize_t>(ret[1]);
	return boost::python::extract<bool>(ret[0]);
}

int getIndex(const XMLCh* const uri, const XMLCh* const localPart ) const {
	boost::python::tuple ret = this->get_override("getIndex")(XMLString(uri), XMLString(localPart));
	return boost::python::extract<XMLSize_t>(ret[1]);
}

bool getIndex(const XMLCh* const qName, XMLSize_t& index) const {
	boost::python::tuple ret = this->get_override("getIndex")(XMLString(qName));
	index = boost::python::extract<XMLSize_t>(ret[1]);
	return boost::python::extract<bool>(ret[0]);
}

int getIndex(const XMLCh* const qName ) const {
	boost::python::tuple ret = this->get_override("getIndex")(XMLString(qName));
	return boost::python::extract<XMLSize_t>(ret[1]);
}

const XMLCh* getType(const XMLCh* const uri, const XMLCh* const localPart ) const {
	return this->get_override("getType")(XMLString(uri), XMLString(localPart));
}

const XMLCh* getType(const XMLCh* const qName) const {
	return this->get_override("getType")(XMLString(qName));
}

const XMLCh* getValue(const XMLCh* const uri, const XMLCh* const localPart ) const {
	return this->get_override("getValue")(XMLString(uri), XMLString(localPart));
}

const XMLCh* getValue(const XMLCh* const qName) const {
	return this->get_override("getValue")(XMLString(qName));
}

};

void Attributes_init(void) {
	//! xercesc::Attributes
	boost::python::class_<AttributesWrapper, boost::noncopyable>("Attributes")
			.def(AttributesDefVisitor())
			.def("getLength", boost::python::pure_virtual(&xercesc::Attributes::getLength))
			.def("getURI", boost::python::pure_virtual(&xercesc::Attributes::getURI), boost::python::return_value_policy<boost::python::return_by_value>())
			.def("getLocalName", boost::python::pure_virtual(&xercesc::Attributes::getLocalName), boost::python::return_value_policy<boost::python::return_by_value>())
			.def("getQName", boost::python::pure_virtual(&xercesc::Attributes::getQName), boost::python::return_value_policy<boost::python::return_by_value>())
			.def("getType", boost::python::pure_virtual(static_cast<const XMLCh*(xercesc::Attributes::*)(const XMLSize_t) const>(&xercesc::Attributes::getType)), boost::python::return_value_policy<boost::python::return_by_value>())
			.def("getValue", boost::python::pure_virtual(static_cast<const XMLCh*(xercesc::Attributes::*)(const XMLSize_t) const>(&xercesc::Attributes::getValue)), boost::python::return_value_policy<boost::python::return_by_value>())
			//.def("getIndex", static_cast<bool(xercesc::Attributes::*)(const XMLCh* const, const XMLCh* const, XMLSize_t&) const>(&xercesc::Attributes::getIndex))
			//! @sa AttributesDefVisitor
			.def("getIndex", boost::python::pure_virtual(static_cast<int(xercesc::Attributes::*)(const XMLCh* const, const XMLCh* const) const>(&xercesc::Attributes::getIndex)))
			//.def("getIndex", static_cast<bool(xercesc::Attributes::*)(const XMLCh* const, XMLSize_t&) const>(&xercesc::Attributes::getIndex))
			//.def("getIndex", static_cast<int(xercesc::Attributes::*)(const XMLCh* const) const>(&xercesc::Attributes::getIndex))
			.def("getType", boost::python::pure_virtual(static_cast<const XMLCh*(xercesc::Attributes::*)(const XMLCh* const, const XMLCh* const) const>(&xercesc::Attributes::getType)), boost::python::return_value_policy<boost::python::return_by_value>())
			.def("getType", boost::python::pure_virtual(static_cast<const XMLCh*(xercesc::Attributes::*)(const XMLCh* const) const>(&xercesc::Attributes::getType)), boost::python::return_value_policy<boost::python::return_by_value>())
			.def("getValue", boost::python::pure_virtual(static_cast<const XMLCh*(xercesc::Attributes::*)(const XMLCh* const, const XMLCh* const) const>(&xercesc::Attributes::getValue)), boost::python::return_value_policy<boost::python::return_by_value>())
			.def("getValue", boost::python::pure_virtual(static_cast<const XMLCh*(xercesc::Attributes::*)(const XMLCh* const) const>(&xercesc::Attributes::getValue)), boost::python::return_value_policy<boost::python::return_by_value>())
			;
}

} /* namespace pyxerces */
