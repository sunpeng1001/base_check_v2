# -*- coding: utf-8 -*-
from base_check.common.utils import BaseCheck
from base_check.common import log as logging
from base_check.checks.system.common.system_port_post_check \
    import SystemPortExamine

LOG = logging.getLogger(__name__)


class SystemPortCheck(BaseCheck):

    def check_system_port(self, conf):
        a = SystemPortExamine()
        node_role = a.conform_role_of_node(
            conf.nodes, a.get_manger_ip_host(conf.manager_ip))
        if node_role == 0:
            LOG.error('Manager_ip Error')
        elif node_role == 1:
            LOG.error('Host Error')
        else:
            a.tcp_port_check(conf[node_role]['tcp'])
            a.upd_port_check(conf[node_role]['udp'])
