# -*- coding: utf-8 -*-
from base_check.common.utils import BaseCheck
from base_check.common.shell import shell
from base_check.checks.network.common.mac_check import MacExamine
from base_check.checks.network.common.mac_check import device_list
from base_check.common import log as logging

LOG = logging.getLogger(__name__)


class MacCheck(BaseCheck):

    def check_mac(self, conf):
        a = MacExamine()
        cmd1 = "ip -o -4 a |awk '{print $4}'"
        local_ip_set = shell(cmd1).stdout.replace('/24', '').split()
        manger_ip = ''.join(set(conf.macs.keys()) & set(local_ip_set))
        server_device_mac_file_list = conf.macs[manger_ip]
        for device in server_device_mac_file_list.keys()[::-1]:
            server_mac = a.get_network_device_mac(device)
            if server_mac == server_device_mac_file_list[device].lower():
                LOG.debug('%s:OK' % device)
            elif device not in device_list:
                LOG.warn('%s:%s' % (device, server_mac))
            elif server_device_mac_file_list[device] == '':
                LOG.warn('%s:%s' % (device, server_mac))
            else:
                LOG.error('%s:Error' % device)
