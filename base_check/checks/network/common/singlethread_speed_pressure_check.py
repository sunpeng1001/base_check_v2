# -*- coding: utf-8 -*-
from base_check.common.shell import shell
from base_check.common import log as logging
from speed_pressure_check import NetworkSpeedPressureExamine

LOG = logging.getLogger(__name__)


class SingleThreadNetworkSpeedPressureExamine(NetworkSpeedPressureExamine):

    def __init__(self):
        super(SingleThreadNetworkSpeedPressureExamine, self).__init__()
        self.device_ip_dict = {}
        self.generate_avaiable_device_and_ip_dict()

    def device_iperf_client_single_check(self, target_ip, check_time):
        cmd = "iperf -c %s -t %d &>/dev/null&" % (target_ip, check_time)
        shell(cmd)

    def generate_avaiable_device_and_ip_dict(self):
        for device in self.device_list:
            device_ipaddr = self.device_ipaddr_check(device)
            if device_ipaddr and device != 'lo':
                self.local_device_list.append(device)
                self.local_ip_list.append(device_ipaddr)
        self.device_ip_dict = dict(zip(self.local_device_list,
                                       self.local_ip_list))

    def iperf_client_host_list(self, target_device,
                               manager_ip_segment, test_cluster_host):
        iperf_client_cluster_list = []
        mgmt_device_ipaddr = self.get_manager_ip(
            manager_ip_segment)
        mgmt_ip = mgmt_device_ipaddr.split('.', 4)
        for host in self.iperf_host_list(
                manager_ip_segment, test_cluster_host):
            local_ip = self.device_ip_dict[target_device]
            ip_seg_list = local_ip.split('.', 4)
            D_value = int(ip_seg_list[3]) - int(mgmt_ip[3])
            ip_seg_list[3] = str(int(host) + D_value)
#            ip_seg_list[3] = str(host)
            target_iperf_server_ip = '.'.join(ip_seg_list)
            iperf_client_cluster_list.append(target_iperf_server_ip)
        return iperf_client_cluster_list
