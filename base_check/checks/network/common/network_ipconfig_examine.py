import re
from base_check.common.shell import shell
from base_check.common import log as logging

LOG = logging.getLogger(__name__)


class NetworkIpconfigCheck():

    def ip_analysis(self, ip):
        target_ip = ip.split('.')
        ip_prefix = target_ip[0] + '.' + target_ip[1] + '.' + target_ip[2]
        post_ip = target_ip[3].split('/')[0]
        ip_netmask = '/' + target_ip[3].split('/')[1]
        return target_ip, ip_prefix, post_ip, ip_netmask

    def ip_config(self, target_network_device, ip):
        cmd_set_ip = "ip addr add %s dev %s" % (ip, target_network_device)
        result = shell(cmd_set_ip).stdout
        LOG.debug('ip addr add %s dev %s" \n%s'
                  % (ip, target_network_device, result))
        if result:
            LOG.info(result)

    def del_ip(self, target_network_device, ip):
        cmd_del_ip = "ip addr del %s dev %s" % (ip, target_network_device)
        result = shell(cmd_del_ip).stdout
        LOG.debug('ip addr del %s dev %s" \n%s'
                  % (ip, target_network_device, result))
        if result:
            LOG.info(result)

    def get_post_ip_and_netmask(self, network):
        ip_prefix = self.ip_analysis(network)[1]
        ip_netmask = self.ip_analysis(network)[3]
        cmd = "ip -o -4 a | grep '%s' | awk '{print $4}' " % ip_prefix
        ip = shell(cmd).stdout
        post_ip = self.ip_analysis(ip)[2]
        post_ip_and_netmask = post_ip + ip_netmask
        return post_ip_and_netmask

    def get_ip_prefix(self, ip):
        ip_prefix = self.ip_analysis(ip)[1]
        return ip_prefix

    def get_interface_list(self):
        cmd = " ip -o addr | awk '{print $2}' | uniq "
        interface_list = shell(cmd).stdout
        return interface_list

    def ip_check(self, ip):
        pattern = re.compile(r"^((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}"
                              r"(2[0-4]\d|25[0-5]|[01]?\d\d?)\/"
                              r"([12]?\d|3[0-2])$")
        if pattern.match(ip):
            return ip
        else:
            return None

    def device_get_ip(self, device):
        cmd = " ip -o -4 addr show %s | awk '{print $4}' " % device
        ip = shell(cmd).stdout
        if self.ip_check(ip):
            return ip
        else:
            return None
