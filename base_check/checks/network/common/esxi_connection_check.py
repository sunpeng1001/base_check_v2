# -*- coding: utf-8 -*-

import os
from base_check.common.shell import shell
from base_check.common import log as logging

LOG = logging.getLogger(__name__)


class NetworkConnectionCheck():

    def network_device_check(self, target_devices):
        cmd = "esxcli network ip interface list " \
              "|grep '^   Name:' |awk '{print $2}'"
        vmknic_list = shell(cmd).stdout
        network_device_list = vmknic_list.split("\n")
        return set(target_devices).issubset(set(network_device_list))

    def pre_ping_check(self, device, targete_getway):
        cmd = "ping -I %s -i 0.01 -W 2 %s >/dev/null" \
               % (device, targete_getway)
        shell(cmd)

    def ping_check(self, device, targete_getway, ping_test_duration):
        cmd = "ping -I %s -i 0.01 -W 2 -c %s %s >/tmp/%s.pingtxt&" \
               % (device, ping_test_duration, targete_getway, device)
        shell(cmd)

    def _check_ping_result(self, target_devices):
        for device in target_devices:
            cmd1 = "cat /tmp/%s.pingtxt |grep transmitted|" \
                   "awk '{print $1}'" % device
            cmd2 = "cat /tmp/%s.pingtxt |grep transmitted|" \
                   "awk '{print $4}'" % device

            transmitted_packets = shell(cmd1).stdout
            received_packets = shell(cmd2).stdout
            loss_num = int(transmitted_packets) - int(received_packets)
            loss_percent = (float(loss_num) / float(transmitted_packets))
            if int(transmitted_packets) \
                   == int(received_packets) or loss_percent < 0.0005:
                LOG.debug('%s:OK(%d)' % (device, loss_num))
            elif int(received_packets) == 0:
                LOG.error('%s:Unreachable' % device)
            else:
                LOG.error('%s:Error(%d/%d/%f)'
                          % (device, int(transmitted_packets),
                             loss_num, loss_percent))

    def test_file_delete(self, target_devices):
        for device in target_devices:
            test_file = '/tmp' + '/' + device + '.pingtxt'
            os.remove(test_file)
