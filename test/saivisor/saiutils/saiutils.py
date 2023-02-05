# See https://github.com/opencomputeproject/SAI/blob/10a9d5723287e0676bf81120d1a4ad5c882aefdc/inc/saitypes.h#L187
# TODO - find way to autogenerate this or get from saithrift python client module sai_headers.py
SAI_OBJECT_TYPE_PORT                     =  1
SAI_OBJECT_TYPE_LAG                      =  2
SAI_OBJECT_TYPE_VIRTUAL_ROUTER           =  3
SAI_OBJECT_TYPE_NEXT_HOP                 =  4
SAI_OBJECT_TYPE_NEXT_HOP_GROUP           =  5
SAI_OBJECT_TYPE_ROUTER_INTERFACE         =  6
SAI_OBJECT_TYPE_ACL_TABLE                =  7
SAI_OBJECT_TYPE_ACL_ENTRY                =  8
SAI_OBJECT_TYPE_ACL_COUNTER              =  9
SAI_OBJECT_TYPE_ACL_RANGE                = 10
SAI_OBJECT_TYPE_ACL_TABLE_GROUP          = 11
SAI_OBJECT_TYPE_ACL_TABLE_GROUP_MEMBER   = 12
SAI_OBJECT_TYPE_HOSTIF                   = 13
SAI_OBJECT_TYPE_MIRROR_SESSION           = 14
SAI_OBJECT_TYPE_SAMPLEPACKET             = 15
SAI_OBJECT_TYPE_STP                      = 16
SAI_OBJECT_TYPE_HOSTIF_TRAP_GROUP        = 17
SAI_OBJECT_TYPE_POLICER                  = 18
SAI_OBJECT_TYPE_WRED                     = 19
SAI_OBJECT_TYPE_QOS_MAP                  = 20
SAI_OBJECT_TYPE_QUEUE                    = 21
SAI_OBJECT_TYPE_SCHEDULER                = 22
SAI_OBJECT_TYPE_SCHEDULER_GROUP          = 23
SAI_OBJECT_TYPE_BUFFER_POOL              = 24
SAI_OBJECT_TYPE_BUFFER_PROFILE           = 25
SAI_OBJECT_TYPE_INGRESS_PRIORITY_GROUP   = 26
SAI_OBJECT_TYPE_LAG_MEMBER               = 27
SAI_OBJECT_TYPE_HASH                     = 28
SAI_OBJECT_TYPE_UDF                      = 29
SAI_OBJECT_TYPE_UDF_MATCH                = 30
SAI_OBJECT_TYPE_UDF_GROUP                = 31
SAI_OBJECT_TYPE_FDB_ENTRY                = 32
SAI_OBJECT_TYPE_SWITCH                   = 33
SAI_OBJECT_TYPE_HOSTIF_TRAP              = 34
SAI_OBJECT_TYPE_HOSTIF_TABLE_ENTRY       = 35
SAI_OBJECT_TYPE_NEIGHBOR_ENTRY           = 36
SAI_OBJECT_TYPE_ROUTE_ENTRY              = 37
SAI_OBJECT_TYPE_VLAN                     = 38
SAI_OBJECT_TYPE_VLAN_MEMBER              = 39
SAI_OBJECT_TYPE_HOSTIF_PACKET            = 40
SAI_OBJECT_TYPE_TUNNEL_MAP               = 41
SAI_OBJECT_TYPE_TUNNEL                   = 42
SAI_OBJECT_TYPE_TUNNEL_TERM_TABLE_ENTRY  = 43
SAI_OBJECT_TYPE_FDB_FLUSH                = 44
SAI_OBJECT_TYPE_NEXT_HOP_GROUP_MEMBER    = 45
SAI_OBJECT_TYPE_STP_PORT                 = 46
SAI_OBJECT_TYPE_RPF_GROUP                = 47
SAI_OBJECT_TYPE_RPF_GROUP_MEMBER         = 48
SAI_OBJECT_TYPE_L2MC_GROUP               = 49
SAI_OBJECT_TYPE_L2MC_GROUP_MEMBER        = 50
SAI_OBJECT_TYPE_IPMC_GROUP               = 51
SAI_OBJECT_TYPE_IPMC_GROUP_MEMBER        = 52
SAI_OBJECT_TYPE_L2MC_ENTRY               = 53
SAI_OBJECT_TYPE_IPMC_ENTRY               = 54
SAI_OBJECT_TYPE_MCAST_FDB_ENTRY          = 55
SAI_OBJECT_TYPE_HOSTIF_USER_DEFINED_TRAP = 56
SAI_OBJECT_TYPE_BRIDGE                   = 57
SAI_OBJECT_TYPE_BRIDGE_PORT              = 58
SAI_OBJECT_TYPE_TUNNEL_MAP_ENTRY         = 59
SAI_OBJECT_TYPE_TAM                      = 60
SAI_OBJECT_TYPE_SRV6_SIDLIST             = 61
SAI_OBJECT_TYPE_PORT_POOL                = 62
SAI_OBJECT_TYPE_INSEG_ENTRY              = 63
SAI_OBJECT_TYPE_DTEL                     = 64
SAI_OBJECT_TYPE_DTEL_QUEUE_REPORT        = 65
SAI_OBJECT_TYPE_DTEL_INT_SESSION         = 66
SAI_OBJECT_TYPE_DTEL_REPORT_SESSION      = 67
SAI_OBJECT_TYPE_DTEL_EVENT               = 68
SAI_OBJECT_TYPE_BFD_SESSION              = 69
SAI_OBJECT_TYPE_ISOLATION_GROUP          = 70
SAI_OBJECT_TYPE_ISOLATION_GROUP_MEMBER   = 71
SAI_OBJECT_TYPE_TAM_MATH_FUNC            = 72
SAI_OBJECT_TYPE_TAM_REPORT               = 73
SAI_OBJECT_TYPE_TAM_EVENT_THRESHOLD      = 74
SAI_OBJECT_TYPE_TAM_TEL_TYPE             = 75
SAI_OBJECT_TYPE_TAM_TRANSPORT            = 76
SAI_OBJECT_TYPE_TAM_TELEMETRY            = 77
SAI_OBJECT_TYPE_TAM_COLLECTOR            = 78
SAI_OBJECT_TYPE_TAM_EVENT_ACTION         = 79
SAI_OBJECT_TYPE_TAM_EVENT                = 80
SAI_OBJECT_TYPE_NAT_ZONE_COUNTER         = 81
SAI_OBJECT_TYPE_NAT_ENTRY                = 82
SAI_OBJECT_TYPE_TAM_INT                  = 83
SAI_OBJECT_TYPE_COUNTER                  = 84
SAI_OBJECT_TYPE_DEBUG_COUNTER            = 85
SAI_OBJECT_TYPE_PORT_CONNECTOR           = 86
SAI_OBJECT_TYPE_PORT_SERDES              = 87
SAI_OBJECT_TYPE_MACSEC                   = 88
SAI_OBJECT_TYPE_MACSEC_PORT              = 89
SAI_OBJECT_TYPE_MACSEC_FLOW              = 90
SAI_OBJECT_TYPE_MACSEC_SC                = 91
SAI_OBJECT_TYPE_MACSEC_SA                = 92
SAI_OBJECT_TYPE_SYSTEM_PORT              = 93
SAI_OBJECT_TYPE_FINE_GRAINED_HASH_FIELD  = 94
SAI_OBJECT_TYPE_SWITCH_TUNNEL            = 95
SAI_OBJECT_TYPE_MY_SID_ENTRY             = 96
SAI_OBJECT_TYPE_MY_MAC                   = 97
SAI_OBJECT_TYPE_NEXT_HOP_GROUP_MAP       = 98
SAI_OBJECT_TYPE_IPSEC                    = 99
SAI_OBJECT_TYPE_IPSEC_PORT               = 100
SAI_OBJECT_TYPE_IPSEC_SA                 = 101
SAI_OBJECT_TYPE_TABLE_BITMAP_CLASSIFICATION_ENTRY = 102
SAI_OBJECT_TYPE_TABLE_BITMAP_ROUTER_ENTRY = 103
SAI_OBJECT_TYPE_TABLE_META_TUNNEL_ENTRY = 104
SAI_OBJECT_TYPE_DASH_ACL_GROUP = 105
SAI_OBJECT_TYPE_DASH_ACL_RULE = 106
SAI_OBJECT_TYPE_DIRECTION_LOOKUP_ENTRY = 107
SAI_OBJECT_TYPE_ENI_ETHER_ADDRESS_MAP_ENTRY = 108
SAI_OBJECT_TYPE_ENI = 109
SAI_OBJECT_TYPE_INBOUND_ROUTING_ENTRY = 110
SAI_OBJECT_TYPE_OUTBOUND_CA_TO_PA_ENTRY = 111
SAI_OBJECT_TYPE_OUTBOUND_ROUTING_ENTRY = 112
SAI_OBJECT_TYPE_VNET = 113
SAI_OBJECT_TYPE_PA_VALIDATION_ENTRY = 114
SAI_OBJECT_TYPE_VIP_ENTRY = 115

# For every entry, we'll generate BPF callback code and enable USDT probe
# USDT probes must already appear in the executable's ELF notes SDT section
# Use readelf -n <prog> or tplist-bpcff <prog>) to view SDT symbols
#
# TODO - finish dict of string names
probes = {
    SAI_OBJECT_TYPE_PORT                     :'port',
    SAI_OBJECT_TYPE_LAG                      :'lag',
    SAI_OBJECT_TYPE_VIRTUAL_ROUTER           :'virtual_router',
    SAI_OBJECT_TYPE_NEXT_HOP                 :'next_hop',
    SAI_OBJECT_TYPE_NEXT_HOP_GROUP           :'next_hop_group',
    SAI_OBJECT_TYPE_ROUTER_INTERFACE         :'router_interface',
    SAI_OBJECT_TYPE_ACL_TABLE                :'acl_table',
    SAI_OBJECT_TYPE_ACL_ENTRY                :'acl_entry',
    SAI_OBJECT_TYPE_ACL_COUNTER              :'acl_counter',
    SAI_OBJECT_TYPE_ACL_RANGE                :'acl_range',
    SAI_OBJECT_TYPE_ACL_TABLE_GROUP          :'acl_table_group',
    SAI_OBJECT_TYPE_ACL_TABLE_GROUP_MEMBER   :'acl_table_group_member',
    SAI_OBJECT_TYPE_HOSTIF                   :'hostif',
    SAI_OBJECT_TYPE_MIRROR_SESSION           :'mirror_session',
    SAI_OBJECT_TYPE_SAMPLEPACKET             :'sample_packet',
    SAI_OBJECT_TYPE_STP                      :'stp',
    SAI_OBJECT_TYPE_HOSTIF_TRAP_GROUP        :'hostif_trap_group',
    SAI_OBJECT_TYPE_POLICER                  :'policer',
    SAI_OBJECT_TYPE_WRED                     :'wred',
    SAI_OBJECT_TYPE_QOS_MAP                  :'qos_map',
    SAI_OBJECT_TYPE_QUEUE                    :'queue',
    SAI_OBJECT_TYPE_SCHEDULER                :'scheduler',
    SAI_OBJECT_TYPE_SCHEDULER_GROUP          :'scheduler_group',
    SAI_OBJECT_TYPE_BUFFER_POOL              :'buffer_pool',
    SAI_OBJECT_TYPE_BUFFER_PROFILE           :'buffer_profile',
    SAI_OBJECT_TYPE_INGRESS_PRIORITY_GROUP   :'ingress_priority_group',
    SAI_OBJECT_TYPE_LAG_MEMBER               :'lag_member',
    SAI_OBJECT_TYPE_HASH                     :'hash',
    SAI_OBJECT_TYPE_UDF                      :'udf',
    SAI_OBJECT_TYPE_UDF_MATCH                :'udf_match',
    SAI_OBJECT_TYPE_UDF_GROUP                :'udf_group',
    SAI_OBJECT_TYPE_FDB_ENTRY                :'fdb_entry',
    SAI_OBJECT_TYPE_SWITCH                   :'switch',
    SAI_OBJECT_TYPE_HOSTIF_TRAP              :'hostif_trap',
    SAI_OBJECT_TYPE_HOSTIF_TABLE_ENTRY       :'hostif_table_entry',
    SAI_OBJECT_TYPE_NEIGHBOR_ENTRY           :'neighbor_entry',
    SAI_OBJECT_TYPE_ROUTE_ENTRY              :'route_entry',
    SAI_OBJECT_TYPE_VLAN                     :'vlan',
    SAI_OBJECT_TYPE_VLAN_MEMBER              :'vlan_member',
    SAI_OBJECT_TYPE_HOSTIF_PACKET            :'hostif_packet',
    SAI_OBJECT_TYPE_TUNNEL_MAP               :'tunnel_map',
    SAI_OBJECT_TYPE_TUNNEL                   :'tunnel',
    SAI_OBJECT_TYPE_TUNNEL_TERM_TABLE_ENTRY  :'tunnel_term_table_entry',
    SAI_OBJECT_TYPE_FDB_FLUSH                :'fdb_flush',
    SAI_OBJECT_TYPE_NEXT_HOP_GROUP_MEMBER    :'next_hop_group_member',
    SAI_OBJECT_TYPE_STP_PORT                 :'stp_port',
    SAI_OBJECT_TYPE_RPF_GROUP                :'rpf_group',
    SAI_OBJECT_TYPE_RPF_GROUP_MEMBER         :'rpf_group_member',
    SAI_OBJECT_TYPE_L2MC_GROUP               :'l2mc_group',
    SAI_OBJECT_TYPE_L2MC_GROUP_MEMBER        :'l2mc_group_member',
    SAI_OBJECT_TYPE_IPMC_GROUP               :'ipmc_group',
    SAI_OBJECT_TYPE_IPMC_GROUP_MEMBER        :'ipmc_group_member',
    SAI_OBJECT_TYPE_L2MC_ENTRY               :'l2mc_entry',
    SAI_OBJECT_TYPE_IPMC_ENTRY               :'ipmc_entry',
    SAI_OBJECT_TYPE_MCAST_FDB_ENTRY          :'mcast_fdb_entry',
    SAI_OBJECT_TYPE_HOSTIF_USER_DEFINED_TRAP :'hostif_user_defined_trap',
    SAI_OBJECT_TYPE_BRIDGE                   :'bridge',
    SAI_OBJECT_TYPE_BRIDGE_PORT              :'bridge_port',
    SAI_OBJECT_TYPE_TUNNEL_MAP_ENTRY         :'tunnel_map_entry',
    SAI_OBJECT_TYPE_TAM                      :'tam',
    SAI_OBJECT_TYPE_SRV6_SIDLIST             :'srv6_sidlist',
    SAI_OBJECT_TYPE_PORT_POOL                :'port_pool',
    SAI_OBJECT_TYPE_INSEG_ENTRY              :'inseg_entry',
    SAI_OBJECT_TYPE_DTEL                     :'dtel',
    SAI_OBJECT_TYPE_DTEL_QUEUE_REPORT        :'dtel_queue_report',
    SAI_OBJECT_TYPE_DTEL_INT_SESSION         :'dtel_int_session',
    SAI_OBJECT_TYPE_DTEL_REPORT_SESSION      :'dtel_report_session',
    SAI_OBJECT_TYPE_DTEL_EVENT               :'dtel_event',
    SAI_OBJECT_TYPE_BFD_SESSION              :'bfd_session',
    SAI_OBJECT_TYPE_ISOLATION_GROUP          :'isolation_group',
    SAI_OBJECT_TYPE_ISOLATION_GROUP_MEMBER   :'isolation_group_member',
    SAI_OBJECT_TYPE_TAM_MATH_FUNC            :'tam_math_func',
    SAI_OBJECT_TYPE_TAM_REPORT               :'tam_report',
    SAI_OBJECT_TYPE_TAM_EVENT_THRESHOLD      :'tam_event_threshold',
    SAI_OBJECT_TYPE_TAM_TEL_TYPE             :'tam_tel_type',
    SAI_OBJECT_TYPE_TAM_TRANSPORT            :'tam_transport',
    SAI_OBJECT_TYPE_TAM_TELEMETRY            :'tam_telemetry',
    SAI_OBJECT_TYPE_TAM_COLLECTOR            :'tam_collector',
    SAI_OBJECT_TYPE_TAM_EVENT_ACTION         :'tam_event_action',
    SAI_OBJECT_TYPE_TAM_EVENT                :'tam_event',
    SAI_OBJECT_TYPE_NAT_ZONE_COUNTER         :'nat_zone_counter',
    SAI_OBJECT_TYPE_NAT_ENTRY                :'nat_entry',
    SAI_OBJECT_TYPE_TAM_INT                  :'tam_int',
    SAI_OBJECT_TYPE_COUNTER                  :'counter',
    SAI_OBJECT_TYPE_DEBUG_COUNTER            :'debug_counter',
    SAI_OBJECT_TYPE_PORT_CONNECTOR           :'port_connector',
    SAI_OBJECT_TYPE_PORT_SERDES              :'port_serdes',
    SAI_OBJECT_TYPE_MACSEC                   :'macsec',
    SAI_OBJECT_TYPE_MACSEC_PORT              :'macsec_port',
    SAI_OBJECT_TYPE_MACSEC_FLOW              :'macsec_flow',
    SAI_OBJECT_TYPE_MACSEC_SC                :'macsec_sc',
    SAI_OBJECT_TYPE_MACSEC_SA                :'macsec_sa',
    SAI_OBJECT_TYPE_SYSTEM_PORT              :'system_port',
    SAI_OBJECT_TYPE_FINE_GRAINED_HASH_FIELD  :'fine_grained_hash_field',
    SAI_OBJECT_TYPE_SWITCH_TUNNEL            :'switch_tunnel',
    SAI_OBJECT_TYPE_MY_SID_ENTRY             :'my_sid_entry',
    SAI_OBJECT_TYPE_MY_MAC                   :'my_mac',
    SAI_OBJECT_TYPE_NEXT_HOP_GROUP_MAP       :'next_hop_group_map',
    SAI_OBJECT_TYPE_IPSEC                    :'ipsec',
    SAI_OBJECT_TYPE_IPSEC_PORT               :'ipsec_port',
    SAI_OBJECT_TYPE_IPSEC_SA                 :'ipsec_sa',
}

def get_probes():
    return probes

def get_probename_for_sai_objtype(objtype):
    return probes[objtype]