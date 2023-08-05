#!/usr/bin/env python
#
#   Copyright 2013 Hewlett-Packard Development Company, L.P.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from hpsdnclient.tests.base import ApiTestCase
from hpsdnclient.error import OpenflowProtocolError, VersionMismatch, NotFound
import hpsdnclient.datatypes

OF10_DPID = '00:00:00:00:00:00:00:0b'


class TestOfMixin10(ApiTestCase):
    def setUp(self):
        super(TestOfMixin10, self).setUp()

    def tearDown(self):
        super(TestOfMixin10, self).tearDown()

    def _flow_exists(self, flow):
        match_fields = ['eth_type', 'ipv4_src', 'ipv4_dst',
                        'ip_proto', 'tcp_dst']
        action_fields = ['output']

        for f in self._api.get_flows(OF10_DPID):

            if not flow.priority == f.priority:
                continue
            else:
                for a in action_fields:
                    if not (flow.actions.__getattribute__(a) ==
                                f.actions.__getattribute__(a)):
                        break
                else:
                    for m in match_fields:
                        if not (flow.match.__getattribute__(m) ==
                                    f.match.__getattribute__(m)):
                            break
                    else:
                        return True
        return False

    def test_get_stats(self):
        data = self._api.get_stats()
        self.assertTrue(data)

    def test_get_port_stats(self):
        data = self._api.get_port_stats(OF10_DPID, 1)
        self.assertTrue(data)

    def test_get_group_stats(self):
        self.assertRaises(VersionMismatch, self._api.get_group_stats,
                          OF10_DPID, 1)

    def test_get_meter_stats(self):
        self.assertRaises(NotFound, self._api.get_meter_stats,
                          OF10_DPID, 1)

    def test_get_datapaths(self):
        data = self._api.get_datapaths()
        self.assertTrue(data)

    def test_get_datapath_detail(self):
        data = self._api.get_datapath_detail(OF10_DPID)
        self.assertTrue(data)

    def test_get_datapath_meter_features(self):
        self.assertRaises(NotFound,
                          self._api.get_datapath_meter_features, OF10_DPID)

    def test_get_datapath_group_features(self):
        self.assertRaises(VersionMismatch,
                          self._api.get_datapath_group_features, OF10_DPID)

    def test_get_ports(self):
        data = self._api.get_ports(OF10_DPID)
        self.assertTrue(data)

    def test_get_port_detail(self):
        data = self._api.get_port_detail(OF10_DPID, 1)
        self.assertTrue(data)

    def test_get_meters(self):
        self.assertRaises(OpenflowProtocolError,
                          self._api.get_meters, OF10_DPID)

    def test_get_meter_details(self):
        self.assertRaises(OpenflowProtocolError,
                          self._api.get_meter_details,
                          OF10_DPID, 1)

    def test_get_flows(self):
        data = self._api.get_flows(OF10_DPID)
        self.assertTrue(data)


    def test_get_groups(self):
        self.assertRaises(VersionMismatch, self._api.get_groups, OF10_DPID)

    def test_get_group_details(self):
        self.assertRaises(VersionMismatch,
                          self._api.get_group_details,
                          OF10_DPID, 1)

    def test_add_flow(self):
        match = hpsdnclient.datatypes.Match(eth_type="ipv4",
                                            ipv4_src="10.0.0.1",
                                            ipv4_dst="10.0.0.22",
                                            ip_proto="tcp",
                                            tcp_dst=80)
        output6 = hpsdnclient.datatypes.Action(output=6)
        flow = hpsdnclient.datatypes.Flow(priority=12345, idle_timeout=30,
                                          match=match, actions=output6)
        self._api.add_flows(OF10_DPID, flow)
        self.assertTrue(self._flow_exists(flow))

    def test_delete_flow(self):
        match = hpsdnclient.datatypes.Match(eth_type="ipv4",
                                            ipv4_src="10.0.0.1",
                                            ipv4_dst="10.0.0.22",
                                            ip_proto="tcp",
                                            tcp_dst=80)
        output6 = hpsdnclient.datatypes.Action(output=6)
        flow = hpsdnclient.datatypes.Flow(priority=12345, idle_timeout=30,
                                          match=match, actions=output6)

        self.assertTrue(self._flow_exists(flow))
        self._api.delete_flows(OF10_DPID, flow)
        self.assertFalse(self._flow_exists(flow))

