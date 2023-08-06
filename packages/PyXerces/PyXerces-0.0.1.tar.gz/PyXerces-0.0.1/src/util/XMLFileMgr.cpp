/*
 * XMLFileMgr.cpp
 *
 *  Created on: 2013/02/23
 *      Author: mugwort_rc
 */

#include "XMLFileMgr.h"

#include <boost/python.hpp>

//! for forward declaration
#include <xercesc/framework/MemoryManager.hpp>

#include <xercesc/util/XMLFileMgr.hpp>

namespace pyxerces {

class XMLFileMgrWrapper
: public xercesc::XMLFileMgr, public boost::python::wrapper<xercesc::XMLFileMgr>
{
public:
xercesc::FileHandle	fileOpen(const XMLCh* path, bool toWrite, xercesc::MemoryManager* const manager) {
	return this->get_override("fileOpen")(path, toWrite, manager);
}

xercesc::FileHandle	fileOpen(const char* path, bool toWrite, xercesc::MemoryManager* const manager) {
	return this->get_override("fileOpen")(path, toWrite, manager);
}

xercesc::FileHandle	openStdIn(xercesc::MemoryManager* const manager) {
	return this->get_override("openStdIn")(manager);
}

void fileClose(xercesc::FileHandle f, xercesc::MemoryManager* const manager) {
	this->get_override("fileClose")(f, manager);
}

void fileReset(xercesc::FileHandle f, xercesc::MemoryManager* const manager) {
	this->get_override("fileReset")(f, manager);
}

XMLFilePos curPos(xercesc::FileHandle f, xercesc::MemoryManager* const manager) {
	return this->get_override("curPos")(f, manager);
}

XMLFilePos fileSize(xercesc::FileHandle f, xercesc::MemoryManager* const manager) {
	return this->get_override("fileSize")(f, manager);
}

XMLSize_t fileRead(xercesc::FileHandle f, XMLSize_t byteCount, XMLByte* buffer, xercesc::MemoryManager* const manager) {
	return this->get_override("fileRead")(f, byteCount, buffer, manager);
}

void fileWrite(xercesc::FileHandle f, XMLSize_t byteCount, const XMLByte* buffer, xercesc::MemoryManager* const manager) {
	this->get_override("fileWrite")(f, byteCount, buffer, manager);
}

XMLCh* getFullPath(const XMLCh* const srcPath, xercesc::MemoryManager* const manager) {
	return this->get_override("getFullPath")(srcPath, manager);
}

XMLCh* getCurrentDirectory(xercesc::MemoryManager* const manager) {
	return this->get_override("getCurrentDirectory")(manager);
}

bool isRelative(const XMLCh* const toCheck, xercesc::MemoryManager* const manager) {
	return this->get_override("isRelative")(toCheck, manager);
}
};

void XMLFileMgr_init(void) {
	//! xercesc::XMLFileMgr
	boost::python::class_<XMLFileMgrWrapper, boost::noncopyable>("XMLFileMgr")
			.def("fileOpen", boost::python::pure_virtual(static_cast<xercesc::FileHandle(xercesc::XMLFileMgr::*)(const XMLCh*, bool, xercesc::MemoryManager* const)>(&xercesc::XMLFileMgr::fileOpen)), boost::python::return_value_policy<boost::python::return_opaque_pointer>())  //!< void*
			.def("fileOpen", boost::python::pure_virtual(static_cast<xercesc::FileHandle(xercesc::XMLFileMgr::*)(const char*, bool, xercesc::MemoryManager* const)>(&xercesc::XMLFileMgr::fileOpen)), boost::python::return_value_policy<boost::python::return_opaque_pointer>())  //!< void*
			.def("fileOpen", boost::python::pure_virtual(&xercesc::XMLFileMgr::openStdIn), boost::python::return_value_policy<boost::python::return_opaque_pointer>())  //!< void*
			.def("fileClose", boost::python::pure_virtual(&xercesc::XMLFileMgr::fileClose))
			.def("fileReset", boost::python::pure_virtual(&xercesc::XMLFileMgr::fileReset))
			.def("curPos", boost::python::pure_virtual(&xercesc::XMLFileMgr::curPos))
			.def("fileSize", boost::python::pure_virtual(&xercesc::XMLFileMgr::fileSize))
			.def("fileRead", boost::python::pure_virtual(&xercesc::XMLFileMgr::fileRead))
			.def("fileWrite", boost::python::pure_virtual(&xercesc::XMLFileMgr::fileWrite))
			.def("getFullPath", boost::python::pure_virtual(&xercesc::XMLFileMgr::getFullPath), boost::python::return_value_policy<boost::python::return_opaque_pointer>())
			.def("getCurrentDirectory", boost::python::pure_virtual(&xercesc::XMLFileMgr::getCurrentDirectory), boost::python::return_value_policy<boost::python::return_opaque_pointer>())
			.def("isRelative", boost::python::pure_virtual(&xercesc::XMLFileMgr::isRelative))
			;
}

} /* namespace pyxerces */
