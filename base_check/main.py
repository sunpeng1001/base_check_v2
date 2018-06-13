import os
import sys
try:
    from base_check.common import utils
except ImportError:
    filename = os.path.abspath(__file__)
    _index = filename.rfind('/base_check/')
    dirname = filename[:_index] if _index > 0 \
        else os.path.dirname(filename)
    sys.path.insert(0, dirname)
    from base_check.common import utils

from base_check.common import log as logging
from base_check.common.cfg import CONF


# import the module to check
check_modules = [
    # 'base_check.checks.network.network_check.device_set_ip',
    # 'base_check.checks.network.network_check.network_base_check',
    # 'base_check.checks.network.network_check.bond_device_check',
    # 'base_check.checks.network.network_check.phy_device_set_off',
    # 'base_check.checks.network.network_check.connection_check',
    # 'base_check.checks.network.network_check.phy_device_set_up',
    # 'base_check.checks.network.network_check.phy_device_set_off',
    # 'base_check.checks.network.network_check.connection_check',
    # 'base_check.checks.network.network_check.phy_device_set_up',
    # 'base_check.checks.network.network_check.mac_check',
    # 'base_check.checks.network.network_check.speed_pressure_check',
    # 'base_check.checks.network.network_check.singlethread_speed_pressure_check',
    # 'base_check.checks.network.network_check.device_del_ip',
    # 'base_check.checks.system.system_check.system_port_check',
    # 'base_check.checks.system.system_check.numa_check',
     'base_check.checks.system.system_check.system_port_post_check',
    # 'base_check.checks.system.system_check.system_base_check',
    # ###########------esxi_base_network_status_test--------################
    # 'base_check.checks.network.esxi_network.esxi_network_base_check',
    # 'base_check.checks.network.esxi_network.esxi_vswitch_check'
    # 'base_check.checks.network.esxi_network.esxi_uplink_down',
    # 'base_check.checks.network.esxi_network.esxi_connection_check',
    # 'base_check.checks.network.esxi_network.esxi_uplink_up',
    # 'base_check.checks.network.esxi_network.esxi_uplink_down',
    # 'base_check.checks.network.esxi_network.esxi_connection_check',
    # 'base_check.checks.network.esxi_network.esxi_uplink_up',
]


def main():
    CONF()
    logging.setup(CONF)
    LOG = logging.getLogger(__name__)

    utils.import_module_list(check_modules)
    utils.run_all_checks(check_modules)
    if utils.check_all_passed():
        return 0
    else:
        for info in utils.get_all_fails():
            LOG.error(info)
        return 1


if __name__ == '__main__':
    sys.exit(main())
