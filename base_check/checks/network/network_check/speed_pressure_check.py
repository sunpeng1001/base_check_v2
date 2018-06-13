# -*- coding: utf-8 -*-
import threading
import time
from base_check.common.utils import BaseCheck
from base_check.checks.network.common.speed_pressure_check \
    import NetworkSpeedPressureExamine
from base_check.common import log as logging


LOG = logging.getLogger(__name__)


class NetworkSpeedPressureCheck(BaseCheck):

    def check_speed_pressure(self, conf):
        a = NetworkSpeedPressureExamine()
        firewalld_state = a.firewalld_service_stop()
        a.ensure_iperf_rpm_install()
        a.device_iperf_server_check()
        a.add_avaiable_device_and_ip_list(conf.target_devices)

        time.sleep(2)
        threads = []
        for iperf_server_ip in a.iperf_host_cluster(
                conf.manager_ip_segment,
                a.change_list_format(conf.test_cluster_host)):
            t = threading.Thread(target=a.device_iperf_clinet_check,
                                 args=(iperf_server_ip, conf.check_time + 10))
            threads.append(t)
            t.start()
            time.sleep(1)

        for t in threads:
            t.join()

        time.sleep(1)

        threads = []
        for device in a.local_device_list:
            t = threading.Thread(target=a.network_device_receive_flow_check,
                                 args=(device, conf.check_time))
            threads.append(t)
            t.start()
            time.sleep(1)

        for t in threads:
            t.join()

        time.sleep(2)

        a.kill_iperf_server()
        if firewalld_state == 0:
            a.firewalld_service_start()
        a.test_file_delete()
