# -*- coding:utf-8 -*-
from base_check.common.utils import BaseCheck
from base_check.common import log as logging
from base_check.checks.ceph.common.cpu_check import CPUExamine

LOG = logging.getLogger(__name__)


class CPUCheck(BaseCheck):

    def check_cpu(self, conf):
        cpu = CPUExamine()

        if cpu.get_cpu_numbers() != conf.cpu_info['count']:
            LOG.error("CPU count: ERROR")
            return

        cpu.check_cpu_version(conf.cpu_info['count'], conf.cpu_info['version'])
        cpu.check_cpu_speed(conf.cpu_info['count'], conf.cpu_info['speed'])
        cpu.check_cpu_max_speed(conf.cpu_info['count'], conf.cpu_info['max_speed'])
