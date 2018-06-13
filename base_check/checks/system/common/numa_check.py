# -*- coding: utf-8 -*-
from base_check.common.shell import shell
from base_check.common import log as logging

LOG = logging.getLogger(__name__)


class NumaCheck(object):

    def nvme_device_numa_check(self):
        cmd1 = "ls /sys/class/block|grep nvme &>/dev/null ;echo $?"
        cmd2 = "for i in /sys/class/block/nvme[0-9]n[0-9];" \
               "do cat $i/device/device/numa_node;done|grep 0|wc -l"
        cmd3 = "for i in /sys/class/block/nvme[0-9]n[0-9];" \
               "do cat $i/device/device/numa_node;done|grep 1|wc -l"
        is_exits = shell(cmd1).stdout
        numa_node0_num = shell(cmd2).stdout.strip()
        numa_node1_num = shell(cmd3).stdout.strip()
        if int(is_exits) == 0:
            if int(numa_node0_num) == int(numa_node1_num):
                LOG.debug('Nvme_numa_0:%s Nvme_numa_1:%s' %
                          (numa_node0_num, numa_node1_num))
            else:
                LOG.error('Nvme_numa_0:Error(%s) Nvme_numa_1:Error(%s)' %
                          (numa_node0_num, numa_node1_num))
        else:
            LOG.warn('Nvme:None')
