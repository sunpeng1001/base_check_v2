# -*- coding: utf-8 -*-
from base_check.common.utils import BaseCheck
from base_check.common import log as logging
from base_check.checks.system.common.system_base_check \
    import SystemBaseCheckFunc

LOG = logging.getLogger(__name__)


class SystemBaseCheck(BaseCheck):

    def check_system_base_element(self, conf):
        a = SystemBaseCheckFunc()
        a.kernel_release_check(conf.kernel_release_conf)
        a.os_release_check(conf.os_release_conf)
        # 循环获取服务名称,调用系统服务检查的参数依次是服务名称、服务软件名称、服务状态
        for service in conf.os_service_state.keys():

            a.os_service_check(service,
                               conf.os_service_state[service]['software'],
                               conf.os_service_state[service]['state'])
        a.os_disk_partition()
        a.os_disk_raid_check()
        if conf.packages_list_conf:
            for package in conf.packages_list_conf:
                a.package_check(package)
        else:
            LOG.error('conf:Error')
