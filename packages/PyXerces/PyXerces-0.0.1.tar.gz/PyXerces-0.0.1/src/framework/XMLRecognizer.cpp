/*
 * XMLRecognizer.cpp
 *
 *  Created on: 2013/02/26
 *      Author: mugwort_rc
 */

#include "XMLRecognizer.h"

#include <boost/python.hpp>

//!< for forward declaration
#include <xercesc/framework/MemoryManager.hpp>

#include <xercesc/framework/XMLRecognizer.hpp>

#include "../util/XMLString.h"

namespace pyxerces {

class XMLRecognizerDefVisitor
: public boost::python::def_visitor<XMLRecognizerDefVisitor> {
friend class def_visitor_access;

public:
template <class T>
void visit(T& class_) const {
	class_
	.def("basicEncodingProbe", static_cast<xercesc::XMLRecognizer::Encodings(*)(const std::string&)>(&XMLRecognizerDefVisitor::basicEncodingProbe))
	;
}

static xercesc::XMLRecognizer::Encodings basicEncodingProbe(const std::string& rawBuffer) {
	return xercesc::XMLRecognizer::basicEncodingProbe(reinterpret_cast<const unsigned char*>(rawBuffer.c_str()), rawBuffer.size());
}

};

class XMLRecognizerStringDefVisitor
: public boost::python::def_visitor<XMLRecognizerStringDefVisitor> {
friend class def_visitor_access;

public:
template <class T>
void visit(T& class_) const {
	class_
	.def("encodingForName", &XMLRecognizerStringDefVisitor::encodingForName)
	;
}

static xercesc::XMLRecognizer::Encodings encodingForName(const XMLString& theEncName) {
	return xercesc::XMLRecognizer::encodingForName(theEncName.ptr());
}

};

BOOST_PYTHON_FUNCTION_OVERLOADS(XMLRecognizerNameForEncodingOverloads, xercesc::XMLRecognizer::nameForEncoding, 1, 2)

void XMLRecognizer_init(void) {
	//! xercesc::XMLRecognizer
	auto XMLRecognizer = boost::python::class_<xercesc::XMLRecognizer, boost::noncopyable>("XMLRecognizer", boost::python::no_init)
			.def(XMLRecognizerDefVisitor())
			.def(XMLRecognizerStringDefVisitor())
			.def("basicEncodingProbe", &xercesc::XMLRecognizer::basicEncodingProbe)
			.def("encodingForName", &xercesc::XMLRecognizer::encodingForName)
			.def("nameForEncoding", &xercesc::XMLRecognizer::nameForEncoding, XMLRecognizerNameForEncodingOverloads()[boost::python::return_value_policy<boost::python::return_by_value>()])
			.staticmethod("basicEncodingProbe")
			.staticmethod("encodingForName")
			.staticmethod("nameForEncoding")
			.setattr("fgASCIIPre", reinterpret_cast<const char*>(xercesc::XMLRecognizer::fgASCIIPre))
			.setattr("fgASCIIPreLen", xercesc::XMLRecognizer::fgASCIIPreLen)
			.setattr("fgEBCDICPre", reinterpret_cast<const char*>(xercesc::XMLRecognizer::fgEBCDICPre))
			.setattr("fgEBCDICPreLen", xercesc::XMLRecognizer::fgEBCDICPreLen)
			.setattr("fgUTF16BPre", reinterpret_cast<const char*>(xercesc::XMLRecognizer::fgUTF16BPre))
			.setattr("fgUTF16LPre", reinterpret_cast<const char*>(xercesc::XMLRecognizer::fgUTF16LPre))
			.setattr("fgUTF16PreLen", xercesc::XMLRecognizer::fgUTF16PreLen)
			.setattr("fgUCS4BPre", reinterpret_cast<const char*>(xercesc::XMLRecognizer::fgUCS4BPre))
			.setattr("fgUCS4LPre", reinterpret_cast<const char*>(xercesc::XMLRecognizer::fgUCS4LPre))
			.setattr("fgUCS4PreLen", xercesc::XMLRecognizer::fgUCS4PreLen)
			.setattr("fgUTF8BOM", reinterpret_cast<const char*>(xercesc::XMLRecognizer::fgUTF8BOM))
			.setattr("fgUTF8BOMLen", xercesc::XMLRecognizer::fgUTF8BOMLen)
			;
	boost::python::scope XMLRecognizerScope = XMLRecognizer;
	//! xercesc::XMLRecognizer::Encodings
	boost::python::enum_<xercesc::XMLRecognizer::Encodings>("Encodings")
			.value("EBCDIC", xercesc::XMLRecognizer::EBCDIC)
			.value("UCS_4B", xercesc::XMLRecognizer::UCS_4B)
			.value("UCS_4L", xercesc::XMLRecognizer::UCS_4L)
			.value("US_ASCII", xercesc::XMLRecognizer::US_ASCII)
			.value("UTF_8", xercesc::XMLRecognizer::UTF_8)
			.value("UTF_16B", xercesc::XMLRecognizer::UTF_16B)
			.value("UTF_16L", xercesc::XMLRecognizer::UTF_16L)
			.value("XERCES_XMLCH", xercesc::XMLRecognizer::XERCES_XMLCH)
			.value("Encodings_Count", xercesc::XMLRecognizer::Encodings_Count)
			.value("Encodings_Min", xercesc::XMLRecognizer::Encodings_Min)
			.value("Encodings_Max", xercesc::XMLRecognizer::Encodings_Max)
			.value("OtherEncoding", xercesc::XMLRecognizer::OtherEncoding)
			.export_values()
			;
}

} /* namespace pyxerces */
