/**
 * @file    probe_utils.h
 *
 * @brief   This file defines macros used to instrument SAI-thrift server with DTRACE probe points.
 */
#include <sys/sdt.h>

// Perform a DTRACE probe call with no function parameters
#define SAI_PROBE(_provider, _probe) DTRACE_PROBE(_provider, _probe)