# -*- coding: utf-8 -*-
import time
from base_check.common.utils import BaseCheck
from base_check.checks.network.common.singlethread_speed_pressure_check \
    import SingleThreadNetworkSpeedPressureExamine
from base_check.common import log as logging


LOG = logging.getLogger(__name__)


class NetworkSpeedPressureCheck(BaseCheck):

    def check_speed_pressure(self, conf):
        a = SingleThreadNetworkSpeedPressureExamine()
        firewalld_state = a.firewalld_service_stop()
        a.ensure_iperf_rpm_install()
        a.device_iperf_server_check()
        for device in a.device_ip_dict.keys():
            for ip in a.iperf_client_host_list(
                    device, conf.manager_ip_segment,
                    a.change_list_format(conf.test_cluster_host)):
                a.device_iperf_client_single_check(ip, conf.check_time + 5)
            a.network_device_receive_flow_check(device, conf.check_time)
            time.sleep(conf.check_time + 5)

        time.sleep(2)

        a.kill_iperf_server()
        if firewalld_state == 0:
            a.firewalld_service_start()
        a.test_file_delete()
