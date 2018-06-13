# -*- coding: utf-8 -*-
# import os
from base_check.common.shell import shell
from base_check.common import log as logging

LOG = logging.getLogger(__name__)


class NetworkExamine():

    def __init__(self):
        cmd = "esxcli network nic list | awk  NR\>2'{print $1}'"
        self.target_network_devices = shell(cmd).stdout

    def network_device_check(self, target_network_device):
        if target_network_device in self.target_network_devices:
            LOG.debug('%s:' % target_network_device)
            return True
        else:
            LOG.debug('%s:None' % target_network_device)
            return False

    def network_device_state_check(self, target_network_device):
        cmd = "esxcli network nic list | grep %s | awk '{print $5}'" \
              % target_network_device
        if target_network_device in self.target_network_devices:
            target_network_device_state_var = shell(cmd).stdout
            if target_network_device_state_var == 'Up':
                LOG.debug('%s:up' % target_network_device)
            else:
                LOG.error('%s:down' % target_network_device)
        else:
            LOG.warn('%s:state:error' % target_network_device)

    def network_device_mtu_check(self, target_network_device,
                               target_network_mtu):
        cmd = "esxcli network nic list | grep %s | awk '{print $9}'" \
              % target_network_device
        if target_network_device in self.target_network_devices:
            target_network_device_mtu_var = shell(cmd).stdout
            if target_network_mtu == int(target_network_device_mtu_var):
                LOG.debug('%s:%s' % (target_network_device,
                                     int(target_network_device_mtu_var)))
            else:
                LOG.error('%s:%s' % (target_network_device,
                                     int(target_network_device_mtu_var)))
        else:
                LOG.warn('%s:mtu:0' % target_network_device)

    def network_device_speed_check(self, target_network_device,
                                 target_network_speed):
        cmd = "esxcli network nic list | grep %s | awk '{print $6}'" \
              % target_network_device
        if target_network_device in self.target_network_devices:
            target_network_device_speed_var = shell(cmd).stdout
            if target_network_speed == int(target_network_device_speed_var):
                LOG.debug('%s:%s' % (target_network_device,
                                     int(target_network_device_speed_var)))
            else:
                LOG.error('%s:%s' % (target_network_device,
                                     int(target_network_device_speed_var)))
        else:
            LOG.warn('%s:None' % target_network_device)
