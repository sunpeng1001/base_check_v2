# -*- coding: utf-8 -*-
from base_check.common.utils import BaseCheck
from base_check.common import log as logging
from base_check.checks.network.common.esxi_network_base_check \
   import NetworkExamine

LOG = logging.getLogger(__name__)


class NetworkBaseCheck(BaseCheck):

    def check_base_network_conf(self, conf):
        a = NetworkExamine()
        for target_net_device in conf.device_conf.keys():
            if a.network_device_check(target_net_device):
                target_net_device_mtu = \
                    conf.device_conf[target_net_device]['MTU']
                target_net_device_speed = \
                    conf.device_conf[target_net_device]['speed']
                a.network_device_check(target_net_device)
                a.network_device_state_check(target_net_device)
                a.network_device_mtu_check(
                    target_net_device, target_net_device_mtu)
                a.network_device_speed_check(
                    target_net_device, target_net_device_speed)
            else:
                LOG.warn('%s:None' % target_net_device)
