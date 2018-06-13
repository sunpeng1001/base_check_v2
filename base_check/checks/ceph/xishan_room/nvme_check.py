# -*- coding:utf-8 -*-
from base_check.common.shell import shell
from base_check.common.utils import BaseCheck
from base_check.common import log as logging
from base_check.checks.ceph.common.nvme_check import NVMeExamine

LOG = logging.getLogger(__name__)


class NVMeCheck(BaseCheck):

    def check_nvme(self, conf):
        nvme = NVMeExamine()

        if nvme.get_nvme_number() != conf.nvme_info['count']:
            LOG.error("nvme number: ERROR")
            return
        nvme.check_nvme_size(conf.nvme_info['count'],
                             conf.nvme_info['size'])
        nvme.check_nvme_version(conf.nvme_info['count'],
                                conf.nvme_info['version'])
        cmd = "lscpu | grep 'NUMA node(s)' | awk -F: '{print $2}' | " \
              "sed 's/^[ \t]*//g'"
        numa = int(shell(cmd).stdout)
        if numa > 1:
            nvme.get_nvme_numa_node(numa)
            nvme.get_nvme_interrupt()
        nvme.get_nvme_life()
