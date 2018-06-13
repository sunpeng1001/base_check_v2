# -*- coding: utf-8 -*-
import os
from base_check.common.shell import shell
from base_check.common import log as logging

LOG = logging.getLogger(__name__)


class BondDeviceOnOffCheck():

    def __init__(self):
        self.device_list = os.listdir('/sys/class/net/')

    def pre_check(self, target_device):
        if target_device in self.device_list:
            if os.path.exists('/proc/net/bonding'):
                target_network_bond_device = os.listdir('/proc/net/bonding')
                if target_device in target_network_bond_device:
                    return True
        return False

    def phy_device_state_check(self, target_device):
        bonding_slaves_state = []
        if self.pre_check(target_device):
            cmd2 = "cat /proc/net/bonding/%s | grep 'Slave Interface' " \
                   "| awk '{print $3}'" % target_device
            bonding_slaves = shell(cmd2).stdout.replace('\n', ' ')
            cmd3 = "for i in %s ;do cat /sys/class/net/$i/operstate ;done" \
                   % bonding_slaves
            bonding_slaves_state = shell(cmd3).stdout.\
                replace('\n', ' ').split()
        return bonding_slaves_state

    def phy_device_check(self, target_device):
        bonding_slaves_set = set()
        if self.pre_check(target_device):
            cmd = "cat /proc/net/bonding/%s | grep 'Slave Interface' " \
                  "| awk '{print $3}'" % target_device
            bonding_slaves_set = set(shell(cmd).stdout.
                                     replace('\n', ' ').split())
        return bonding_slaves_set

    def set_phy_device_down(self, phy_device):
        cmd = "ip link set %s down" % phy_device
        shell(cmd, 10)

    def set_phy_device_up(self, phy_device):
        cmd = "ip link set %s up" % phy_device
        shell(cmd, 10)
