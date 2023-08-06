/*
 * SchemaDateTimeException.cpp
 *
 *  Created on: 2013/02/28
 *      Author: mugwort_rc
 */

#include "SchemaDateTimeException.h"

#include <boost/python.hpp>

//! for forward declaration
#include <xercesc/framework/MemoryManager.hpp>

#include <xercesc/util/SchemaDateTimeException.hpp>

#include "XMLException.h"

namespace pyxerces {

//! SchemaDateTimeException
MakePythonTranslateXMLException(SchemaDateTimeException)

void SchemaDateTimeException_init(void) {
	//! xercesc::SchemaDateTimeException
	MakePythonXMLException(SchemaDateTimeException)
}

} /* namespace pyxerces */
