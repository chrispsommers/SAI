#!/usr/bin/python3
from bcc import BPF, USDT
import os
from time import sleep
import sys
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+"/saivisor_grpc/")
sys.path.append(dir_path+"/saivisor_grpc/pb2")
# print ("sys.path: ",sys.path)

import saiutils.saiutils as saiutils
import saibpf.saibpf as saibpf
import argparse, textwrap

from prometheus_client import start_http_server, Summary
from prometheus_client.core import REGISTRY

from bpfmetrics import saibpfmetrics
from grafana.grafana import emit_dashboard_config

from saivisor_grpc.server import SaiVisorGrpcServer

import logging
logger = logging.getLogger('SAI Probe Metrics Server')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
log_format = '[%(asctime)-15s] [%(levelname)08s] %(module)s.%(funcName)s-%(lineno)d: %(message)s'
logging.basicConfig(format=log_format)


parser = argparse.ArgumentParser(description='Accumulate and print SAI function trace metrics',
            formatter_class=argparse.RawTextHelpFormatter,
            epilog = textwrap.dedent('''
Examples:
=========
Install BPF probes and continuously expose live Prometheus metrics:
./saivisor.py --output prometheus [--prom_port 8000]

Install BPF probes and accumulate histograms, output as ASCII-art after terminating via ^C:
./saivisor.py --output ascii

Install BPF probes and accumulate histograms, output as JSON data after terminating via ^C:
./saivisor.py --output json

Gafana dashboard JSON generation. The following cmd-line operations control which metrics to generate panels for, and their effect is cumulative, i.e. you can specify metrics from multiple sources and their names will be added to a list from which to genreate panels:
--quad_probes, --quad_ops, --stats_probes, --stats_ops, --metrics, --metrics_file

Generate Grafana dashboard JSON for specified SAI objects and operations, plus stats objects and operations:
./saivisor.py --format grafana --quad_probes "route_entry" --quad_ops "create,remove" --stats_probes "port,router_interface" --stats_ops "get_stats" --datasource_uid vf50YxP7z --title "Route & Port" --dash_uid 2

Generate Grafana dashboard JSON for metrics passed in as --metrics argument:
./saivisor.py --output grafana --metrics "route_entry_create_latency_usec_bucket,route_entry_remove_latency_usec_bucket" --datasource_uid vf50YxP7z --title "Route & Port3" --dash_uid 3

Generate Grafana dashboard JSON for metrics read from file "tmp":
./saivisor.py --output grafana --metrics_file tmp --datasource_uid vf50YxP7z --title "Route & Port5" --dash_uid 5

Generate Grafana dashboard JSON for metrics read from stdin:
echo 'route_entry_create_latency_usec_bucket,route_entry_remove_latency_usec_bucket' | ./saivisor.py --output grafana --metrics_file - --datasource_uid vf50YxP7z --title "Route & Port5" --dash_uid 5
            '''))

parser.add_argument('--output',  choices=['none', 'ascii', 'json', 'prometheus', 'grafana'], default='none',
        help='Metrics output format. ascii, json send probe info to console; prometheus exposes /metrics HTTP server; grafana emits dashboard .json only')
parser.add_argument('--title',  default="SAI Visor", help='Dashboard Title, e.g. SAI Visor"')
parser.add_argument('--dash_uid',  default="0", help='Dashboard UID, e.g. "2"; needed when you import into Grafana to keep unique')
parser.add_argument('--metrics',  help='comma-separated list of metrics to add to Grafana dashboard when using "--output grafana" option, e.g. "route_entry_create_latency_usec_bucket,route_entry_remove_latency_usec_bucket"; if omitted, probes are read from ELF file')
parser.add_argument('--metrics_file', type=argparse.FileType('r'), help='comma-separated and/or line-separated list of metrics to add to Grafana dashboard when using "--output grafana" option, use "-" for stdin')
parser.add_argument('--quad_probes',  help='comma-separated list of SAI quad entry objects to add to Grafana dashboard when using "--output grafana" option, e.g. "route_entry,neighbor"; if omitted, probes are read from ELF file')
parser.add_argument('--quad_ops',  default='create,remove,get,set', help='comma-separated list of SAI quad entry operations to add to Grafana dashboard when using "--output grafana" option, e.g. "create,remove"; if omitted, all operations are included')
parser.add_argument('--stats_probes',  help='comma-separated list of SAI stats objects to add to Grafana dashboard when using "--output grafana" option, e.g. "port,router_interface"; if omitted, probes are read from ELF file')
parser.add_argument('--stats_ops',  default='get_stats,clear_stats', help='comma-separated list of SAI stats operations to add to Grafana dashboard when using "--output grafana" option, e.g. "get,clear"; if omitted, all operations are included')
parser.add_argument('--datasource_uid',  default='0',help='Grafana datasource UID, e.g. "1." Hint: get the UID from the Grafana browser URL when viewing a dashboard, e.g. IP:3000/d/<uid>/....')
parser.add_argument('--colorScheme',  default='interpolateSpectral',help='Grafana heatmap colorscheme, e.g. "interpolateSpectral"')
parser.add_argument('--prom_port', default=8000, type=int, help='Server port for prometheus metrics [8000]')
parser.add_argument('--grpc_port', default=50051, type=int, help='Server port for gRPC [50051]')
parser.add_argument('--bpf_autoinstall', choices=['n','y'], default='y', help='Install BPF code at startup [y]')
parser.add_argument('--bpf_autoattach', choices=['n','y'], default='y', help='Attach BPF probes at startup (requires autoinstall=y) [y]')
parser.add_argument('--grpc', choices=['n','y'], default='y', help='Launch gRPC server at startup [y]')
args = parser.parse_args()

# Render string labels for the nested histograms. Lambda func sends (ot,op) set for "bucket"
def latency_bucket_desc(bucket):
    ot = bucket[0]
    op = bucket[1]
    return "latency %s_%s " % (saiutils.get_probename_for_sai_objtype(ot), saibpf.opcode_to_label(op))

# Render string labels for the nested histograms. Lambda func sends (ot,op) set for "bucket"
def item_count_bucket_desc(bucket):
    ot = bucket[0]
    op = bucket[1]
    return "# Item Count %s_%s " % (saiutils.get_probename_for_sai_objtype(ot), saibpf.opcode_to_label(op))

target_pid=None
target_name='saiserver'
probe_names=None
target_path=''
bpf = None

def get_probes_from_elf_file_once():
    global target_pid, target_path, target_name, probe_names
    if target_pid is None:
        target_pid = saibpf.get_pidof_proc(target_name)
        target_path = '/proc/%d/root/SAI/rpc/usr/sbin/%s' % (target_pid, target_name)
        logger.info("Tracing %s pid=%d" % (target_path,target_pid))

    if probe_names is None:
        probe_names = saibpf.get_saivisor_usdt_probes_for_pid(target_pid)
        logger.info('Found the following %d USDT probes for SAI in "%s":' %(len(probe_names),target_name))
        logger.info("=================================================")
        logger.info(probe_names)

# Get quad entry probes from cmdline

quad_entry_probes = []
quad_entry_ops = []
stats_probes = []
stats_ops = []
usdt_contexts = []


# If we're just generating grafana template, emit JSON and exit
if args.output == 'grafana':
    metrics = []

    if args.quad_probes:
        quad_entry_probes = args.quad_probes.split(',')
    if args.quad_ops:
        quad_entry_ops = args.quad_ops.split(',')

    if args.stats_probes:
        stats_probes = args.stats_probes.split(',')
    if args.stats_probes:
        stats_ops = args.stats_ops.split(',')
    for objtype in quad_entry_probes:
        for op in quad_entry_ops:
            metrics.append('%s_%s_latency_usec_bucket' % (objtype,op))
    for objtype in stats_probes:
        for op in stats_ops:
            metrics.append('%s_%s_latency_usec_bucket' % (objtype,op))

    if args.metrics:
        metrics.extend(args.metrics.split(','))

    if args.metrics_file:
        while line := args.metrics_file.readline():
            # print (line)
            m = line.rstrip().split(',')
            metrics.extend(m)
        # print (metrics)

    if len(metrics) == 0:
        print ("No metrics specified - check cmd-line args!")
        exit()
    print(emit_dashboard_config(
        title=args.title,
        dash_uid=args.dash_uid,
        datasource_uid=args.datasource_uid,
        colorScheme=args.colorScheme,
        metrics=metrics
        ))
    exit()

# Compose BPF code

if args.bpf_autoinstall == 'n':
    logger.info("Skipping BPF probe installation per cmd-line option")
else:
    get_probes_from_elf_file_once()
    quad_entry_probes = saibpf.get_sai_quad_probes_from_list(probe_names)
    stats_probes = saibpf.get_stats_probes_from_list(probe_names)

    bpf_source = saibpf.sai_bpf_base_code

    usdt = USDT(path = target_path)
    usdt_contexts = [usdt]
    # Generate BPF code from templates and enable probes for QUAD accessors:
    for probe in quad_entry_probes:
        trace_bpf= saibpf.generate_usdt_bpf_for_probename(probe)
        logger.info("==> Generating code for %s..." % probe)
        # logger.info(trace_bpf)
        if trace_bpf is not None:
            bpf_source += "\n" + trace_bpf
            logger.info("==> Enabling USDT probe %s..." % probe)
            usdt.enable_probe(probe = probe, fn_name = "trace_%s" % (probe))

    # View the BPF 'c' code
    # logger.info(bpf_source)

    # Enable probes in USDT "context" - not actually installed yet, need BPF object created ahead
    for func in args.stats_ops.split(','):
        for suffix in ['fn', 'ret', 'ret_val']:                # arbitrary function name suffixes for entry, exit probes
            probe = "sai_%s_%s" % (func,suffix)
            if probe in stats_probes:
                logger.info("==> Enabling USDT probes for %s()..." % (probe))
                usdt.enable_probe(probe = "%s" % (probe), fn_name = "trace_%s" % (probe))
            else:
                logger.info("%s probe not available; not installing" % probe)
    logger.info("Installing BPF probes...")
    bpf = BPF(text = bpf_source, usdt_contexts = usdt_contexts, defer_usdt_probes=True)
    if args.bpf_autoattach == 'y':
        logger.info("Attaching BPF probes...")
        usdt.attach_uprobes(bpf,None)
    else:
        logger.info("BPF code is installed, NOT Attaching BPF probes...")


###### start gRPC server #####

if args.grpc == 'y':
    grpc_server_addr='0.0.0.0:%d' % args.grpc_port
    grpc_server_addr='0.0.0.0:%d' % args.grpc_port
    grpc_server=SaiVisorGrpcServer(addr=grpc_server_addr, bpf=bpf, usdt_contexts = usdt_contexts)
    grpc_server.start()
else:
    logger.info("Skipping gRPC server per cmd-line option")

try:
    # First test for output formats which don't continuously stream to console
    if args.output == 'prometheus':
        REGISTRY.register(saibpfmetrics.BpfMetricsCollector(bpf))    # Start up the server to expose the metrics.
        logger.info("Starting Prometheus server on port :%d/metrics" % args.prom_port)
        start_http_server(args.prom_port)

    logger.info("Hit Ctrl-C to end...")

    # Wait forever
    sleep(99999999)

except KeyboardInterrupt:

    if args.output == 'json':

        bpf['sai_func_latency_hist'].print_json_hist(
            section_header="Bucket",
            val_type = "usec",
            bucket_fn=lambda k: (k.ot, k.op), # turn struct into set
            section_print_fn=latency_bucket_desc)

        bpf['sai_func_item_hist'].print_json_hist(
            section_header="Bucket",
            val_type = "items",
            bucket_fn=lambda k: (k.ot, k.op), # turn struct into set
            section_print_fn=item_count_bucket_desc)

    elif args.output == 'ascii':

        logger.info("\nSAI Function Latency Distributions")
        logger.info(  "==================================")
        bpf['sai_func_latency_hist'].print_log2_hist(
            #   strip_leading_zero=True,
            section_header="Bucket",
            val_type = "usec",
            bucket_fn=lambda k: (k.ot, k.op), # turn struct into set
            section_print_fn=latency_bucket_desc)

        logger.info("\nSAI Function item count Distributions")
        logger.info(  "=====================================")

        bpf['sai_func_item_hist'].print_log2_hist(
            #   strip_leading_zero=True,
            section_header="Bucket",
            val_type = "items",
            bucket_fn=lambda k: (k.ot, k.op), # turn struct into set
            section_print_fn=item_count_bucket_desc)

    elif args.output == 'prometheus':
        # We hit ^C while serving metrics
        logger.info("...Shutting down Prometheus server")
    
    elif args.output == 'none':
        logger.info("Exiting, bye-bye!")

    
    else:
        logger.info("ERROR - unknown format: %s", args.output)

    if grpc_server:
        logger.info("...Shutting down gRPC server")
        grpc_server.stop()
