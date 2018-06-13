# -*- coding: utf-8 -*-
from base_check.common.utils import BaseCheck
from base_check.common import log as logging
from base_check.checks.network.common.esxi_vswitch_check \
   import EsxiVswichCheck

LOG = logging.getLogger(__name__)


class EsxistandVswichCheck(BaseCheck):

    def check_esxi_vswich(self, conf):
        a = EsxiVswichCheck()
        for target_device in conf.target_devices.keys():
            if a.pre_check_vswitch(target_device):
                if a.vswitch_uplinks(target_device) == \
                        set(conf.target_devices[target_device]):
                    LOG.debug("%s:ok" % target_device)
                else:
                    for vmnic in a.vswitch_uplinks(target_device):
                        if vmnic in conf.target_devices[target_device]:
                            LOG.debug("%s:%s" % (target_device, vmnic))
                        else:
                            LOG.warn("%s:error(%s)" % (target_device, vmnic))
            else:
                LOG.warn("%s:error" % target_device)
