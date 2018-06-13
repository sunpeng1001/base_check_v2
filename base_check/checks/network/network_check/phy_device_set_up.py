# -*- coding: utf-8 -*-
import time
from base_check.common.utils import BaseCheck
from base_check.common import log as logging
from base_check.checks.network.common.bond_device_on_off_check \
    import BondDeviceOnOffCheck

LOG = logging.getLogger(__name__)
num = -1


class PhyDeviceSetOff(BaseCheck):

    def check_set_phy_dev_down(self, conf):
        global num
        num = num + 1
        a = BondDeviceOnOffCheck()
        for i in conf.target_devices.keys():
            if len(conf.target_devices[i]) == 2:
                if set(conf.target_devices[i]) == a.phy_device_check(i):
                        a.set_phy_device_up(conf.target_devices[i][num])
        time.sleep(5)
