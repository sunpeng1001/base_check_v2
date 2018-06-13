# -*- coding: utf-8 -*-
import os
from base_check.common.shell import shell
from base_check.common import log as logging

LOG = logging.getLogger(__name__)


class NetworkConnectionCheck():
    def network_device_check(self, target_devices):
        network_device_list = os.listdir('/sys/class/net/')
        return set(target_devices).issubset(set(network_device_list))

    def pre_ping_check(self, device, targete_getway):
        cmd = "arping -I %s %s -c 3 -b -f >/dev/null" \
              % (device, targete_getway)
        shell(cmd)
        cmd1 = "ping -I %s %s -i 0.1 -w 2 >/dev/null" \
               % (device, targete_getway)
        shell(cmd1)

    def ping_check(self, device, targete_getway, ping_test_duration):
        cmd = "ping -I %s %s -i 0.1 -w %s >/tmp/%s.txt&" \
              % (device, targete_getway, ping_test_duration, device)
        shell(cmd)

    def _check_result(self, target_devices):
        for device in target_devices:
            cmd1 = "cat /tmp/%s.txt |grep transmitted|" \
                   "awk '{print $1}'" % device
            cmd2 = "cat /tmp/%s.txt |grep transmitted|" \
                   "awk '{print $4}'" % device
            transmitted_packets = shell(cmd1).stdout
            received_packets = shell(cmd2).stdout
            loss_num = int(transmitted_packets) - int(received_packets)
            loss_percent = (float(loss_num) / float(transmitted_packets))
            if int(transmitted_packets) \
                    == int(received_packets) or loss_percent < 0.005:
                LOG.debug('%s:OK(%d)' % (device, loss_num))
            elif int(received_packets) == 0:
                LOG.error('%s:Unreachable' % device)
            else:
                LOG.error('%s:Error(%d/%d/%f)'
                          % (device, int(transmitted_packets),
                             loss_num, loss_percent))

    def test_file_delete(self, target_devices):
        for device in target_devices:
            test_file = '/tmp' + '/' + device + '.txt'
            os.remove(test_file)
