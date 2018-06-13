# -*- coding: utf-8 -*-
import threading
import time
from base_check.common.utils import BaseCheck
from base_check.common.shell import shell
from base_check.common import log as logging
from base_check.checks.network.common.esxi_connection_check \
     import NetworkConnectionCheck

LOG = logging.getLogger(__name__)


class ConnectionCheck(BaseCheck):

    def check_connection(self, conf):
        a = NetworkConnectionCheck()
        ping_test_duration = conf.ping_test_duration
        test_device_count = len(conf.target_devices.keys())
        if a.network_device_check(conf.target_devices.keys()):
            threads = []
            for device in conf.target_devices.keys():
                target_getway = conf.target_devices[device]['gateway']
                t = threading.Thread(target=a.pre_ping_check,
                                     args=(device, target_getway))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

            threads = []
            for device in conf.target_devices.keys():
                target_getway = conf.target_devices[device]['gateway']
                t = threading.Thread(target=a.ping_check,
                    args=(device, target_getway, ping_test_duration))
                threads.append(t)
                t.start()
                time.sleep(1)

            for t in threads:
                t.join()

            cmd = "grep transmitted /tmp/*pingtxt|wc -l"
            result_num = shell(cmd).stdout
            second = 0
            while int(result_num) != int(test_device_count):
                result_num = shell(cmd).stdout
                time.sleep(1)
                second = second + 1
                if second == conf.ping_test_timeout:
                    print("Timeout!")
                    break
            else:
                a._check_ping_result(conf.target_devices.keys())
            a.test_file_delete(conf.target_devices.keys())
        else:
            LOG.warn('Device:Error')
