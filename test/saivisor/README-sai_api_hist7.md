# sai_api_hist7.py tracing program with Prometheus Metrics Exporter and gRPC API
This enables USDT probes around SAI route entry funcs. The probes measure latency between the func entry and exit probes, accumulate log2 histograms in multi-indexed (by SAI obj type and operation) BPF histogram maps and exposes them as Prometheus metrics. It also has a gRPC controller API to manage probes and fetch metrics. This allows finer control over which probes are active at any one time.

 It mainly probes the so-called QUAD accessors wihch are usd in `syncd.cpp` plus the get/clear stats functions. Empirically, `tplist-bpfcc` shows mainly `xxx_entry` SAI objects. I need to find out where to instrument other object types such as ports.

The changes compared to [../saivisor-202111-cc46936/sai_api_hist6.py](../saivisor-202111-cc46936/sai_api_hist7.py) is to add a gRPC server on port 50051.

# Diagram
![syncd-usdt-probes-prom-grpc.svg](syncd-usdt-probes-prom-grpc.svg)
## TODO - next steps
* Add SAI attr APIs
* Where are port APIs etc.?
* Fix grafana dashboard generation from running BPF (actual maps)
* Filter ops from -- options
* Pass dictionary of template params around, reduce function arg lists (extend dict as it descends).
* Refactor/add BPF helpers, simplify main code + servers (Prometheus, gRPC)
* PR to libbpf (modified //usr/lib/python3/dist-packages/bcc/__init__.py to optionally defer USDT probe attachment)
# gRPC server
See [saivisor_grpc](saivisor_grpc/README.md)