# -*- coding: utf-8 -*-
from base_check.common.utils import BaseCheck
from base_check.common import log as logging
from base_check.checks.network.common.bond_device_check import BondDeviceCheck

LOG = logging.getLogger(__name__)


class PhyDeviceSetOff(BaseCheck):

    def check_bond_device_conf(self, conf):
        a = BondDeviceCheck()
        for bond in conf.target_devices.keys():
            error_list = []
            if not a.pre_check(bond):
                LOG.warn("%s:Error" % bond)
                return
            if a.bond_mode_check(bond) != conf.bond_mode[bond]:
                error_list.append(a.bond_mode_check(bond))
            for dev in a.phy_device_state_check(bond).keys():
                if dev not in set(conf.target_devices[bond]):
                    error_list.append(dev)
                elif set(conf.target_devices[bond]) \
                        == a.phy_device_check(bond):
                    if a.phy_device_state_check(bond)[dev] != 'up':
                        LOG.warn('%s:%s:Error(%s)'
                                 % (bond, dev,
                                    a.phy_device_state_check(bond)[dev]))
                    elif int(a.phy_device_speed_check(dev)) \
                            != conf.phy_device_speed.get(dev):
                        LOG.warn("%s:%s:Error(%s)" %
                                 (bond, dev, a.phy_device_speed_check(dev)))
                    else:
                        LOG.debug("%s:%s:%s:%s" % (bond, dev,
                                  a.phy_device_state_check(bond)[dev],
                                  a.phy_device_speed_check(dev)))
                else:
                    error_list.append(dev)
            if error_list:
                LOG.error("%s:Error(%s)" % (bond, ':'.join(error_list)))
