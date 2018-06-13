# -*- coding: utf-8 -*-
import time
from base_check.common.utils import BaseCheck
from base_check.common import log as logging
from base_check.checks.network.common.esxi_vswitch_check \
   import EsxiVswichCheck

LOG = logging.getLogger(__name__)
num = -1


class PhyDeviceSetOff(BaseCheck):

    def check_esxi_uplink_up(self, conf):
        global num
        num = num + 1
        a = EsxiVswichCheck()
        for vswich in conf.target_devices.keys():
            if len(conf.target_devices[vswich]) == 2:
                if set(conf.target_devices[vswich]) == \
                        a.vswitch_uplinks(vswich):
                    a.uplinks_up(conf.target_devices[vswich][num])
        time.sleep(3)
