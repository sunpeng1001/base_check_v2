# -*- coding: utf-8 -*-
from base_check.common.shell import shell
from base_check.common import log as logging
import time

LOG = logging.getLogger(__name__)


class EsxiVswichCheck():

    def __init__(self):
        cmd = "esxcli network nic list | awk  NR\>2'{print $1}'"
        self.target_network_devices = shell(cmd).stdout
        cmd1 = "esxcli network vswitch standard list | grep 'Name:' " \
               "|sort| awk '{print $2}'"
        self.target_network_vswich = shell(cmd1).stdout

    def pre_check_vswitch(self, target_device):
        if target_device in self.target_network_vswich:
            return True
        return False

    def vswitch_uplinks(self, target_device):
        cmd = "esxcfg-vswitch -l | grep %s | awk '{print $6}'" \
              % target_device
        standard_uplinks = shell(cmd).stdout
        return set(standard_uplinks.split(","))

    def uplinks_down(self, target_device):
        cmd = "esxcli network nic down -n=%s" % target_device
        shell(cmd)
        cmd1 = "esxcli network nic list | grep %s | awk '{print $5}'" \
               % target_device
        time.sleep(1)
        link_status = shell(cmd1).stdout.lower()
        if link_status == "down":
            LOG.debug('%s:down success!' % target_device)
        elif link_status == "up":
            LOG.info('%s:down failed!' % target_device)
        else:
            LOG.info('%s:status error!' % target_device)

    def uplinks_up(self, target_device):
        cmd = "esxcli network nic up -n=%s" % target_device
        shell(cmd)
        cmd1 = "esxcli network nic list | grep %s | awk '{print $5}'" \
               % target_device
        time.sleep(4)
        link_status = shell(cmd1).stdout.lower()
        if link_status == "up":
            LOG.debug('%s:up success!' % target_device)
        elif link_status == "down":
            LOG.info('%s:up failed!' % target_device)
        else:
            LOG.info('%s:status error!' % target_device)

    def vmnic_status(self, target_device):
        cmd = "esxcli network nic list | grep %s | awk '{print $5}'" \
               % target_device
        link_status = shell(cmd).stdout.lower()
        return link_status
