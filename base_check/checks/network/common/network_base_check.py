# -*- coding: utf-8 -*-
import os
from base_check.common.shell import shell
from base_check.common import log as logging

LOG = logging.getLogger(__name__)


class NetworkExamine():

    def __init__(self, path='/sys/class/net/'):
        self.target_network_devices = os.listdir(path)

    def network_device_check(self, target_network_device):
        if target_network_device in self.target_network_devices:
            LOG.debug('%s:ok' % target_network_device)
        else:
            LOG.error("%s:None" % target_network_device)

    def network_device_state_check(self, target_network_device):
        cmd = "cat /sys/class/net/%s/operstate" % target_network_device
        if target_network_device in self.target_network_devices:
            target_network_device_state_var = shell(cmd).stdout
            if target_network_device_state_var.strip('\n') == 'up':
                LOG.debug('%s:UP' % target_network_device)
            else:
                LOG.error('%s:DOWN' % target_network_device)
        else:
            LOG.warn('%s:None' % target_network_device)

    def network_device_mtu_check(
            self, target_network_device, target_network_mtu):
        cmd = "cat /sys/class/net/%s/mtu" % target_network_device
        if target_network_device in self.target_network_devices:
            target_network_device_mtu_var = shell(cmd).stdout
            if target_network_mtu == int(target_network_device_mtu_var):
                LOG.debug('%s MTU:%s' % (target_network_device,
                                         int(target_network_device_mtu_var)))
            else:
                LOG.error('%s MTU:%s' % (target_network_device,
                                         int(target_network_device_mtu_var)))
        else:
            LOG.warn('%s:None' % target_network_device)

    def network_device_speed_check(
            self, target_network_device, target_network_speed):
        cmd = "cat /sys/class/net/%s/speed" % target_network_device
        if target_network_device in self.target_network_devices:
            target_network_device_speed_var = shell(cmd).stdout
            if not target_network_device_speed_var:
                LOG.error('%s Speed:Err' % target_network_device)
            elif target_network_speed == int(target_network_device_speed_var):
                LOG.debug('%s Speed:%s'
                          % (target_network_device,
                             int(target_network_device_speed_var)))
            else:
                LOG.error('%s Speed:%s'
                          % (target_network_device,
                             int(target_network_device_speed_var)))
        else:
            LOG.warn('%s:None' % target_network_device)

    def network_device_mac_check(self, target_network_device):
        cmd = "cat /sys/class/net/%s/address" % target_network_device
        if target_network_device in self.target_network_devices:
            target_network_device_mac_var = shell(cmd).stdout
            LOG.debug('MAC:%s' % (target_network_device_mac_var).strip('\n'))
        else:
            LOG.warn('MAC:None')

    def network_device_ipaddress_check(self, target_network_device):
        cmd = "ip -o a|grep %s|awk NR==1|grep -w inet|awk '{print $4}'" \
              % target_network_device
        if target_network_device in self.target_network_devices:
            target_device_ipaddress = shell(cmd).stdout
            if target_device_ipaddress:
                LOG.debug('IP:%s' % target_device_ipaddress.strip('\n'))
            else:
                LOG.warn('%s:noIP' % target_network_device)
        else:
            LOG.warn('%s:None' % target_network_device)

    def network_device_fiber_check(self, target_network_device):
        cmd = "cat /sys/class/net/%s/operstate" % target_network_device
        cmd1 = "ethtool %s|grep 'Supported ports'|awk '{print $4}'" \
              % target_network_device
        cmd2 = "ethtool -m %s|grep 'Laser bias current   '|" \
               "awk '{print $5}'" % target_network_device
        if target_network_device in self.target_network_devices:
            target_network_device_state_var = shell(cmd).stdout.upper()
            if target_network_device_state_var.strip('\n') == 'UP':
                target_network_device_type = shell(cmd1).stdout.upper()
                if target_network_device_type == 'FIBRE':
                    laser_bias = shell(cmd2).stdout
                    if not laser_bias:
                        LOG.info('%s bias:null' % target_network_device)
                        pass
                    elif float(laser_bias) > 12:
                        LOG.info('%s bias:%s' % (target_network_device,
                                                 laser_bias))
                    else:
                        LOG.debug('%s bias:%s' % (target_network_device,
                                                 laser_bias))
                else:
                    LOG.debug('%s:TP' % target_network_device)
            else:
                LOG.debug('%s:down' % target_network_device)
        else:
            LOG.debug('%s:None' % target_network_device)
