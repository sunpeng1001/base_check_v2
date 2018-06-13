from base_check.common.utils import BaseCheck
from base_check.common import log as logging
from base_check.common.shell import shell

LOG = logging.getLogger(__name__)


class Demo(BaseCheck):
    def check_foo(self, obj):
        cmd = "ip address show eth1 | grep inet | grep eth1 | " \
              "awk '{print $2}' | cut -d'/' -f1"
        ip = shell(cmd).stdout
        LOG.debug('check_foo -------------')
        LOG.debug(ip)
        LOG.debug(obj)
        LOG.debug(obj.aa)

    def check_bar(self, obj):
        LOG.debug('check_bar -------------')
        LOG.debug(obj)
        LOG.debug(obj['macs'])
        LOG.debug(obj.macs)
        LOG.debug(obj.macs.aa.eth0)

    def check_baz(self, obj):
        LOG.debug('check_baz -------------')
        LOG.debug(obj)
