# -*- coding: utf-8 -*-
from base_check.common.shell import shell
from base_check.common import log as logging

LOG = logging.getLogger(__name__)


class SystemExamine():

    def tcp_and_udp_port_check(self):
        tcp_conf_port = [22]
        udp_conf_port = []
        cmd1 = "ss -lantu4 | grep LISTEN | grep -w tcp | " \
               "awk '{print $5}' | awk -F ':' '{print $2}' | uniq | wc -l"
        cmd2 = "ss -lantu4 | grep LISTEN | grep -w tcp | awk '{print $5}' " \
               "| awk -F ':' '{print $2}' | uniq | tr '\n' ' '"
        cmd3 = "ss -lantu4|grep udp|awk '{print $5}' | " \
               "awk -F ':' '{print $2}'|uniq|wc -l"
        cmd4 = "ss -lantu4 | grep udp | awk '{print $5}' | " \
               "awk -F ':' '{print $2}' | uniq|tr '\n' ' '"
        listen_tcp_port_num = shell(cmd1).stdout
        listen_tcp_port = map(int, shell(cmd2).stdout.split())
        listen_udp_port_num = shell(cmd3).stdout
        listen_udp_port = map(int, shell(cmd4).stdout.split())
        redundant_tcp_port = ' '.join(str(s) for s in set(listen_tcp_port).
                                      difference(set(tcp_conf_port)))
        redundant_udp_port = ' '.join(str(s) for s in set(listen_udp_port).
                                  difference(set(udp_conf_port)))
        LOG.debug('TCP_Port_Num:%d TCP_Port:%s UDP_Port_Num:%d UDP_Port:%s'
                  % (int(listen_tcp_port_num), listen_tcp_port,
                     int(listen_udp_port_num), listen_udp_port))
        if set(listen_tcp_port) != set(tcp_conf_port):
            LOG.warn('TCP:%s' % redundant_tcp_port)
        if set(listen_udp_port) != set(udp_conf_port):
            LOG.warn('UDP:%s' % redundant_udp_port)
