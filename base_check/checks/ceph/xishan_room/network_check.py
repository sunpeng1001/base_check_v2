# -*- coding:utf-8 -*-
from base_check.common.utils import BaseCheck
from base_check.common import log as logging
from base_check.common.shell import shell
from base_check.checks.ceph.common.network_check import NetworkExamine

LOG = logging.getLogger(__name__)


class NetworkCheck(BaseCheck):

    def check_network(self, conf):
        network = NetworkExamine()

        if not network.check_network_number(conf.counts):
            return

        cmd = "ip -o -4 a |awk '{print $4}'"
        local_ip_set = shell(cmd).stdout.replace('/24', '').split()
        manger_ip = ''.join(set(conf.macs.keys()) & set(local_ip_set))
        mac_list = conf.macs[manger_ip]
        network.check_network_mac(mac_list)
        network.check_network_numa_node(conf.speeds)
        network.check_network_interrupt_node(conf.speeds)
        network.check_network_vendor(conf.vendors)
        network.check_network_version(conf.versions)
