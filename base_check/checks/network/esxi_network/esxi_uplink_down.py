# -*- coding: utf-8 -*-
import time
from base_check.common.utils import BaseCheck
from base_check.common import log as logging
from base_check.checks.network.common.esxi_vswitch_check \
   import EsxiVswichCheck

LOG = logging.getLogger(__name__)
num = -1


class EsxiUplinkDown(BaseCheck):

    def check_esxi_uplink_down(self, conf):
        global num
        num = num + 1
        a = EsxiVswichCheck()
        for vswich in conf.target_devices.keys():
            if len(conf.target_devices[vswich]) == 2:
                if set(conf.target_devices[vswich]) == \
                        a.vswitch_uplinks(vswich):
                    nic0 = a.vmnic_status(conf.target_devices[vswich][0])
                    nic1 = a.vmnic_status(conf.target_devices[vswich][1])
                    if nic0 == "up" and nic1 == "up":
                        a.uplinks_down(conf.target_devices[vswich][num])
                    else:
                        LOG.warn('%s:vmnic down!' % vswich)
                else:
                    LOG.warn('%s:uplinks error!' % vswich)
        time.sleep(3)
