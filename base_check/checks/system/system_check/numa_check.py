# -*- coding: utf-8 -*-
from base_check.common.utils import BaseCheck
from base_check.common import log as logging
from base_check.checks.system.common.numa_check import NumaCheck

LOG = logging.getLogger(__name__)


class DeviceNumaCheck(BaseCheck):

    def check_device_numa(self):
        a = NumaCheck()
        a.nvme_device_numa_check()
