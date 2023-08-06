/*
 * XMLBuffer.cpp
 *
 *  Created on: 2013/02/26
 *      Author: mugwort_rc
 */

#include "XMLBuffer.h"

#include <boost/python.hpp>
#include <xercesc/framework/XMLBuffer.hpp>

#include "../util/XMLString.h"

namespace pyxerces {

class XMLBufferDefVisitor
: public boost::python::def_visitor<XMLBufferDefVisitor> {
friend class def_visitor_access;

public:
template <class T>
void visit(T& class_) const {
	class_
	.def("append", static_cast<void(*)(xercesc::XMLBuffer&, const XMLString&)>(&XMLBufferDefVisitor::append))
	.def("set", static_cast<void(*)(xercesc::XMLBuffer&, const XMLString&)>(&XMLBufferDefVisitor::set))
	;
}

static void append(xercesc::XMLBuffer& self, const XMLString& chars) {
	self.append(chars.ptr());
}

static void set(xercesc::XMLBuffer& self, const XMLString& chars) {
	self.set(chars.ptr());
}

};

class XMLBufferFullHandlerWrapper
: public xercesc::XMLBufferFullHandler, public boost::python::wrapper<xercesc::XMLBufferFullHandler>
{
public:
bool bufferFull(xercesc::XMLBuffer& buffer) {
	return this->get_override("bufferFull")(boost::ref(buffer));
}

};

void XMLBuffer_init(void) {
	//! xercesc::XMLBuffer
	boost::python::class_<xercesc::XMLBuffer, boost::noncopyable>("XMLBuffer", boost::python::init<boost::python::optional<const XMLSize_t, xercesc::MemoryManager* const> >())
			.def(XMLBufferDefVisitor())
			.def("setFullHandler", &xercesc::XMLBuffer::setFullHandler)
			.def("append", static_cast<void(xercesc::XMLBuffer::*)(const XMLCh)>(&xercesc::XMLBuffer::append))
			.def("append", static_cast<void(xercesc::XMLBuffer::*)(const XMLCh* const, const XMLSize_t)>(&xercesc::XMLBuffer::append))
			.def("append", static_cast<void(xercesc::XMLBuffer::*)(const XMLCh* const)>(&xercesc::XMLBuffer::append))
			.def("set", static_cast<void(xercesc::XMLBuffer::*)(const XMLCh* const, const XMLSize_t)>(&xercesc::XMLBuffer::set))
			.def("set", static_cast<void(xercesc::XMLBuffer::*)(const XMLCh* const)>(&xercesc::XMLBuffer::set))
			.def("getRawBuffer", static_cast<const XMLCh*(xercesc::XMLBuffer::*)(void) const>(&xercesc::XMLBuffer::getRawBuffer), boost::python::return_value_policy<boost::python::return_by_value>())
			.def("reset", &xercesc::XMLBuffer::reset)
			.def("getInUse", &xercesc::XMLBuffer::getInUse)
			.def("getLen", &xercesc::XMLBuffer::getLen)
			.def("isEmpty", &xercesc::XMLBuffer::isEmpty)
			.def("setInUse", &xercesc::XMLBuffer::setInUse)
			;
	//! xercesc::XMLBufferFullHandler
	boost::python::class_<XMLBufferFullHandlerWrapper, boost::noncopyable>("XMLBufferFullHandler")
			.def("bufferFull", &xercesc::XMLBufferFullHandler::bufferFull)
			;
}

} /* namespace pyxerces */
