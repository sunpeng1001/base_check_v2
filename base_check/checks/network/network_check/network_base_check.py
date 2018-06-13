# -*- coding: utf-8 -*-
from base_check.common.utils import BaseCheck
from base_check.common import log as logging
from base_check.checks.network.common.network_base_check import NetworkExamine

LOG = logging.getLogger(__name__)


class NetworkBaseCheck(BaseCheck):

    def check_base_network_conf(self, conf):
        a = NetworkExamine()
        for target_net_device in conf.device_conf.keys():
            target_net_device_mtu = conf.device_conf[target_net_device]['MTU']
            target_net_device_speed = \
                conf.device_conf[target_net_device]['speed']
            a.network_device_check(target_net_device)
            a.network_device_state_check(target_net_device)
            a.network_device_mtu_check(
                target_net_device, target_net_device_mtu)
            a.network_device_speed_check(
                target_net_device, target_net_device_speed)
            a.network_device_mac_check(target_net_device)
            a.network_device_ipaddress_check(target_net_device)
            a.network_device_fiber_check(target_net_device)
            LOG.info(' ')
