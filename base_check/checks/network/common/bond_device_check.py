# -*- coding: utf-8 -*-
import os
from base_check.common.shell import shell
from base_check.common import log as logging

LOG = logging.getLogger(__name__)


class BondDeviceCheck():

    def __init__(self):
        self.device_list = os.listdir('/sys/class/net/')
        self.bond_mode_list = {'mode0': 'load balancing (round-robin)',
                          'mode1': 'fault-tolerance (active-backup)',
                          'mode2': 'load balancing (xor)',
                          'mode3': 'fault-tolerance (broadcast)',
                          'mode4': 'IEEE 802.3ad Dynamic link aggregation',
                          'mode5': 'transmit load balancing',
                          'mode6': 'adaptive load balancing'}

    def pre_check(self, target_device):
        if target_device in self.device_list:
            if os.path.exists('/proc/net/bonding'):
                target_network_bond_device = os.listdir('/proc/net/bonding')
                if target_device in target_network_bond_device:
                    return True
        return False

    def bond_mode_check(self, target_device):
        cmd = "cat /proc/net/bonding/%s | grep 'Bonding Mode' " \
              "| awk -F ':' '{print $2}'" % target_device
        bond_mode = shell(cmd).stdout.strip()
        for mode_name, mode_alg in self.bond_mode_list.items():
            if mode_alg == bond_mode:
                return mode_name
        return None

    def phy_device_state_check(self, target_device):
        cmd1 = "cat /proc/net/bonding/%s | grep 'Slave Interface' " \
               "| awk '{print $3}'" % target_device
        bonding_slaves = shell(cmd1).stdout.replace('\n', ' ')
        cmd2 = "for i in %s ;do cat /sys/class/net/$i/operstate ;done" \
               % bonding_slaves
        bonding_slaves_state = shell(cmd2).stdout.replace('\n', ' ').split()
        slave_state_dict = dict(zip(bonding_slaves.split(),
                                    bonding_slaves_state))
        return slave_state_dict

    def phy_device_speed_check(self, phy_device):
        cmd = "cat /sys/class/net/%s/speed" % phy_device
        phy_device_speed = shell(cmd).stdout
        return phy_device_speed

    def phy_device_check(self, target_device):
        cmd = "cat /proc/net/bonding/%s | grep 'Slave Interface' " \
              "| awk '{print $3}'" % target_device
        bonding_slaves_set = set(shell(cmd).stdout.replace('\n', ' ').split())
        return bonding_slaves_set
