from base_check.common.utils import BaseCheck
from base_check.common import log as logging
from base_check.checks.network.common.network_ipconfig_examine \
    import NetworkIpconfigCheck

LOG = logging.getLogger(__name__)


class NetworkDelIp(BaseCheck):

    def check_del_ip(self, conf):
        mgmt_device = conf.mgmt_device
        target_device = conf.target_device
        instance = NetworkIpconfigCheck()
        mgmt_network = instance.device_get_ip(mgmt_device)
        post_ip_and_netmask = instance.get_post_ip_and_netmask(mgmt_network)
        for device, ip_network in target_device.items():
            interface_list = instance.get_interface_list()
            if device in interface_list:
                ip_prefix = instance.get_ip_prefix(ip_network)
                ip = ip_prefix + '.' + post_ip_and_netmask
                result = instance.del_ip(device, ip)
                LOG.debug(result)
            else:
                LOG.info("%s error" % device)
