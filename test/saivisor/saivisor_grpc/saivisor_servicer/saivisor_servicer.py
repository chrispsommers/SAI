import grpc

from pb2 import saivisor_pb2, saivisor_pb2_grpc
from bpfmetrics import saibpfmetrics

import logging
logger = logging.getLogger('Saivisor_servicer')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
log_format = '[%(asctime)-15s] [%(levelname)08s] %(module)s.%(funcName)s-%(lineno)d: %(message)s'
logging.basicConfig(format=log_format)

class Saivisor_servicer(saivisor_pb2_grpc.SaivisorServicer):

    def __init__(self, bpf=None, usdt_contexts=[]):
        self.bpf = bpf
        self.usdt_contexts = usdt_contexts
        self.probe_states = {}

    def GetProbes(self, request, context):
        """ Get list of BPF probe names and other details"""

        logger.info("Saivisor_servicer.GetProbes()" )
        context.set_code(grpc.StatusCode.OK)
        response_pb =  saivisor_pb2.GetProbesResponse()

        if self.usdt_contexts is not None:
            for usdt in self.usdt_contexts:
                logger.info("getting probes for %s..." % usdt)
                probes = usdt.enumerate_active_probes()
                for (binpath, fn_name, addr, pid) in probes:
                    name = binpath.decode()
                    fn_name = fn_name.decode()
                    key = (name, fn_name, pid)
                    if key in self.probe_states:
                        attached = self.probe_states[key]
                    else:
                        attached = False

                    probe_pb = saivisor_pb2.Probe(
                        binpath = name,
                        fn_name = fn_name,
                        addr = addr,
                        pid = pid,
                        type = saivisor_pb2.Probe.USDT,
                        attached = attached
                    )
                    response_pb.probes.append(probe_pb)
        else:
            probe_pb = saivisor_pb2.Probe(
                        binpath = "/fake-bin/path",
                        fn_name = "fake_function_name",
                        addr = 0xdeadbeef,
                        pid = 12345,
                        type = saivisor_pb2.Probe.USDT,
                    enabled = True if self.bpf is not None else False
                )
        return response_pb;

    def GetMetrics(self, request, context):
        """ Get list of Prometheus metrics data """

        logger.info("Saivisor_servicer.GetMetrics()" )
        context.set_code(grpc.StatusCode.OK)
        response_pb =  saivisor_pb2.GetMetricsResponse()
        
        if self.bpf is not None:
            metrics = saibpfmetrics.get_histogram_data_dicts(self.bpf)
            for metric in metrics:
                print("\n==========\n",metric)
                metric_pb = saivisor_pb2.Metric(
                    name = metric["Bucket"],
                    tstamp = metric["ts"],
                    type = metric["type"],
                    units = metric["units"]
                )
                for data in metric["data"]:
                    bucket_pb = saivisor_pb2.Histogram_bucket(
                        intval_start = data["intvl-start"],
                        intval_end = data["intvl-end"],
                        count = data["count"]
                    )
                    metric_pb.buckets.append(bucket_pb)
                response_pb.metrics.append(metric_pb)
        else:
            metric_pb = saivisor_pb2.Metric(
                    name = "FAKE_metric"
                )
            response_pb.metrics.append(metric_pb)
        return response_pb;

    def GetMetricsNames(self, request, context):
        """ Get list of Prometheus metrics names only """

        logger.info("Saivisor_servicer.GetMetricsNames()" )
        context.set_code(grpc.StatusCode.OK)
        response_pb =  saivisor_pb2.GetMetricsNamesResponse()
        
        if self.bpf is not None:
            names = saibpfmetrics.get_latency_histogram_names(self.bpf)
            for name in names:
                response_pb.names.append(name)
        else:
            response_pb.names.append("FAKE_metric1")
            response_pb.names.append("FAKE_metric2")
        return response_pb;

    def AttachProbes(self, request, context):
        """ Attach BPF probes """
        logger.info("Saivisor_servicer.AttachProbes()" )
        context.set_code(grpc.StatusCode.OK)
        response_pb =  saivisor_pb2.AttachProbesResponse()
        req_probes = request.probes # empty = all, else match
        if self.usdt_contexts is not None:
            if req_probes is not None and len(req_probes) > 0:
                req_keys = {}
                for req_probe in req_probes:
                    key = (req_probe.binpath, req_probe.fn_name, req_probe.pid)
                    req_keys[key] = True

            for usdt in self.usdt_contexts:
                probes = usdt.enumerate_active_probes()
                for (binpath, fn_name, addr, pid) in probes:
                    binpath = binpath.decode()
                    fn_name = fn_name.decode()
                    if req_keys is None or (binpath, fn_name, pid) in req_keys:
                        logger.info("  attaching probe %s %s" % (binpath, fn_name))
                        self.bpf.attach_uprobe(name=binpath, fn_name=fn_name,
                                        addr=addr, pid=pid)
                        key = (binpath, fn_name, pid)
                        self.probe_states[key] = True

        return response_pb


    def DetachProbes(self, request, context):
        """ Detach BPF probes """
        logger.info("Saivisor_servicer.DetachProbes()" )
        context.set_code(grpc.StatusCode.OK)
        response_pb =  saivisor_pb2.DetachProbesResponse()
        req_probes = request.probes # empty = all, else match

        if self.usdt_contexts is not None:
            if req_probes is not None and len(req_probes) > 0:
                req_keys = {}
                for req_probe in req_probes:
                    key = (req_probe.binpath, req_probe.fn_name, req_probe.pid)
                    req_keys[key] = True

            for usdt in self.usdt_contexts:
                probes = usdt.enumerate_active_probes()
                for (binpath, fn_name, addr, pid) in probes:
                    binpath = binpath.decode()
                    fn_name = fn_name.decode()
                    if req_keys is None or (binpath, fn_name, pid) in req_keys:
                        logger.info("  detaching probe %s %s" % (binpath, fn_name))
                        self.bpf.detach_uprobe(name=binpath, sym=fn_name,
                                        addr=addr, pid=pid)
                        key = (binpath, fn_name, pid)
                        self.probe_states[key] = False

        return response_pb
