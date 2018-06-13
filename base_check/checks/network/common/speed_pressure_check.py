# -*- coding: utf-8 -*-
import os
import time
from base_check.common.shell import shell
from base_check.common import log as logging

LOG = logging.getLogger(__name__)


class NetworkSpeedPressureExamine(object):

    def __init__(self):
        self.local_ip_list = []
        self.local_device_list = []
        self.device_list = os.listdir('/sys/class/net/')

    def device_ipaddr_check(self, device_name):
        cmd1 = "ip -o -4 a |awk '{print $2}'"
        cmd2 = "cat /proc/net/bonding/*|" \
               "grep 'Slave Interface'|awk '{print $3}'"
        cmd3 = "ip -o -4 a |grep %s|awk NR==1|awk '{print $4}'" % device_name
        device_which_has_ipaddr = shell(cmd1).stdout.strip().split('\n')
        if os.path.exists("/proc/net/bonding"):
            bonding_slave = shell(cmd2).stdout.strip().split()
            if device_name in bonding_slave \
                    or device_name not in device_which_has_ipaddr:
                device_ipaddr = ''
            else:
                device_ipaddr = shell(cmd3).stdout.split('/', 2)[0]
        elif not os.path.exists("/proc/net/bonding") \
                and device_name in device_which_has_ipaddr:
            device_ipaddr = shell(cmd3).stdout.split('/', 2)[0]
        else:
            device_ipaddr = ''
        return device_ipaddr

    def firewalld_service_stop(self):
        cmd1 = "systemctl status firewalld" \
               "|grep -w active|awk '{print $2}'"
        cmd2 = "systemctl stop firewalld"
        firewalld_service_state = shell(cmd1).stdout
        if firewalld_service_state.strip() == 'active':
            shell(cmd2)
            return 0
        else:
            return 1

    def firewalld_service_start(self):
        cmd1 = "systemctl start firewalld"
        shell(cmd1)

    def ensure_iperf_rpm_install(self):
        cmd1 = "rpm -qa | grep iperf &>/dev/null;echo $?"
        check_result = shell(cmd1).stdout
        if int(check_result) != 0:
            cmd2 = "yum install iperf -y &>/dev/null"
            shell(cmd2, timeout=10)

    def device_iperf_server_check(self):
        cmd1 = "iperf -s &>/tmp/iperf_server.txt &"
        shell(cmd1)

    def device_iperf_clinet_check(self, target_ip, check_time):
        cmd1 = "iperf -c %s -t %d &>/dev/null&" \
               % (target_ip, check_time)
        shell(cmd1)

    def kill_iperf_server(self):
        cmd1 = "for i in $(pidof iperf);do kill -9 $i;done"
        shell(cmd1)

    def iperf_server_client_num_check(self, device_name):
        device_ipaddr = self.device_ipaddr_check(device_name)
        if device_ipaddr == '':
            client_num = 0
        else:
            client_num_cmd = "cat /tmp/iperf_server.txt|grep %s" \
                                "|sort|uniq|wc -l" % device_ipaddr
            client_num = shell(client_num_cmd).stdout
        return int(client_num)

    def get_device_conf_speed(self, device_name):
        device_speed_num = "cat /sys/class/net/%s/speed" % device_name
        device_speed = shell(device_speed_num).stdout
        return int(device_speed)

    def network_device_receive_flow_check(self, device_name, check_time):
        device_speed = self.get_device_conf_speed(device_name)
        eligible_speed = device_speed * 0.8
        device_receive_flow_value = "cat /proc/net/dev " \
                          "| grep %s | awk '{print $2}'" % device_name
        device_receive_flow_init = shell(device_receive_flow_value).stdout
        time.sleep(check_time)
        device_receive_flow_ult = shell(device_receive_flow_value).stdout
        device_receive_flow = ((int(device_receive_flow_ult) -
                                int(device_receive_flow_init)) /
                               check_time) * 8
        client_num = self.iperf_server_client_num_check(device_name)
        if device_receive_flow < 1024:
            device_receive_flow = device_receive_flow
            LOG.error('%s:Error(%db/s[%d])'
                      % (device_name, device_receive_flow, client_num))
        elif device_receive_flow >= 1024 \
                and device_receive_flow < (1024 * 1024):
            device_receive_flow = device_receive_flow / 1024
            LOG.error('%s:Error(%dKb/s[%d])'
                      % (device_name, device_receive_flow, client_num))
        elif device_receive_flow >= (1024 * 1024)  \
                and device_receive_flow < (1024 * 1024 * 1024):
            device_receive_flow = device_receive_flow / (1024 * 1024)
            if device_receive_flow < eligible_speed:
                LOG.error('%s:Error(%dMb/s[%d])'
                          % (device_name, device_receive_flow, client_num))
            else:
                LOG.debug('%s:%dMb/s(%d)'
                          % (device_name, device_receive_flow, client_num))
        else:
            device_receive_flow = round(float(device_receive_flow) /
                                        (1024 * 1024 * 1024), 1)
            if device_receive_flow <= (eligible_speed / 1000):
                LOG.error('%s:Error(%.1fGb/s[%d])'
                          % (device_name, device_receive_flow, client_num))
            else:
                LOG.debug('%s:%.1fGb/s(%d)'
                          % (device_name, device_receive_flow, client_num))

    def test_file_delete(self):
            test_file = '/tmp/iperf_server.txt'
            os.remove(test_file)

    def add_avaiable_device_and_ip_list(self, target_devices):
        for device in target_devices:
            device_ipaddr = self.device_ipaddr_check(device)
            if device_ipaddr and device != 'lo':
                self.local_device_list.append(device)
                self.local_ip_list.append(device_ipaddr)

    def get_manager_ip(self, manager_ip_segment):
        cmd = "ip -o a|grep %s|awk NR==1|grep -w inet" \
              "|awk '{print $4}'" % manager_ip_segment
        target_device_ipaddress = shell(cmd).stdout.split('/', 2)[0]
        return target_device_ipaddress

    def change_list_format(self, init_list):
        fin_list = []
        init_list = init_list.strip('[').strip(']').split(',')
        for i in init_list:
            if ':' not in i:
                fin_list.append(int(i))
            else:
                t = i.split(':')
                start = t[0]
                end = t[1]
                fin_list += range(int(start), int(end) + 1)
        return fin_list

    def iperf_host_list(self, manager_ip_segment, test_cluster_host):
        test_iperf_server_list = []
        if len(test_cluster_host) >= 4:
            test_iperf_server_list = []
            local_device_ipaddr = self.get_manager_ip(
                manager_ip_segment)
            list = local_device_ipaddr.split('.', 4)
            if int(list[3]) in test_cluster_host:
                index_position = test_cluster_host.index(int(list[3]))
                test_iperf_server_list = \
                    [test_cluster_host[(i + index_position + 1)
                                       % len(test_cluster_host)]
                     for i in xrange(3)]
        return test_iperf_server_list

    def iperf_host_cluster(self, manager_ip_segment, test_cluster_host):
        iperf_client_cluster_list = []
        mgmt_device_ipaddr = self.get_manager_ip(
            manager_ip_segment)
        mgmt_ip = mgmt_device_ipaddr.split('.', 4)
        for host in self.iperf_host_list(
                manager_ip_segment, test_cluster_host):
            for local_ip in self.local_ip_list:
                list = local_ip.split('.', 4)
                D_value = int(list[3]) - int(mgmt_ip[3])
                list[3] = str(int(host) + D_value)
                target_iperf_server_ip = '.'.join(list)
                iperf_client_cluster_list.append(target_iperf_server_ip)
        return iperf_client_cluster_list
