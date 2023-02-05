# sai_api_hist5.py tracing program
This enables USDT probes around SAI route entry funcs. The probes measure latency between the func entry and exit probes, accumulate log2 histograms in multi-indexed (by SAI obj type and operation) BPF histogram maps  and prints them out. It mainly probes the so-called QUAD accessors wihch are usd in `syncd.cpp` plus the get/clear stats functions. Empirically, `tplist-bpfcc` shows mainly `xxx_entry` SAI objects. I need to find out where to instrument other object types such as ports.

The changes compared to [../saivisor-202111-cc46936/sai_api_hist4.py](../saivisor-202111-cc46936/sai_api_hist4.py) in the previous build of `syncd` is to add bulk quad tracing, API item count histograms (`attr_count`, `object_count` values per API).
# Diagram
![syncd-usdt-probes.svg](syncd-usdt-probes.svg)
## TODO - next steps
* Add SAI attr APIs
* Where are port APIs etc.?


# Example
Summary:
* Start program - it waits for CTRL-C to stop and print
* Run `route_cmds.sh` to add/delete 255 routes on SONiC box
* Stop program, view histograms
## Start tracing program
```
root@sonic:/home/chris# ./sai_api_hist5.py
Skipping probes for port
Skipping probes for lag
Skipping probes for virtual_router
Skipping probes for next_hop
Skipping probes for next_hop_group
Skipping probes for router_interface
Skipping probes for acl_table
Skipping probes for acl_counter
Skipping probes for acl_range
Skipping probes for acl_table_group
Skipping probes for acl_table_group_member
Skipping probes for hostif
Skipping probes for mirror_session
Skipping probes for sample_packet
Skipping probes for stp
Skipping probes for hostif_trap_group
Skipping probes for policer
Skipping probes for wred
Skipping probes for qos_map
Skipping probes for queue
Skipping probes for scheduler
Skipping probes for scheduler_group
Skipping probes for buffer_pool
Skipping probes for buffer_profile
Skipping probes for ingress_priority_group
Skipping probes for lag_member
Skipping probes for hash
Skipping probes for udf
Skipping probes for udf_match
Skipping probes for udf_group
==> Enabling QUAD (create,remove,set,get) func & ret USDT probes for SAI object:fdb_entry (8 total)
Skipping probes for switch
Skipping probes for hostif_trap
==> Enabling QUAD (create,remove,set,get) func & ret USDT probes for SAI object:neighbor_entry (8 total)
==> Enabling QUAD (create,remove,set,get) func & ret USDT probes for SAI object:route_entry (8 total)
Skipping probes for vlan
Skipping probes for vlan_member
Skipping probes for hostif_packet
Skipping probes for tunnel_map
Skipping probes for tunnel
Skipping probes for fdb_flush
Skipping probes for next_hop_group_member
Skipping probes for stp_port
Skipping probes for rpf_group
Skipping probes for rpf_group_member
Skipping probes for l2mc_group
Skipping probes for l2mc_group_member
Skipping probes for ipmc_group
Skipping probes for ipmc_group_member
==> Enabling QUAD (create,remove,set,get) func & ret USDT probes for SAI object:l2mc_entry (8 total)
==> Enabling QUAD (create,remove,set,get) func & ret USDT probes for SAI object:ipmc_entry (8 total)
==> Enabling QUAD (create,remove,set,get) func & ret USDT probes for SAI object:mcast_fdb_entry (8 total)
Skipping probes for hostif_user_defined_trap
Skipping probes for bridge
Skipping probes for bridge_port
Skipping probes for tam
Skipping probes for srv6_sidlist
Skipping probes for port_pool
==> Enabling QUAD (create,remove,set,get) func & ret USDT probes for SAI object:inseg_entry (8 total)
Skipping probes for dtel
Skipping probes for dtel_queue_report
Skipping probes for dtel_int_session
Skipping probes for dtel_report_session
Skipping probes for dtel_event
Skipping probes for bfd_session
Skipping probes for isolation_group
Skipping probes for isolation_group_member
Skipping probes for tam_math_func
Skipping probes for tam_report
Skipping probes for tam_event_threshold
Skipping probes for tam_tel_type
Skipping probes for tam_transport
Skipping probes for tam_telemetry
Skipping probes for tam_collector
Skipping probes for tam_event_action
Skipping probes for tam_event
Skipping probes for nat_zone_counter
==> Enabling QUAD (create,remove,set,get) func & ret USDT probes for SAI object:nat_entry (8 total)
Skipping probes for tam_int
Skipping probes for counter
Skipping probes for debug_counter
Skipping probes for port_connector
Skipping probes for port_serdes
Skipping probes for macsec
Skipping probes for macsec_port
Skipping probes for macsec_flow
Skipping probes for macsec_sc
Skipping probes for macsec_sa
Skipping probes for system_port
Skipping probes for fine_grained_hash_field
Skipping probes for switch_tunnel
==> Enabling QUAD (create,remove,set,get) func & ret USDT probes for SAI object:my_sid_entry (8 total)
Skipping probes for my_mac
Skipping probes for next_hop_group_map
Skipping probes for ipsec
Skipping probes for ipsec_port
Skipping probes for ipsec_sa
==> Enabling func & ret USDT probes for sai_get_stats() (2 probes total)
==> Enabling func & ret USDT probes for sai_get_stats_ext() (2 probes total)
==> Enabling func & ret USDT probes for sai_clear_stats() (2 probes total)
...

Tracing SAI functions... Hit Ctrl-C to end.
...                                       |
```
## Add/Delete routes
```
root@sonic:/home/chris# ./route_cmds.sh 
ip r add 31.1.8.1/32 dev Ethernet8
ip r add 31.1.8.2/32 dev Ethernet8
ip r add 31.1.8.3/32 dev Ethernet8
...
ip r del 31.1.1.253/32 dev Ethernet8
ip r del 31.1.1.254/32 dev Ethernet8
ip r del 31.1.1.255/32 dev Ethernet8
```

## Stop and view results
```
^C
SAI Function Latency Distributions
==================================

Bucket = latency (usec) queue_get_stats 
     value               : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 255      |***********                             |
        16 -> 31         : 863      |****************************************|
        32 -> 63         : 755      |**********************************      |
        64 -> 127        : 41       |*                                       |
       128 -> 255        : 1        |                                        |
       256 -> 511        : 0        |                                        |
       512 -> 1023       : 0        |                                        |
      1024 -> 2047       : 2        |                                        |
      2048 -> 4095       : 1        |                                        |
      4096 -> 8191       : 1        |                                        |
      8192 -> 16383      : 0        |                                        |
     16384 -> 32767      : 0        |                                        |
     32768 -> 65535      : 0        |                                        |
     65536 -> 131071     : 1        |                                        |

Bucket = latency (usec) router_interface_get_stats 
     value               : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 0        |                                        |
        64 -> 127        : 0        |                                        |
       128 -> 255        : 0        |                                        |
       256 -> 511        : 601      |****************************************|
       512 -> 1023       : 98       |******                                  |
      1024 -> 2047       : 1        |                                        |
      2048 -> 4095       : 0        |                                        |
      4096 -> 8191       : 1        |                                        |
      8192 -> 16383      : 1        |                                        |
     16384 -> 32767      : 0        |                                        |
     32768 -> 65535      : 0        |                                        |
     65536 -> 131071     : 2        |                                        |

Bucket = latency (usec) route_entry_remove 
     value               : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 0        |                                        |
        64 -> 127        : 177      |****************************************|
       128 -> 255        : 75       |****************                        |
       256 -> 511        : 3        |                                        |

Bucket = latency (usec) route_entry_create 
     value               : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 0        |                                        |
        64 -> 127        : 196      |****************************************|
       128 -> 255        : 44       |********                                |
       256 -> 511        : 1        |                                        |
       512 -> 1023       : 14       |**                                      |

Bucket = latency (usec) ingress_priority_group_get_stats 
     value               : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 0        |                                        |
        64 -> 127        : 490      |****************************************|
       128 -> 255        : 9        |                                        |
       256 -> 511        : 13       |*                                       |

Bucket = latency (usec) port_get_stats 
     value               : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 0        |                                        |
        64 -> 127        : 0        |                                        |
       128 -> 255        : 0        |                                        |
       256 -> 511        : 0        |                                        |
       512 -> 1023       : 696      |****************************************|
      1024 -> 2047       : 1        |                                        |
      2048 -> 4095       : 7        |                                        |

SAI Function item count Distributions
=====================================

Bucket = # Item Count queue_get_stats 
     value               : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 1920     |****************************************|

Bucket = # Item Count route_entry_create 
     value               : count     distribution
         0 -> 1          : 255      |****************************************|

Bucket = # Item Count port_get_stats 
     value               : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 0        |                                        |
        64 -> 127        : 704      |****************************************|

Bucket = # Item Count router_interface_get_stats 
     value               : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 704      |****************************************|

Bucket = # Item Count ingress_priority_group_get_stats 
     value               : count     distribution
         0 -> 1          : 512      |****************************************|
```
