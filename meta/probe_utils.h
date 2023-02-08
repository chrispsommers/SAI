/**
 * Copyright (c) 20XX Microsoft Open Technologies, Inc.
 *
 *    Licensed under the Apache License, Version 2.0 (the "License"); you may
 *    not use this file except in compliance with the License. You may obtain
 *    a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 *    THIS CODE IS PROVIDED ON AN *AS IS* BASIS, WITHOUT WARRANTIES OR
 *    CONDITIONS OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT
 *    LIMITATION ANY IMPLIED WARRANTIES OR CONDITIONS OF TITLE, FITNESS
 *    FOR A PARTICULAR PURPOSE, MERCHANTABILITY OR NON-INFRINGEMENT.
 *
 *    See the Apache Version 2.0 License for specific language governing
 *    permissions and limitations under the License.
 *
 *    Microsoft would like to thank the following companies for their review and
 *    assistance with these files: Intel Corporation, Mellanox Technologies Ltd,
 *    Dell Products, L.P., Facebook, Inc., Marvell International Ltd.
 *
 * @file    probe_utils.h
 *
 * @brief   This file defines macros used to instrument SAI-thrift server with DTRACE probe points.
 */
#ifndef _PROBE_UTILS_H_
#define _PROBE_UTILS_H_

#include <sys/sdt.h>

// Perform a DTRACE probe call on every SAI API with no function parameters. Can be used
// for basic BPF probing such as latency histograms.
#ifdef SAI_PROBE_OPT_PER_API_NO_PARAMS
#define SAI_PROBE_ENTER(_provider, _probe) DTRACE_PROBE(_provider, _probe)
#endif

// If no probe opts set, omit probes
#ifndef SAI_PROBE_ENTER
#define SAI_PROBE_ENTER(_provider, _probe)
#warning "No SAI_PROBE_ENTER defined"
#endif

// "Return" probes are called just after calling the sai functions.
// The API "status" return value is available and can optionally
// be sent to the DTRACE probe for processing

// Trace return of function w/o any extra DTRACE params
#ifdef SAI_PROBE_OPT_RET_NO_PARAM
#define SAI_PROBE_RET(_provider, _probe, _status) DTRACE_PROBE(_provider, _probe)
#endif

#ifdef SAI_PROBE_OPT_RET_STATUS_PARAM
#define SAI_PROBE_RET(_provider, _probe, _status) DTRACE_PROBE1(_provider, _probe ## _val, _status)
#endif

// If no probe opts set, omit ret probes
#ifndef SAI_PROBE_RET
#define SAI_PROBE_RET(_provider, _probe, _status)
#warning "No SAI_PROBE_RET defined"
#endif

#endif // #ifndef _PROBE_UTILS_H_
