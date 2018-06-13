# -*- coding: utf-8 -*-
from base_check.common.shell import shell
from base_check.common import log as logging

LOG = logging.getLogger(__name__)


class SystemPortExamine():

    def get_manger_ip_host(self, manager_ip_seg):
        cmd = "ip -o a|grep %s|awk NR==1|grep -w inet" \
              "|awk '{print $4}'" % manager_ip_seg
        manager_ip_host_init = shell(cmd).stdout
        if manager_ip_host_init:
            manager_ip_host = manager_ip_host_init.split(
                '/', 2)[0].split('.', 4)[3]
        else:
            manager_ip_host = 0
        return manager_ip_host

    def change_list_format(self, init_list):
        fin_list = []
        init_list = init_list.strip('[').strip(']').split(',')
        for i in init_list:
            if ':' not in i:
                fin_list.append(int(i))
            else:
                t = i.split(':')
                start = t[0]
                end = t[1]
                fin_list += range(int(start), int(end) + 1)
        return fin_list

    def conform_role_of_node(self, node_dict, target_node):

        if int(target_node) == 0:
            return 0
        node_role = 1
        for role in node_dict.keys():
            if int(target_node) in \
                    self.change_list_format(node_dict[role]):
                node_role = role
                break
        return node_role

    def tcp_port_check(self, conf_port):
        cmd = "ss -lantu4 | grep LISTEN | grep -w tcp | awk '{print $5}' " \
               "| awk -F ':' '{print $2}' | uniq | tr '\n' ' '"
        listen_tcp_port = map(int, shell(cmd).stdout.split())
        if set(conf_port) != set(listen_tcp_port):
            redundant_port = ':'.join(str(s) for s in set(listen_tcp_port).
                                      difference(set(conf_port)))
            absent_port = ':'.join(str(s) for s in set(conf_port).
                                   difference(set(listen_tcp_port)))
            if redundant_port and absent_port:
                LOG.error('TCP:++(%s) --(%s)' % (redundant_port, absent_port))
            elif not redundant_port:
                LOG.error('TCP:--(%s)' % absent_port)
            else:
                LOG.error('TCP:++(%s)' % redundant_port)
        else:
            LOG.debug('TCP:(%s)' % ':'.join(str(s) for s in listen_tcp_port))

    def upd_port_check(self, conf_port):
        cmd = "ss -lantu4 | grep udp | awk '{print $5}' | " \
               "awk -F ':' '{print $2}' | uniq|tr '\n' ' '"
        listen_udp_port = map(int, shell(cmd).stdout.split())
        if set(conf_port) != set(listen_udp_port):
            redundant_port = ':'.join(str(s) for s in set(
                listen_udp_port).difference(set(conf_port)))
            absent_port = ':'.join(str(s) for s in set(
                conf_port).difference(set(listen_udp_port)))
            if redundant_port and absent_port:
                LOG.error('UDP:++(%s) --(%s)' % (redundant_port, absent_port))
            elif not redundant_port:
                LOG.error('UDP:--(%s)' % absent_port)
            else:
                LOG.error('UDP:++(%s)' % redundant_port)
        else:
            LOG.debug('UDP:(%s)' % ':'.join(str(s) for s in listen_udp_port))
