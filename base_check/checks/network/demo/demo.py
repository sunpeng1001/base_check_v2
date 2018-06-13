from base_check.common.utils import BaseCheck
from base_check.common import log as logging

LOG = logging.getLogger(__name__)


class Demo(BaseCheck):
    def check_foo(self, obj):
        LOG.debug('check_foo-----')
        LOG.debug(obj)

    def check_bar(self, obj):
        LOG.debug('check_bar-----')
        LOG.debug(obj)
