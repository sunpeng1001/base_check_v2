# -*- coding: utf-8 -*-

from base_check.common.utils import BaseCheck
from base_check.common import log as logging
from base_check.checks.system.common.system_port_check import SystemExamine

LOG = logging.getLogger(__name__)


class SystemPortCheck(BaseCheck):

    def check_system_pre_port(self):
        a = SystemExamine()
        a.tcp_and_udp_port_check()
