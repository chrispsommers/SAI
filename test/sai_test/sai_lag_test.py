# Copyright (c) 2021 Microsoft Open Technologies, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
#    THIS CODE IS PROVIDED ON AN *AS IS* BASIS, WITHOUT WARRANTIES OR
#    CONDITIONS OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT
#    LIMITATION ANY IMPLIED WARRANTIES OR CONDITIONS OF TITLE, FITNESS
#    FOR A PARTICULAR PURPOSE, MERCHANTABILITY OR NON-INFRINGEMENT.
#
#    See the Apache Version 2.0 License for specific language governing
#    permissions and limitations under the License.
#
#    Microsoft would like to thank the following companies for their review and
#    assistance with these files: Intel Corporation, Mellanox Technologies Ltd,
#    Dell Products, L.P., Facebook, Inc., Marvell International Ltd.
#
#
from unittest import skip
from sai_test_base import T0TestBase
from sai_utils import *


class LagConfigTest(T0TestBase):
    """
    Verify the load-balance of l3
    """

    def setUp(self):
        """
        Test the basic setup process.
        """
        T0TestBase.setUp(self)

    def load_balance_on_src_ip(self):
        self.port1_rif = sai_thrift_create_router_interface(self.client,
                                                            virtual_router_id=self.dut.default_vrf,
                                                            type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                                                            port_id=self.dut.port_list[1])
        ip_dst = self.servers[11][1].ipv4
        pkt1 = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                 eth_src=self.servers[1][1].mac,
                                 ip_dst=ip_dst,
                                 ip_src=self.servers[1][1].ipv4,
                                 ip_id=105,
                                 ip_ttl=64)
        pkt2 = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                 eth_src=self.servers[2][1].mac,
                                 ip_dst=ip_dst,
                                 ip_src=self.servers[2][1].ipv4,
                                 ip_id=105,
                                 ip_ttl=64)
        exp_pkt1 = simple_tcp_packet(eth_dst=self.t1_list[1][100].mac,
                                     eth_src=ROUTER_MAC,
                                     ip_dst=ip_dst,
                                     ip_src=self.servers[1][1].ipv4,
                                     ip_id=105,
                                     ip_ttl=63)
        exp_pkt2 = simple_tcp_packet(eth_dst=self.t1_list[1][100].mac,
                                     eth_src=ROUTER_MAC,
                                     ip_dst=ip_dst,
                                     ip_src=self.servers[2][1].ipv4,
                                     ip_id=105,
                                     ip_ttl=63)
        send_packet(self, 1, pkt1)
        verify_packet_any_port(
            self, exp_pkt1, self.dut.lag1.member_port_indexs)
        send_packet(self, 1, pkt2)
        verify_packet_any_port(
            self, exp_pkt2, self.dut.lag1.member_port_indexs)

    def runTest(self):
        try:
            self.load_balance_on_src_ip()
        finally:
            pass

    def tearDown(self):
        sai_thrift_remove_router_interface(self.client, self.port1_rif)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        super().tearDown()


class LoadbalanceOnSrcPortTest(T0TestBase):
    """
    Test load balance of l3 by source port.
    """

    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self)

    def runTest(self):
        """
        1. Generate different packets by updating src port
        2. send these packets on port1
        3. Check if packets are received on ports of lag1 equally
        """
        try:
            print("Lag l3 load balancing test based on src port")
            self.port1_rif = sai_thrift_create_router_interface(self.client,
                                                                virtual_router_id=self.dut.default_vrf,
                                                                type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                                                                port_id=self.dut.port_list[1])
            max_itrs = 99
            begin_port = 2000
            rcv_count = [0, 0]
            for i in range(0, max_itrs):
                src_port = begin_port + i
                pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                        eth_src=self.servers[1][1].mac,
                                        ip_dst=self.servers[11][1].ipv4,
                                        ip_src=self.servers[1][1].ipv4,
                                        tcp_sport=src_port,
                                        ip_id=105,
                                        ip_ttl=64)
                exp_pkt = simple_tcp_packet(eth_dst=self.t1_list[1][100].mac,
                                            eth_src=ROUTER_MAC,
                                            ip_dst=self.servers[11][1].ipv4,
                                            ip_src=self.servers[1][1].ipv4,
                                            tcp_sport=src_port,
                                            ip_id=105,
                                            ip_ttl=63)
                send_packet(self, 1, pkt)
                rcv_idx, _ = verify_packet_any_port(
                    self, exp_pkt, self.dut.lag1.member_port_indexs)
                print('src_port={}, rcv_port={}'.format(src_port, rcv_idx))
                rcv_count[rcv_idx] += 1
            print(rcv_count)
            for i in range(0, 2):
                self.assertTrue((rcv_count[i] >= ((max_itrs/2) * 0.8)),
                                "Not all paths are equally balanced")
        finally:
            pass

    def tearDown(self):
        sai_thrift_remove_router_interface(self.client, self.port1_rif)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        super().tearDown()


class LoadbalanceOnDesPortTest(T0TestBase):
    """
    Test load balance of l3 by destinstion port.
    """

    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self)

    def runTest(self):
        """
        1. Generate different packets by updating des port
        2. send these packets on port1
        3. Check if packets are received on ports of lag1 equally
        """
        try:
            print("Lag l3 load balancing test based on des port")
            self.port1_rif = sai_thrift_create_router_interface(self.client,
                                                                virtual_router_id=self.dut.default_vrf,
                                                                type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                                                                port_id=self.dut.port_list[1])
            max_itrs = 99
            begin_port = 2000
            rcv_count = [0, 0]
            for i in range(0, max_itrs):
                des_port = begin_port + i
                pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                        eth_src=self.servers[1][1].mac,
                                        ip_dst=self.servers[11][1].ipv4,
                                        ip_src=self.servers[1][1].ipv4,
                                        tcp_dport=des_port,
                                        ip_id=105,
                                        ip_ttl=64)
                exp_pkt = simple_tcp_packet(eth_dst=self.t1_list[1][100].mac,
                                            eth_src=ROUTER_MAC,
                                            ip_dst=self.servers[11][1].ipv4,
                                            ip_src=self.servers[1][1].ipv4,
                                            tcp_dport=des_port,
                                            ip_id=105,
                                            ip_ttl=63)
                send_packet(self, 1, pkt)
                rcv_idx, _ = verify_packet_any_port(
                    self, exp_pkt, self.dut.lag1.member_port_indexs)
                print('des_port={}, rcv_port={}'.format(des_port, rcv_idx))
                rcv_count[rcv_idx] += 1

            print(rcv_count)
            for i in range(0, 2):
                self.assertTrue(
                    (rcv_count[i] >= ((max_itrs/2) * 0.8)), "Not all paths are equally balanced")
        finally:
            pass

    def tearDown(self):
        sai_thrift_remove_router_interface(self.client, self.port1_rif)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        super().tearDown()


class LoadbalanceOnSrcIPTest(T0TestBase):
    """
    Test load balance of l3 by source IP.
    """

    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self)

    def runTest(self):
        """
        1. Generate different packets by updating src ip
        2. send these packets on port1
        3. Check if packets are received on ports of lag1 equally
        """
        try:
            print("Lag l3 load balancing test based on src IP")
            self.port1_rif = sai_thrift_create_router_interface(self.client,
                                                                virtual_router_id=self.dut.default_vrf,
                                                                type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                                                                port_id=self.dut.port_list[1])
            max_itrs = 99
            rcv_count = [0, 0]
            for i in range(1, max_itrs):
                pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                        eth_src=self.servers[1][i].mac,
                                        ip_dst=self.servers[11][1].ipv4,
                                        ip_src=self.servers[1][i].ipv4,
                                        ip_id=105,
                                        ip_ttl=64)
                exp_pkt = simple_tcp_packet(eth_dst=self.t1_list[1][100].mac,
                                            eth_src=ROUTER_MAC,
                                            ip_dst=self.servers[11][1].ipv4,
                                            ip_src=self.servers[1][i].ipv4,
                                            ip_id=105,
                                            ip_ttl=63)
                send_packet(self, 1, pkt)
                rcv_idx, _ = verify_packet_any_port(
                    self, exp_pkt, self.dut.lag1.member_port_indexs)
                print('ip_src={}, rcv_port={}'.format(
                    self.servers[1][i].ipv4, rcv_idx))
                rcv_count[rcv_idx] += 1

            print(rcv_count)
            for i in range(0, 2):
                self.assertTrue(
                    (rcv_count[i] >= ((max_itrs/2) * 0.8)), "Not all paths are equally balanced")
        finally:
            pass

    def tearDown(self):
        sai_thrift_remove_router_interface(self.client, self.port1_rif)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        super().tearDown()


class LoadbalanceOnDesIPTest(T0TestBase):
    """
    Test load balance of l3 by destinstion IP.
    """

    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self)

    def runTest(self):
        """
        1. Generate different packets by updating des ip
        2. send these packets on port1
        3. Check if packets are received on ports of lag1 equally
        """
        try:
            print("Lag l3 load balancing test based on des IP")
            self.port1_rif = sai_thrift_create_router_interface(self.client,
                                                                virtual_router_id=self.dut.default_vrf,
                                                                type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                                                                port_id=self.dut.port_list[1])
            max_itrs = 99
            rcv_count = [0, 0]
            for i in range(1, max_itrs):
                pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                        eth_src=self.servers[1][1].mac,
                                        ip_dst=self.servers[11][i].ipv4,
                                        ip_src=self.servers[1][1].ipv4,
                                        ip_id=105,
                                        ip_ttl=64)
                exp_pkt = simple_tcp_packet(eth_dst=self.t1_list[1][100].mac,
                                            eth_src=ROUTER_MAC,
                                            ip_dst=self.servers[11][i].ipv4,
                                            ip_src=self.servers[1][1].ipv4,
                                            ip_id=105,
                                            ip_ttl=63)
                send_packet(self, 1, pkt)
                rcv_idx, _ = verify_packet_any_port(
                    self, exp_pkt, self.dut.lag1.member_port_indexs)
                print('des_src={}, rcv_port={}'.format(
                    self.servers[1][1].ipv4, rcv_idx))
                rcv_count[rcv_idx] += 1

            print(rcv_count)
            for i in range(0, 2):
                self.assertTrue(
                    (rcv_count[i] >= ((max_itrs/2) * 0.8)), "Not all paths are equally balanced")
        finally:
            pass

    def tearDown(self):
        sai_thrift_remove_router_interface(self.client, self.port1_rif)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        super().tearDown()


"""
Skip test for broadcom, can't load balance on protocol such as tcp and udp
Item: 15023123
"""


@skip
class LoadbalanceOnProtocolTest(T0TestBase):
    """
    Test load balance of l3 by protocol.
    """

    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self)

    def runTest(self):
        """
        1. Generate different packets with tcp and icmp
        2. send these packets on port1
        3. Check if packets are received on ports of lag1 equally
        """
        try:
            print("Lag l3 load balancing test based on protocal")
            self.port1_rif = sai_thrift_create_router_interface(self.client,
                                                                virtual_router_id=self.dut.default_vrf,
                                                                type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                                                                port_id=self.dut.port_list[1])
            max_itrs = 99
            rcv_count = [0, 0]
            for i in range(0, max_itrs):
                if i % 2 == 0:
                    pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                            eth_src=self.servers[1][1].mac,
                                            ip_dst=self.servers[11][1].ipv4,
                                            ip_src=self.servers[1][1].ipv4,
                                            ip_id=105,
                                            ip_ttl=64)
                    exp_pkt = simple_tcp_packet(eth_dst=self.t1_list[1][100].mac,
                                                eth_src=ROUTER_MAC,
                                                ip_dst=self.servers[11][1].ipv4,
                                                ip_src=self.servers[1][1].ipv4,
                                                ip_id=105,
                                                ip_ttl=63)
                else:
                    print("icmp")
                    pkt = simple_icmp_packet(eth_dst=ROUTER_MAC,
                                             eth_src=self.servers[1][1].mac,
                                             ip_dst=self.servers[11][1].ipv4,
                                             ip_src=self.servers[1][1].ipv4,
                                             ip_id=105,
                                             ip_ttl=64)
                    exp_pkt = simple_icmp_packet(eth_dst=self.t1_list[1][100].mac,
                                                 eth_src=ROUTER_MAC,
                                                 ip_dst=self.servers[11][1].ipv4,
                                                 ip_src=self.servers[1][1].ipv4,
                                                 ip_id=105,
                                                 ip_ttl=63)
                send_packet(self, 1, pkt)
                rcv_idx, _ = verify_packet_any_port(
                    self, exp_pkt, self.dut.lag1.member_port_indexs)
                print('des_src={}, rcv_port={}'.format(
                    self.servers[1][1].ipv4, rcv_idx))
                rcv_count[rcv_idx] += 1

            print(rcv_count)
            for i in range(0, 2):
                self.assertTrue(
                    (rcv_count[i] >= ((max_itrs/2) * 0.8)), "Not all paths are equally balanced")
        finally:
            pass

    def tearDown(self):
        sai_thrift_remove_router_interface(self.client, self.port1_rif)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        super().tearDown()


class DisableEgressTest(T0TestBase):
    """
    When disable egress on a lag member, we expect traffic drop on the disabled lag member.
    """

    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self)

    def runTest(self):
        """
        1. Generate different packets by updating src_port
        2. send these packets on port1
        3. Check if packets are received on ports of lag1 equally
        4. Disable port18 egress
        5. Generate different packets by updating src_port
        6. send these packets on port1
        7. Check if packets are received on port17
        """
        try:
            print("Lag disable egress lag member test")
            self.port1_rif = sai_thrift_create_router_interface(self.client,
                                                                virtual_router_id=self.dut.default_vrf,
                                                                type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                                                                port_id=self.dut.port_list[1])
            pkts_num = 10
            begin_port = 2000
            exp_drop = []
            for i in range(0, pkts_num):
                src_port = begin_port + i
                pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                        eth_src=self.servers[1][1].mac,
                                        ip_dst=self.servers[11][1].ipv4,
                                        ip_src=self.servers[1][1].ipv4,
                                        tcp_sport=src_port,
                                        ip_id=105,
                                        ip_ttl=64)
                exp_pkt = simple_tcp_packet(eth_dst=self.t1_list[1][100].mac,
                                            eth_src=ROUTER_MAC,
                                            ip_dst=self.servers[11][1].ipv4,
                                            ip_src=self.servers[1][1].ipv4,
                                            tcp_sport=src_port,
                                            ip_id=105,
                                            ip_ttl=63)
                send_packet(self, 1, pkt)
                rcv_idx, _ = verify_packet_any_port(
                    self, exp_pkt, self.dut.lag1.member_port_indexs)
                if rcv_idx == 18:
                    exp_drop.append(src_port)

            # disable egress of lag member: port18
            print("disable port18 egress")
            status = sai_thrift_set_lag_member_attribute(self.client,
                                                         self.dut.lag1.lag_members[1],
                                                         egress_disable=True)
            self.assertEqual(status, SAI_STATUS_SUCCESS)

            for i in range(0, pkts_num):
                src_port = begin_port + i
                pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                        eth_src=self.servers[1][1].mac,
                                        ip_dst=self.servers[11][1].ipv4,
                                        ip_src=self.servers[1][1].ipv4,
                                        tcp_sport=src_port,
                                        ip_id=105,
                                        ip_ttl=64)
                exp_pkt = simple_tcp_packet(eth_dst=self.t1_list[1][100].mac,
                                            eth_src=ROUTER_MAC,
                                            ip_dst=self.servers[11][1].ipv4,
                                            ip_src=self.servers[1][1].ipv4,
                                            tcp_sport=src_port,
                                            ip_id=105,
                                            ip_ttl=63)
                send_packet(self, 1, pkt)
                if src_port in exp_drop:
                    verify_no_packet(self, exp_pkt, 18)
                verify_packet(self, exp_pkt, 17)
        finally:
            pass

    def tearDown(self):
        sai_thrift_remove_router_interface(self.client, self.port1_rif)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        super().tearDown()


"""
Skip test for broadcom, can't disable ingress of lag member
Item: 14988584
"""


@skip
class DisableIngressTest(T0TestBase):

    """
    When disable ingress on a lag member, we expect traffic drop on the disabled lag member.
    """

    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self)

    def runTest(self):
        """
        1. Generate different packets by updating src_port
        2. send these packets on port 18
        3. Check if packets are received on port1
        4. Disable port18 ingress
        5. Generate same different packets in step 1 by updating src_port
        6. send these packets on port 18
        7. Check if packets are received on port1
        """
        try:
            print("Lag disable ingress lag member test")
            self.port1_rif = sai_thrift_create_router_interface(self.client,
                                                                virtual_router_id=self.dut.default_vrf,
                                                                type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                                                                port_id=self.dut.lag1.lag_id)
            pkts_num = 10
            begin_port = 2000
            for i in range(0, pkts_num):
                src_port = begin_port + i
                pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                        eth_src=self.t1_list[1][100].mac,
                                        ip_dst=self.servers[1][1].ipv4,
                                        ip_src=self.servers[11][1].ipv4,
                                        tcp_sport=src_port,
                                        ip_id=105,
                                        ip_ttl=64)
                exp_pkt = simple_tcp_packet(eth_dst=self.servers[1][1].mac,
                                            eth_src=ROUTER_MAC,
                                            ip_dst=self.servers[1][1].ipv4,
                                            ip_src=self.servers[11][1].ipv4,
                                            tcp_sport=src_port,
                                            ip_id=105,
                                            ip_ttl=63)
                send_packet(self, 18, pkt)
                verify_packet(self, exp_pkt, 1)
            # git disable ingress of lag member: port18
            print("disable port18 ingress")
            status = sai_thrift_set_lag_member_attribute(
                self.client, self.lag1.lag_members[1], ingress_disable=True)
            self.assertEqual(status, SAI_STATUS_SUCCESS)

            for i in range(0, pkts_num):
                src_port = begin_port + i
                pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                        eth_src=self.t1_list[1][100].mac,
                                        ip_dst=self.servers[1][1].ipv4,
                                        ip_src=self.servers[11][1].ipv4,
                                        tcp_sport=src_port,
                                        ip_id=105,
                                        ip_ttl=64)
                exp_pkt = simple_tcp_packet(eth_dst=self.servers[1][1].mac,
                                            eth_src=ROUTER_MAC,
                                            ip_dst=self.servers[1][1].ipv4,
                                            ip_src=self.servers[11][1].ipv4,
                                            tcp_sport=src_port,
                                            ip_id=105,
                                            ip_ttl=63)
                send_packet(self, 18, pkt)
                verify_no_packet(self, exp_pkt, 1)
        finally:
            pass

    def tearDown(self):
        sai_thrift_remove_router_interface(self.client, self.port1_rif)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        super().tearDown()


class RemoveLagMemberTest(T0TestBase):
    """
    When remove lag member, we expect traffic drop on the removed lag member.
    """

    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self)

    def runTest(self):
        """
        1. Generate different packets by updating src_port
        2. Send these packets on port1
        3. Check if packets are received on ports of lag1 equally
        4. Remove port18 in lag1 
        5. Generate same different packets in step 1 by updating src_port
        6. Send these packets on port1
        7. Check if packets aren't received on port18
        """
        try:
            print("Lag remove lag member test")
            self.port1_rif = sai_thrift_create_router_interface(self.client,
                                                                virtual_router_id=self.dut.default_vrf,
                                                                type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                                                                port_id=self.dut.port_list[1])

            pkts_num = 10
            begin_port = 2000
            for i in range(0, pkts_num):
                src_port = begin_port + i
                pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                        eth_src=self.servers[1][1].mac,
                                        ip_dst=self.servers[11][1].ipv4,
                                        ip_src=self.servers[1][1].ipv4,
                                        tcp_sport=src_port,
                                        ip_id=105,
                                        ip_ttl=64)
                exp_pkt = simple_tcp_packet(eth_dst=self.t1_list[1][100].mac,
                                            eth_src=ROUTER_MAC,
                                            ip_dst=self.servers[11][1].ipv4,
                                            ip_src=self.servers[1][1].ipv4,
                                            tcp_sport=src_port,
                                            ip_id=105,
                                            ip_ttl=63)
                send_packet(self, 1, pkt)
                verify_packet_any_port(
                    self, exp_pkt, self.dut.lag1.member_port_indexs)

            self.lag_configer.remove_lag_member_by_port_idx(
                lag_obj=self.dut.lag1, port_idx=18)

            for i in range(0, pkts_num):
                src_port = begin_port + i
                pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                        eth_src=self.servers[1][1].mac,
                                        ip_dst=self.servers[11][1].ipv4,
                                        ip_src=self.servers[1][1].ipv4,
                                        tcp_sport=src_port,
                                        ip_id=105,
                                        ip_ttl=64)
                exp_pkt = simple_tcp_packet(eth_dst=self.t1_list[1][100].mac,
                                            eth_src=ROUTER_MAC,
                                            ip_dst=self.servers[11][1].ipv4,
                                            ip_src=self.servers[1][1].ipv4,
                                            tcp_sport=src_port,
                                            ip_id=105,
                                            ip_ttl=63)
                send_packet(self, 1, pkt)
                verify_no_packet(self, exp_pkt, 18)
            self.lag_configer.create_lag_member(lag_obj=self.dut.lag1,
                                                lag_port_idxs=range(18, 19))
        finally:
            pass

    def tearDown(self):
        sai_thrift_remove_router_interface(self.client, self.port1_rif)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        super().tearDown()


class AddLagMemberTest(T0TestBase):
    """
    When  add lag member, we expect traffic appear on the added lag member.
    """

    def setUp(self):
        """
        set up configurations
        """
        T0TestBase.setUp(self)

    def runTest(self):
        """
        1. Generate different packets by updating src_port
        2. Send these packets on port1
        3. Check if packets are received on ports of lag1 equally
        4. Add port21 as lag1 member
        5. Generate same different packets in step 1 by updating src_port
        6. Send these packets on port1
        7. Check if packets are received on lag1(port 17,18,21)
        """
        try:
            print("Lag add lag member test")
            self.port1_rif = sai_thrift_create_router_interface(self.client,
                                                                virtual_router_id=self.dut.default_vrf,
                                                                type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                                                                port_id=self.dut.port_list[1])
            pkts_num = 10
            begin_port = 2000
            rcv_count = [0, 0, 0]
            for i in range(0, pkts_num):
                src_port = begin_port + i
                pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                        eth_src=self.servers[1][1].mac,
                                        ip_dst=self.servers[11][1].ipv4,
                                        ip_src=self.servers[1][1].ipv4,
                                        tcp_sport=src_port,
                                        ip_id=105,
                                        ip_ttl=64)
                exp_pkt = simple_tcp_packet(eth_dst=self.t1_list[1][100].mac,
                                            eth_src=ROUTER_MAC,
                                            ip_dst=self.servers[11][1].ipv4,
                                            ip_src=self.servers[1][1].ipv4,
                                            tcp_sport=src_port,
                                            ip_id=105,
                                            ip_ttl=63)
                send_packet(self, 1, pkt)
                verify_packet_any_port(
                    self, exp_pkt, self.dut.lag1.member_port_indexs)
            print("add port21 into lag1")
            self.lag_configer.create_lag_member(lag_obj=self.dut.lag1,
                                                lag_port_idxs=range(21, 22))
            for i in range(0, pkts_num):
                src_port = begin_port + i
                pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                        eth_src=self.servers[1][1].mac,
                                        ip_dst=self.servers[11][1].ipv4,
                                        ip_src=self.servers[1][1].ipv4,
                                        tcp_sport=src_port,
                                        ip_id=105,
                                        ip_ttl=64)
                exp_pkt = simple_tcp_packet(eth_dst=self.t1_list[1][100].mac,
                                            eth_src=ROUTER_MAC,
                                            ip_dst=self.servers[11][1].ipv4,
                                            ip_src=self.servers[1][1].ipv4,
                                            tcp_sport=src_port,
                                            ip_id=105,
                                            ip_ttl=63)
                send_packet(self, 1, pkt)
                rcv_idx, _ = verify_packet_any_port(
                    self, exp_pkt, self.dut.lag1.member_port_indexs)
                rcv_count[rcv_idx] += 1
            for cnt in rcv_count:
                self.assertGreater(
                    cnt, 0, "each member in lag1 should receive pkt")
            self.lag_configer.remove_lag_member_by_port_idx(
                lag_obj=self.dut.lag1, port_idx=21)
        finally:
            pass

    def tearDown(self):
        sai_thrift_remove_router_interface(self.client, self.port1_rif)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        super().tearDown()


class IndifferenceIngressPortTest(T0TestBase):
    """
    Verify the ingress ports should not be as a hash factor in lag load balance.
    Forwarding the same packet from different ingress ports, if only the ingress
    port changed, the load balance should not happen among lag members.
    """

    def setUp(self):
        T0TestBase.setUp(self)

    def runTest(self):
        try:
            self.vlan10_rif = sai_thrift_create_router_interface(self.client,
                                                                virtual_router_id=self.dut.default_vrf,
                                                                type=SAI_ROUTER_INTERFACE_TYPE_VLAN,
                                                                vlan_id=10)
            pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                    eth_src=self.servers[1][1].mac,
                                    ip_dst=self.servers[11][1].ipv4,
                                    ip_src=self.servers[1][1].ipv4,
                                    ip_id=105,
                                    ip_ttl=64)
            exp_pkt = simple_tcp_packet(eth_dst=self.t1_list[1][100].mac,
                                        eth_src=ROUTER_MAC,
                                        ip_dst=self.servers[11][1].ipv4,
                                        ip_src=self.servers[1][1].ipv4,
                                        ip_id=105,
                                        ip_ttl=63)

            exp_port_idx = -1
            exp_port_list = self.dut.lag1.member_port_indexs
            for i in range(1, 9):
                send_packet(self, i, pkt)
                if exp_port_idx == -1:
                    exp_port_idx, _ = verify_packet_any_port(
                        self, exp_pkt, exp_port_list)
                else:
                    verify_packet(self, exp_pkt, exp_port_list[exp_port_idx])
        finally:
            pass

    def tearDown(self):
        sai_thrift_remove_router_interface(self.client, self.vlan10_rif)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        super().tearDown()
