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
#ifdef SAI_PROBE_PER_API_NO_PARAMS
#define SAI_PROBE(_provider, _probe) DTRACE_PROBE(_provider, _probe)
#endif

#ifndef SAI_PROBE
#define SAI_PROBE(_provider, _probe)
#endif

#endif // #ifndef _PROBE_UTILS_H_
