# saivisor gRPC server

# Examples
Start probe daemon on target:
```
./sai_api_hist7.py --bpf_autoattach n
...
[2022-04-23 00:31:20,593] [    INFO] sai_api_hist7.<module>-202: BPF code is installed, NOT Attaching BPF probes...
SaiVisorGrpcServer.start()
[2022-04-23 00:31:20,594] [   DEBUG] server.start-32: SaiVisorGrpcServer.start()
Starting gRPC server at 0.0.0.0:50051
[2022-04-23 00:31:20,598] [    INFO] server.start-44: Starting gRPC server at 0.0.0.0:50051
Hit Ctrl-C to end...
[2022-04-23 00:31:20,600] [    INFO] sai_api_hist7.<module>-222: Hit Ctrl-C to end...
```
Get probes (none should be attached yet):
```
root@chris-z4:/# grpc_cli call sonic1:50051 GetProbes ""
...
probes {
  binpath: "/proc/2608/root/usr/bin/syncd"
  fn_name: "trace_sai_clear_stats_fn"
  addr: 537296
  pid: -1
  type: USDT
}
probes {
  binpath: "/proc/2608/root/usr/bin/syncd"
  fn_name: "trace_sai_clear_stats_ret"
  addr: 537310
  pid: -1
  type: USDT
}
```

Attach some probes using `grpc_cli`:
```
root@chris-z4:/# grpc_cli call sonic1:50051 AttachProbes 'probes [{binpath: "/proc/2608/root/usr/bin/syncd",fn_name: "trace_sai_clear_stats_fn",pid: -1}, {binpath: "/proc/2608/root/usr/bin/syncd",fn_name: "trace_sai_clear_stats_ret",pid: -1}]'
connecting to sonic1:50051
```

Get probes, note two are now attached:
```
probes {
  binpath: "/proc/2608/root/usr/bin/syncd"
  fn_name: "trace_sai_clear_stats_fn"
  addr: 537296
  pid: -1
  type: USDT
  attached: true
}
probes {
  binpath: "/proc/2608/root/usr/bin/syncd"
  fn_name: "trace_sai_clear_stats_ret"
  addr: 537310
  pid: -1
  type: USDT
  attached: true
}
```
Detach probes:
```
root@chris-z4:/# grpc_cli call sonic1:50051 DetachProbes 'probes [{binpath: "/proc/2608/root/usr/bin/syncd",fn_name: "trace_sai_clear_stats_fn",pid: -1}, {binpath: "/proc/2608/root/usr/bin/syncd",fn_name: "trace_sai_clear_stats_ret",pid: -1}]'
connecting to sonic1:50051
```
Get probes (probes which were attached are now detached again):
```
root@chris-z4:/# grpc_cli call sonic1:50051 GetProbes ""
...
probes {
  binpath: "/proc/2608/root/usr/bin/syncd"
  fn_name: "trace_sai_clear_stats_fn"
  addr: 537296
  pid: -1
  type: USDT
}
probes {
  binpath: "/proc/2608/root/usr/bin/syncd"
  fn_name: "trace_sai_clear_stats_ret"
  addr: 537310
  pid: -1
  type: USDT
}
```

Console output on target while probes are attached, detached:
```
[2022-04-23 00:27:03,108] [    INFO] saivisor_servicer.AttachProbes-110: Saivisor_servicer.AttachProbes()
  attaching probe /proc/2608/root/usr/bin/syncd trace_sai_clear_stats_fn
[2022-04-23 00:27:03,109] [    INFO] saivisor_servicer.AttachProbes-127:   attaching probe /proc/2608/root/usr/bin/syncd trace_sai_clear_stats_fn
  attaching probe /proc/2608/root/usr/bin/syncd trace_sai_clear_stats_ret
[2022-04-23 00:27:03,123] [    INFO] saivisor_servicer.AttachProbes-127:   attaching probe /proc/2608/root/usr/bin/syncd trace_sai_clear_stats_ret
Saivisor_servicer.DetachProbes()
[2022-04-23 00:29:09,487] [    INFO] saivisor_servicer.DetachProbes-138: Saivisor_servicer.DetachProbes()
  detaching probe /proc/2608/root/usr/bin/syncd trace_sai_clear_stats_fn
[2022-04-23 00:29:09,487] [    INFO] saivisor_servicer.DetachProbes-156:   detaching probe /proc/2608/root/usr/bin/syncd trace_sai_clear_stats_fn
  detaching probe /proc/2608/root/usr/bin/syncd trace_sai_clear_stats_ret
[2022-04-23 00:29:09,535] [    INFO] saivisor_servicer.DetachProbes-156:   detaching probe /proc/2608/root/usr/bin/syncd trace_sai_clear_stats_ret
```