# BPF code for SAI tracing
import subprocess, re
from string import Template
from saiutils import *

import logging
logger = logging.getLogger('saibpf module')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
log_format = '[%(asctime)-15s] [%(levelname)08s] %(module)s.%(funcName)s-%(lineno)d: %(message)s'
logging.basicConfig(format=log_format)


#==================== STATIC BPF CODE ==============================
sai_bpf_base_code = """
#include <uapi/linux/ptrace.h>

//=== common SAI types ===//
typedef int32_t sai_status_t;
typedef int32_t sai_object_type_t;
typedef uint64_t sai_object_id_t;

// used as keys to map
enum op_type_e {
  OP_CREATE = 0,
  OP_REMOVE = 1,
  OP_SET = 2,
  OP_GET = 3,
  OP_BULK_CREATE = 4,
  OP_BULK_REMOVE = 5,
  OP_GET_STATS = 6,
  OP_GET_STATS_EXT = 7,
  OP_CLEAR_STATS = 8
};

//=============== BPF Histogram data structures and helpers  ===========================//

// For secondary-indexed histogram examples, see:
// https://github.com/iovisor/bcc/blob/e83019bdf6c400b589e69c7d18092e38088f89a8/examples/tracing/nflatency.py

// map of function start times, keyed by object type/operation
// key formed by MAKE_KEY() below
// Obj types are small ints up to around 101 at this time
// See https://github.com/opencomputeproject/SAI/blob/10a9d5723287e0676bf81120d1a4ad5c882aefdc/inc/saitypes.h#L187

#define KEY_SHIFT 4
#define MAKE_KEY(_ot, _op) ((_ot<<KEY_SHIFT) + _op)
#define MAX_OT 127
#define MAX_LATENCY_KEYS ((MAX_OT+1) << KEY_SHIFT) // e.g. 1024 keys handle 128 obj tpes, 16 different "operations"

// Array of start times, keyed by obj type & operation
// Syntax: BPF_ARRAY(name [, leaf_type [, size]])
BPF_ARRAY(start_times_arrmap, uint64_t, MAX_LATENCY_KEYS); // handles obj types up to 127 before need to double

// Define a key used to access a 3D histogram series
// See https://github.com/iovisor/bcc/blob/e83019bdf6c400b589e69c7d18092e38088f89a8/examples/tracing/nflatency.py

typedef struct sai_func_key_s {
    sai_object_type_t ot;   // SAI object type
    enum op_type_e op;      // API operation: create, remove, set, get, get_stats, clear_stats
} sai_func_key_t;

typedef struct hist_key_s {
    sai_func_key_t sai_func;
    int slot;               // distribution slot, linear or log
} hist_key_t;


// Store func entry start time using SAI obj type and "operation" code" as hashmap keys
static void store_func_start_time(sai_object_type_t ot, int op) {
  int key = MAKE_KEY(ot,op);
  uint64_t now = bpf_ktime_get_ns();
  start_times_arrmap.update(&key,&now);
  bpf_trace_printk("store_func_start_time(): ot=%d, op=%d, start=%ld", ot, op, now);
}

// Retreive func entry start time using SAI obj type and "operation" code" as hashmap keys
// calc latency = now - start time, return it
static uint64_t get_func_lat(sai_object_type_t ot, int op) {
  int key = MAKE_KEY(ot,op);
  //uint64_t *start = start_times_hashmap.lookup(&key); 
  uint64_t *start = start_times_arrmap.lookup(&key); 
  uint64_t lat = 0;
  if (start != 0) {
    uint64_t now = bpf_ktime_get_ns();
    lat = now - *start;
    // bpf_trace_printk("get_func_lat(): ot=%d, op=%d, lat=%ld", ot, op, lat);
  } else {
    bpf_trace_printk("get_func_lat(): ot=%d, op=%d, DIDN'T FIND Stored start time!", ot, op);
  }
  return lat;
}

#define USEC_SCALE_FACTOR 1000 // nsec->usec

// func latency histogram, indexed by sai_object_type_t, op_type_e
// Syntax: BPF_HISTOGRAM(name [, key_type [, size ]])
BPF_HISTOGRAM(sai_func_latency_hist, hist_key_t, MAX_LATENCY_KEYS);

static void store_hist_lat_value(sai_object_type_t ot, int op, uint64_t latency) {

  unsigned int slot = bpf_log2l((unsigned int)latency/USEC_SCALE_FACTOR);

  hist_key_t key = {};
  key.sai_func.ot = ot;
  key.sai_func.op = op;
  key.slot = slot;
  sai_func_latency_hist.increment(key);
  bpf_trace_printk("store_hist_lat_value(): increment sai_func_latency_hist[ot=%d, op=%d, slot=%d]", ot, op, slot);
  return;
}


// Item (obj or attr) count histogram, indexed by sai_object_type_t, op_type_e
// Syntax: BPF_HISTOGRAM(name [, key_type [, size ]])
BPF_HISTOGRAM(sai_func_item_hist, hist_key_t, 64);

static void store_hist_item_count(sai_object_type_t ot, int op, uint32_t item_count) {

  hist_key_t key = {};
  key.sai_func.ot = ot;
  key.sai_func.op = op;
  key.slot = bpf_log2l(item_count);
  sai_func_item_hist.increment(key);
  bpf_trace_printk("store_hist_item_count(): increment sai_func_item_hist[ot=%d, op=%d, slot=%d]", ot, op, key.slot);
  return;
}

//=============== BPF Probe "callbacks" ===========================//

// BULK oid API tracing

void trace_sai_bulkCreate_fn(struct pt_regs *ctx) {
  /*     DTRACE_PROBE8(saivisor, sai_bulkCreate_fn, 
            object_type,
            switch_id,
            object_count,
            attr_count,
            attr_list,
            mode,
            object_id,
            object_statuses);
  */
  //    Arguments: 4@-116(%rbp) 8@%rdi 4@%esi 8@%rdx 8@%r14 4@16(%rbp) 8@%r15 8@%r12
        sai_object_type_t ot;
        sai_object_id_t switch_id;
        uint32_t object_count;
        const uint32_t *attr_count;
        void **attr_list;
        uint32_t mode; // sai_bulk_op_error_mode_t = enum
        void *object_id;
        sai_status_t *object_statuses;

  bpf_usdt_readarg(1, ctx, &ot);
  bpf_usdt_readarg(2, ctx, &switch_id);
  bpf_usdt_readarg(3, ctx, &object_count);
  bpf_usdt_readarg(4, ctx, &attr_count);
  bpf_usdt_readarg(5, ctx, &attr_list);
  bpf_usdt_readarg(6, ctx, &mode);
  bpf_usdt_readarg(7, ctx, &object_id);
  bpf_usdt_readarg(8, ctx, &object_statuses);

  bpf_trace_printk("trace_sai_bulkCreate_fn(): ot=%d, object_count=%d, attr_count=%d", ot, object_count, attr_count);
  store_func_start_time(ot, OP_BULK_CREATE);
  store_hist_item_count(ot, OP_BULK_CREATE, object_count);
}


void trace_sai_bulkCreate_ret(struct pt_regs *ctx) {
  //  DTRACE_PROBE3(saivisor, sai_bulkCreate_ret, object_type, status, object_statuses); // probe can examine modified statuses
  //    Arguments: 4@-116(%rbp) -4@%ebx 8@%r12
  sai_object_type_t ot; sai_status_t status; sai_status_t *object_statuses;

  bpf_usdt_readarg(1, ctx, &ot);
  bpf_usdt_readarg(2, ctx, &status);
  bpf_usdt_readarg(3, ctx, &object_statuses);

  bpf_trace_printk("trace_sai_bulkCreate_ret: ot=%d, status=%d",ot, status);
  uint64_t lat = get_func_lat(ot, OP_BULK_CREATE);
  store_hist_lat_value(ot, OP_BULK_CREATE, lat);
}

void trace_sai_bulkRemove_fn(struct pt_regs *ctx) {
  /*     DTRACE_PROBE4(saivisor, sai_bulkRemove_fn, 
            object_type,
            object_id,
            mode,
            object_statuses);
  */
  //    Arguments: 4@-116(%rbp) 8@%rdi 4@%esi 8@%rdx 8@%r14 4@16(%rbp) 8@%r15 8@%r12
        sai_object_type_t ot;
        void *object_id;
        uint32_t mode; // sai_bulk_op_error_mode_t = enum
        sai_status_t *object_statuses;

  bpf_usdt_readarg(1, ctx, &ot);
  bpf_usdt_readarg(2, ctx, &object_id);
  bpf_usdt_readarg(3, ctx, &mode);
  bpf_usdt_readarg(4, ctx, &object_statuses);

  bpf_trace_printk("trace_sai_bulkRemove_fn(): ot=%d, mode=%d)", ot, mode);
  store_func_start_time(ot, OP_BULK_REMOVE);
}

void trace_sai_bulkRemove_ret(struct pt_regs *ctx) {
  //  DTRACE_PROBE3(saivisor, sai_bulkRemove_ret, object_type, status, object_statuses); // probe can examine modified statuses
  //    Arguments: 4@%ebp -4@%eax 8@%r12
  sai_object_type_t ot; sai_status_t status; sai_status_t *object_statuses;

  bpf_usdt_readarg(1, ctx, &ot);
  bpf_usdt_readarg(2, ctx, &status);
  bpf_usdt_readarg(3, ctx, &object_statuses);

  bpf_trace_printk("trace_sai_bulkRemove_ret: ot=%d, status=%d",ot, status);
  uint64_t lat = get_func_lat(ot, OP_BULK_CREATE);
  store_hist_lat_value(ot, OP_BULK_CREATE, lat);
}

// stats API tracing
#if 0
void trace_sai_get_stats_fn(struct pt_regs *ctx) {
  // DTRACE_PROBE5(saivisor, sai_get_stats_fn, object_type, object_id, number_of_counters, counter_ids, counters);
  //    Arguments: 4@%ebx 8@%rdi 4@%r15d 8@%r12 8@%r13
  sai_object_type_t ot; sai_object_id_t oid; uint32_t number_of_counters; void *counter_ids; void *counters;

  bpf_usdt_readarg(1, ctx, &ot);
  bpf_usdt_readarg(2, ctx, &oid);
  bpf_usdt_readarg(3, ctx, &number_of_counters);
  bpf_usdt_readarg(4, ctx, &counter_ids);
  bpf_usdt_readarg(5, ctx, &counters);

  bpf_trace_printk("trace_sai_get_stats_fn(): ot=%d, oid=%d, number_of_counters=%d", ot, oid, number_of_counters);
  store_func_start_time(ot, OP_GET_STATS);
  store_hist_item_count(ot, OP_GET_STATS, number_of_counters);
}

void trace_sai_get_stats_ret(struct pt_regs *ctx) {
  // DTRACE_PROBE2(saivisor, sai_get_stats_ret, (int)object_type, status);
  //    Arguments: -4@%ebx -4@%eax
  sai_object_type_t ot; sai_status_t status;

  bpf_usdt_readarg(1, ctx, &ot);
  bpf_usdt_readarg(2, ctx, &status);

  bpf_trace_printk("trace_sai_get_stats_ret: ot=%d, status=%d",ot, status);
  uint64_t lat = get_func_lat(ot, OP_GET_STATS);
  store_hist_lat_value(ot, OP_GET_STATS, lat);
}


void trace_sai_get_stats_ext_fn(struct pt_regs *ctx) {
  // DTRACE_PROBE6(saivisor, sai_get_stats_ext_fn, object_type, object_id, number_of_counters, counter_ids, mode, counters);
  //    Arguments: 4@%ebx 8@%rdi 4@%esi 8@%r13 4@%r14d 8@%r15
  sai_object_type_t ot; sai_object_id_t oid; uint32_t number_of_counters; void *counter_ids; uint32_t mode; void *counters;

  bpf_usdt_readarg(1, ctx, &ot);
  bpf_usdt_readarg(2, ctx, &oid);
  bpf_usdt_readarg(3, ctx, &number_of_counters);
  bpf_usdt_readarg(4, ctx, &counter_ids);
  bpf_usdt_readarg(5, ctx, &mode);
  bpf_usdt_readarg(6, ctx, &counters);

  bpf_trace_printk("trace_sai_get_stats_ext_fn(): ot=%d, oid=%d, number_of_counters=%d]", ot, oid, number_of_counters);
  store_func_start_time(ot, OP_GET_STATS_EXT);
  store_hist_item_count(ot, OP_GET_STATS_EXT, number_of_counters);
}

void trace_sai_get_stats_ext_ret(struct pt_regs *ctx) {
// DTRACE_PROBE2(saivisor, sai_get_stats_ext_ret, object_type, status);
//    Arguments: 4@%ebx -4@%eax
 sai_object_type_t ot; sai_status_t status;

  bpf_usdt_readarg(1, ctx, &ot);
  bpf_usdt_readarg(2, ctx, &status);

  bpf_trace_printk("trace_sai_get_stats_ext_ret: ot=%d, status=%d",ot, status);
  uint64_t lat = get_func_lat(ot, OP_GET_STATS_EXT);
  store_hist_lat_value(ot, OP_GET_STATS_EXT, lat);
}


void trace_sai_clear_stats_fn(struct pt_regs *ctx) {
  // DTRACE_PROBE4(saivisor, sai_clear_stats_fn, object_type, object_id, number_of_counters, counter_ids);
  //   Arguments: 4@%ebx 8@%r13 4@%r14d 8@%r15
  sai_object_type_t ot; sai_object_id_t oid; uint32_t number_of_counters; void *counter_ids;

  bpf_usdt_readarg(1, ctx, &ot);
  bpf_usdt_readarg(2, ctx, &oid);
  bpf_usdt_readarg(3, ctx, &number_of_counters);
  bpf_usdt_readarg(4, ctx, &counter_ids);

  bpf_trace_printk("trace_sai_clear_stats_fn(): ot=%d, oid=%d, number_of_counters=%d]", ot, oid, number_of_counters);
  store_func_start_time(ot, OP_CLEAR_STATS);
  store_hist_item_count(ot, OP_CLEAR_STATS, number_of_counters);
}

void trace_sai_clear_stats_ret(struct pt_regs *ctx) {
  // DTRACE_PROBE2(saivisor, sai_clear_stats_ret, object_type, status);
  //    Arguments: -4@%ebx -4@%eax
  sai_object_type_t ot; sai_status_t status;

  bpf_usdt_readarg(1, ctx, &ot);
  bpf_usdt_readarg(2, ctx, &status);

  bpf_trace_printk("trace_sai_clear_stats_ret: ot=%d, status=%d",ot, status);
  uint64_t lat = get_func_lat(ot, OP_CLEAR_STATS);
  store_hist_lat_value(ot, OP_CLEAR_STATS, lat);
}
#endif
"""
#==================== END OF STATIC BPF CODE ==============================

#===================== BPF TEMPLATES =================================
# Dictionary of BPF callback "template programs" to perform SAI function tracing
# Actual probe names obtained by tplist-bpfcc are substituted into the templates
# Example: actual probe name: sai_nat_entry_create_fn
# Template substituion: ${_trace_function_} => trace_sai_nat_entry_create_fn 

sai_bpf_usdt_templates = {}

### create entry trace funcs ###
sai_bpf_usdt_templates['create_obj_entry_fn'] = Template("""
void ${_trace_function_}(struct pt_regs *ctx) {
  // Invocation: DTRACE_PROBE(_provider, _probe);
  //bpf_trace_printk("${_trace_function_}");
  store_func_start_time(${_ot_}, OP_CREATE);
  store_hist_item_count(${_ot_}, OP_CREATE, attr_count);
}
""")

# eBPF code template for a USDT probe with signature 'create_<objtype>_entry_ret>'
# No func params
sai_bpf_usdt_templates['create_obj_entry_ret'] = Template("""
void ${_trace_function_}(struct pt_regs *ctx) {
  // Invocation: DTRACE_PROBE(_provider, _probe);

  //bpf_trace_printk("${_trace_function_}");
  uint64_t lat = get_func_lat(${_ot_}, OP_CREATE);
  store_hist_lat_value(${_ot_}, OP_CREATE, lat);
}
""")

# eBPF code template for a USDT probe with signature 'create_<objtype>_entry_ret_val>'
# One func param: the SAI API's return value = 'status'
sai_bpf_usdt_templates['create_obj_entry_ret_val'] = Template("""
void ${_trace_function_}(struct pt_regs *ctx) {
  // DTRACE_PROBE1(_provider, _probe ## _val, _status)
  //    Arguments: -4@%eax
  sai_status_t status;

  bpf_usdt_readarg(1, ctx, &status);
  // TODO - process return val, e.g. track error codes
  //bpf_trace_printk("${_trace_function_}: status=%d", status);
  uint64_t lat = get_func_lat(${_ot_}, OP_CREATE);
  store_hist_lat_value(${_ot_}, OP_CREATE, lat);
}
""")

### Remove entry trace funcs ###
sai_bpf_usdt_templates['remove_obj_entry_fn'] = Template("""
void ${_trace_function_}(struct pt_regs *ctx) {
  // Invocation: DTRACE_PROBE(_provider, _probe);
  //bpf_trace_printk("${_trace_function_}");
  store_func_start_time(${_ot_}, OP_REMOVE);
  store_hist_item_count(${_ot_}, OP_REMOVE, attr_count);
}
""")

# eBPF code template for a USDT probe with signature 'remove_<objtype>_entry_ret>'
# No func params
sai_bpf_usdt_templates['remove_obj_entry_ret'] = Template("""
void ${_trace_function_}(struct pt_regs *ctx) {
  // Invocation: DTRACE_PROBE(_provider, _probe);

  //bpf_trace_printk("${_trace_function_}");
  uint64_t lat = get_func_lat(${_ot_}, OP_REMOVE);
  store_hist_lat_value(${_ot_}, OP_REMOVE, lat);
}
""")

# eBPF code template for a USDT probe with signature 'remove_<objtype>_entry_ret_val>'
# One func param: the SAI API's return value = 'status'
sai_bpf_usdt_templates['remove_obj_entry_ret_val'] = Template("""
void ${_trace_function_}(struct pt_regs *ctx) {
  // DTRACE_PROBE1(_provider, _probe ## _val, _status)
  //    Arguments: -4@%eax
  sai_status_t status;

  bpf_usdt_readarg(1, ctx, &status);
  // TODO - process return val, e.g. track error codes
  //bpf_trace_printk("${_trace_function_}: status=%d", status);
  uint64_t lat = get_func_lat(${_ot_}, OP_REMOVE);
  store_hist_lat_value(${_ot_}, OP_REMOVE, lat);
}
""")

### Set entry trace funcs ###
sai_bpf_usdt_templates['set_obj_entry_attribute_fn'] = Template("""
void ${_trace_function_}(struct pt_regs *ctx) {
  // Invocation: DTRACE_PROBE(_provider, _probe);
  //bpf_trace_printk("${_trace_function_}");
  store_func_start_time(${_ot_}, OP_SET);
  store_hist_item_count(${_ot_}, OP_SET, attr_count);
}
""")

# eBPF code template for a USDT probe with signature 'set_<objtype>_entry_ret>'
# No func params
sai_bpf_usdt_templates['set_obj_entry_attribute_ret'] = Template("""
void ${_trace_function_}(struct pt_regs *ctx) {
  // Invocation: DTRACE_PROBE(_provider, _probe);

  //bpf_trace_printk("${_trace_function_}");
  uint64_t lat = get_func_lat(${_ot_}, OP_SET);
  store_hist_lat_value(${_ot_}, OP_SET, lat);
}
""")

# eBPF code template for a USDT probe with signature 'set_<objtype>_entry_ret_val>'
# One func param: the SAI API's return value = 'status'
sai_bpf_usdt_templates['set_obj_entry_attribute_ret_val'] = Template("""
void ${_trace_function_}(struct pt_regs *ctx) {
  // DTRACE_PROBE1(_provider, _probe ## _val, _status)
  //    Arguments: -4@%eax
  sai_status_t status;

  bpf_usdt_readarg(1, ctx, &status);
  // TODO - process return val, e.g. track error codes
  //bpf_trace_printk("${_trace_function_}: status=%d", status);
  uint64_t lat = get_func_lat(${_ot_}, OP_SET);
  store_hist_lat_value(${_ot_}, OP_SET, lat);
}
""")

### Get entry trace funcs ###
sai_bpf_usdt_templates['get_obj_entry_attribute_fn'] = Template("""
void ${_trace_function_}(struct pt_regs *ctx) {
  // Invocation: DTRACE_PROBE(_provider, _probe);
  //bpf_trace_printk("${_trace_function_}");
  store_func_start_time(${_ot_}, OP_GET);
  store_hist_item_count(${_ot_}, OP_GET, attr_count);
}
""")

# eBPF code template for a USDT probe with signature 'get_<objtype>_entry_ret>'
# No func params
sai_bpf_usdt_templates['get_obj_entry_attribute_ret'] = Template("""
void ${_trace_function_}(struct pt_regs *ctx) {
  // Invocation: DTRACE_PROBE(_provider, _probe);

  //bpf_trace_printk("${_trace_function_}");
  uint64_t lat = get_func_lat(${_ot_}, OP_GET);
  store_hist_lat_value(${_ot_}, OP_GET, lat);
}
""")

# eBPF code template for a USDT probe with signature 'get_<objtype>_entry_ret_val>'
# One func param: the SAI API's return value = 'status'
sai_bpf_usdt_templates['get_obj_entry_attribute_ret_val'] = Template("""
void ${_trace_function_}(struct pt_regs *ctx) {
  // DTRACE_PROBE1(_provider, _probe ## _val, _status)
  //    Arguments: -4@%eax
  sai_status_t status;

  bpf_usdt_readarg(1, ctx, &status);
  // TODO - process return val, e.g. track error codes
  //bpf_trace_printk("${_trace_function_}: status=%d", status);
  uint64_t lat = get_func_lat(${_ot_}, OP_GET);
  store_hist_lat_value(${_ot_}, OP_GET, lat);
}
""")

#====================END OF BPF TEMPLATES ==============================

def generate_bpf_from_template(template_dict, template_name, subst_map):
    """ Generate BPF sourcecode from a template
        template_dict - catalog of templates
        template_name - which template in the catalog
        subst_map - key-value dict of subtitutions,
                    e.g. {'sai_objtype_entry_create_fn':'sai_objtype_entry_create_fn'}
        return: C eBPF source code, or None cannot recognize and render probe function
    """
    template = template_dict[template_name]
    logger.info("Found template %s" % template_name)
    # breakpoint()
    return template.substitute(subst_map)

def generate_usdt_bpf_for_probename(probename):
    """
    Generate USDT BPF code for a USDT probe, e.g. sai_neighbor_entry_create_fn => code output
    """
    logger.info("Rendering eBPF code for probe %s()" % (probename))

    # Parse the probe name and derive generic template & object type
    # Example: probename = 'create_acl_entry_fn'
    #   generic name  = create_obj_entry_ret
    #   obj_type_name = 'acl'
    #   obj_type_enum = SAI_OBJECT_TYPE_ACL_ENTRY = 8
    unsupported_probe_patterns = [
      # 'table_bitmap',
      # 'table_meta'
    ]
    for pattern in unsupported_probe_patterns:
      if pattern in probename:
        logger.info("*** WARNING: Probe '%s' unsupported, not installing" % probename)
        return None

    pattern='(create|remove|get|set)_(.*_entry)(_attribute)?_(.*)'
    #        (group 1              ) (group 2) (group 3  )   (group 4) 
    rex = re.search(pattern, probename)
    if not rex:
      logger.warning("*** Probe name pattern '%s' not recognized," % probename)
      return None
    print ("Groups=", rex.groups())
    # probe_terms = probename.split('_')
    # probe_terms[1] = 'obj'  # replace actual obj name with 'obj' placeholder
    # template_name = '_'.join(probe_terms) 
    template_name = rex.group(1) + '_obj_entry' + (rex.group(3) if rex.group(3) else '') + '_' + rex.group(4) 
    if template_name not in sai_bpf_usdt_templates:
      logger.info("*** WARNING: Probe name pattern '%s' has no matching template '%s', ensure instrumented process and BPF code templates are compatible" % (probename,template_name))
      return None

    # Convert obj name into an int to use as metrics table index; use SAI obj type constants
    obj_type_name = ('SAI_OBJECT_TYPE_%s' % (rex.group(2))).upper()
    obj_type_enum = eval('saiutils.%s' %obj_type_name)

    # Render the template code into a specific function for this probe
    logger.info("Rendering eBPF code for %s(); objtype = %s = %d" % (probename, obj_type_name, obj_type_enum))
    subst_map = {
      '_trace_function_':'trace_%s' % probename,
      '_ot_' : obj_type_enum
    }
    return generate_bpf_from_template(sai_bpf_usdt_templates, template_name, subst_map) 

    # Must match BPF c code:
OP_CREATE = 0
OP_REMOVE = 1
OP_SET = 2
OP_GET = 3
OP_BULK_CREATE = 4
OP_BULK_REMOVE = 5
OP_GET_STATS = 6
OP_GET_STATS_EXT = 7
OP_CLEAR_STATS = 8

# For labeling histograms:
opcodes_labels = {
    OP_CREATE:'create',
    OP_REMOVE:'remove',
    OP_SET:'set',
    OP_BULK_CREATE:'bulkCreate',
    OP_BULK_REMOVE:'bulkRemove',
    OP_GET_STATS:'get_stats',
    OP_GET_STATS_EXT:'get_stats_ext',
    OP_CLEAR_STATS:'clear_stats'
}

def opcode_to_label(opcode):
    return opcodes_labels[opcode]

tplist = None

def get_pidof_proc(proc_name):
    return int(subprocess.check_output(['pidof',proc_name]))

def get_saivisor_usdt_probes_for_pid(pid):
    global tplist
    if tplist is None:
        tplist=subprocess.check_output(['sudo', '/usr/sbin/tplist-bpfcc','-p', '%d' % pid], text=True).splitlines()
        # print('tplist output=', tplist)

    # typical entry in saiprobes: "b'/proc/2629/root/usr/bin/syncd' b'saivisor':b'sai_get_stats_ext_fn'"
    saiprobes = [p for p in tplist if p.find("saivisor") != -1]

    # split on the single quotes, [5] is the name of the probe e.g. "sai_get_stats_ext_fn"
    return [ n.split('\'')[5] for n in saiprobes]

def get_sai_quad_probes_from_list(probe_list):
    """
    Get probes containing "_entry" which we assume are the so-called "QUAD" probes in VendorSai.cpp
    """
    return [p for p in probe_list if p.find("_entry") != -1]

def get_stats_probes_from_list(probe_list):
    return [p for p in probe_list if p.find("_stats") != -1]