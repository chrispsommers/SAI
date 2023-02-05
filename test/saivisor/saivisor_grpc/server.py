#!/usr/bin/python3
import sys,os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+"/pb2")

from concurrent import futures
import grpc,time
from grpc_reflection.v1alpha import reflection

from pb2 import saivisor_pb2, saivisor_pb2_grpc
from  saivisor_servicer import saivisor_servicer

import logging
logger = logging.getLogger('SaiVisorGrpcServer')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
log_format = '[%(asctime)-15s] [%(levelname)08s] %(module)s.%(funcName)s-%(lineno)d: %(message)s'
logging.basicConfig(format=log_format)

class SaiVisorGrpcServer:
    def __init__(self, addr=None, bpf=None, usdt_contexts=[]) -> None:
        self.addr = addr
        self.bpf = bpf
        self.usdt_contexts = usdt_contexts
                
    def start(self, addr=None, bpf=None):
        if addr:
            self.addr = addr
        if bpf:
            self.bpf = bpf

        logger.debug("SaiVisorGrpcServer.start()")

        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        saivisor_pb2_grpc.add_SaivisorServicer_to_server(
            saivisor_servicer.Saivisor_servicer(self.bpf, self.usdt_contexts), self.server)

        SERVICE_NAMES = (
        reflection.SERVICE_NAME,
        saivisor_pb2.DESCRIPTOR.services_by_name['Saivisor'].full_name
        )
        reflection.enable_server_reflection(SERVICE_NAMES, self.server)
        self.server.add_insecure_port(self.addr)
        logger.info("Starting gRPC server at %s" % self.addr)
        self.server.start()

    def stop(self):
        logger.debug("SaiVisorGrpcServer.stop()")
        logger.info("Stopping gRPC server at %s" % self.addr)
        self.server.stop(0)

if __name__ == '__main__':
    addr='127.0.0.1:50051'
    server = SaiVisorGrpcServer(addr=addr)
    server.start()
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        server.stop()