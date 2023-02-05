from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, StateSetMetricFamily, HistogramMetricFamily
import sys, os, traceback, json
from datetime import datetime
from time import strftime
# from bcc import BPF, USDT
from bcc import table

import saiutils.saiutils as saiutils
import saibpf.saibpf as saibpf
import ctypes as ct

import logging
logger = logging.getLogger('SaiBpfMetrics')
logger.setLevel(logging.INFO)

# For test/debug basic operation - register in main
class DummyMetricsCollector(object):
    def collect(self):
        logger.debug("DummyMetricsCollector()")
        yield GaugeMetricFamily('my_gauge', 'Help text', value=7)
        c = CounterMetricFamily('my_counter_total', 'Help text', labels=['foo'])
        c.add_metric(['bar'], 1.7)
        c.add_metric(['baz'], 3.8)
        yield c
        m_status = StateSetMetricFamily('port_link_status', 'Link state of an interface (port)', labels=['mylabel'])
        m_status.add_metric(labels=['some_label'],value={'UP':True}, timestamp=datetime.now().timestamp())
        yield m_status

# Render string labels for the nested histograms. Lambda func sends (ot,op) set for "bucket"
def prometheus_latency_bucket_desc(bucket):
    ot = bucket[0]
    op = bucket[1]
    return "%s_%s_latency" % (saiutils.get_probename_for_sai_objtype(ot), saibpf.opcode_to_label(op))

# Render string labels for the nested histograms. Lambda func sends (ot,op) set for "bucket"
def prometheus_item_count_bucket_desc(bucket):
    ot = bucket[0]
    op = bucket[1]
    return "%s_%s_item_count" % (saiutils.get_probename_for_sai_objtype(ot), saibpf.opcode_to_label(op))

#### Adapted from iovisor bcc/src/python/bcc/table.py _print_json_hist()
def _emit_log2_hist_metrics(vals, val_type, section_bucket=None):
    """ return tuple(prom_hist=list of prometheus metrics, dict_hist=metrics dictionary)"""
    name=section_bucket[1] if section_bucket else '?'
    print ("\n%s" % name)
    print ("========================================")
    prom_hist = HistogramMetricFamily(name=section_bucket[1] if section_bucket else '?',
        documentation=section_bucket[1] if section_bucket else '?',
        unit=val_type)
    hist_list = []
    max_nonzero_idx = 0
    for i in range(len(vals)):
        if vals[i] != 0:
            max_nonzero_idx = i
    index = 1 # power of two histogram bin
    prev = 0
    buckets = []
    # sum of all the observed values; not accurate because of log2 scaling
    # TODO? track true linear sum in the BPF probe code and export as another map value
    sum=0
    #  
    # Cumulative bin counts, bins represent # occurrences less than or equal to the threshold
    count=0 # num of total samples
    for i in range(len(vals)):
        if i != 0 and i <= max_nonzero_idx:
            index = index * 2
            val = int(vals[i])
            count += val
            # print ("Count=%d" % count)
            sum += index*val
            list_obj = {}
            list_obj['intvl-start'] = prev
            list_obj['intvl-end'] = int(index) - 1
            list_obj['count'] = val
            hist_list.append(list_obj)
            prev = index

            # Histogram bins are labled in Prometheus by the "le" or "less-than-or-equal-to" upper limit of the bin
            # So, the upper limit is index^2, and the le value is index^2-1 because the range is not inclusive of the upper limit
            buckets.append(('%d' % (int(index) - 1),count))
            #print ("le=%d count=%d" % (int(index) - 1,count) )

        if i == len(vals)-1 :
            # last interval must end in +Inf and contains total # observations (sum of the values)
            buckets.append(('+Inf',count))
    tstamp =  datetime.now().timestamp()
    prom_hist.add_metric(labels=[],buckets=buckets, sum_value=sum, timestamp=tstamp)
    dict_hist = {"datetime": strftime("%Y-%m-%d %H:%M:%S"), "ts":tstamp, "type": "histogram", "units": val_type, "data": hist_list}
    if section_bucket:
        dict_hist[section_bucket[0]] = name
        # print("\n==========\n",dict_hist)
    return (prom_hist,dict_hist)

#### Adapted from iovisor bcc/src/python/bcc/table.py print_json_hist()
def emit_log2_hist_metrics(hist, val_type="value", section_header="Bucket ptr",
                section_print_fn=None, bucket_fn=None, bucket_sort_fn=None):

    hlist = []
    if isinstance(hist.Key(), ct.Structure):
        tmp = {}
        buckets = []
        hist.decode_c_struct(tmp, buckets, bucket_fn, bucket_sort_fn)
        for bucket in buckets:
            vals = tmp[bucket]
            if section_print_fn:
                section_bucket = (section_header, section_print_fn(bucket))
            else:
                section_bucket = (section_header, bucket)
            hlist.append(_emit_log2_hist_metrics(vals, val_type, section_bucket))
        return hlist
    else:
        vals = [0] * log2_index_max
        for k, v in hist.items():
            vals[k.value] = v.value
        return [_emit_log2_hist_metrics(vals, val_type)]

# assumes section hdr func and histogram keys are ct.Structure's
def get_metric_names_from_bpf_histograms(hist, val_type, section_print_fn=None, bucket_fn=None, bucket_sort_fn=None):
    names = []
    if section_print_fn is None:
        raise Exception("Must have Section Print Function")

    if isinstance(hist.Key(), ct.Structure):
        tmp = {}
        buckets = []
        hist.decode_c_struct(tmp, buckets, bucket_fn, bucket_sort_fn)
        for bucket in buckets:
            names.append(section_print_fn(bucket)+ "_" + val_type + "_buckets")
        return names
    else:
        raise Exception("histogram %s isn't a ct.Structure, bucket name is ambiguous")

def get_latency_histogram_names(bpf):
    return get_metric_names_from_bpf_histograms(
        bpf['sai_func_latency_hist'],
        val_type = "usec",
        bucket_fn=lambda k: (k.ot, k.op), # turn struct into set
        section_print_fn=prometheus_latency_bucket_desc
    )

def get_histogram_data_dicts(bpf):
    """ return list of histogram metrics in dict form """
    metrics = [ m[1] for m in emit_log2_hist_metrics(bpf['sai_func_latency_hist'],
        section_header="Bucket",
        val_type = "usec",
        bucket_fn=lambda k: (k.ot, k.op), # turn struct into set
        section_print_fn=prometheus_latency_bucket_desc)]

    metrics.extend([ m[1] for m in emit_log2_hist_metrics(bpf['sai_func_item_hist'],
        section_header="Bucket",
        val_type = "items",
        bucket_fn=lambda k: (k.ot, k.op), # turn struct into set
        section_print_fn=prometheus_latency_bucket_desc)])
    return metrics

class BpfMetricsCollector(object):

    def __init__(self, bpf):
        self.bpf = bpf

    def collect(self):

        logger.debug("BpfMetricsCollector()")

        print ("\nSAI Function Latency Distributions")
        print (  "==================================")
        self.bpf['sai_func_latency_hist'].print_log2_hist(
            section_header="Bucket",
            val_type = "usec",
            bucket_fn=lambda k: (k.ot, k.op), # turn struct into set
            section_print_fn=prometheus_latency_bucket_desc)

        print ("\nSAI Function item count Distributions")
        print (  "=====================================")

        self.bpf['sai_func_item_hist'].print_log2_hist(
            section_header="Bucket",
            val_type = "items",
            bucket_fn=lambda k: (k.ot, k.op), # turn struct into set
            section_print_fn=prometheus_item_count_bucket_desc)

        for h in emit_log2_hist_metrics(self.bpf['sai_func_latency_hist'],
            section_header="Bucket",
            val_type = "usec",
            bucket_fn=lambda k: (k.ot, k.op), # turn struct into set
            section_print_fn=prometheus_latency_bucket_desc):
            yield h[0]

        for h in emit_log2_hist_metrics(self.bpf['sai_func_item_hist'],
            section_header="Bucket",
            val_type = "items",
            bucket_fn=lambda k: (k.ot, k.op), # turn struct into set
            section_print_fn=prometheus_item_count_bucket_desc):
            yield h[0]
