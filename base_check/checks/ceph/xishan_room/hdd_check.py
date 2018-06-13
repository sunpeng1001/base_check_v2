# -*- coding:utf-8 -*-
from base_check.common.utils import BaseCheck
from base_check.common import log as logging
from base_check.checks.ceph.common.hdd_check import HDDExamine

LOG = logging.getLogger(__name__)


class HDDCheck(BaseCheck):

    def check_hdd(self, conf):
        hdd = HDDExamine()

        if hdd.get_hdd_number() != len(conf.names):
            LOG.error("hdd number: ERROR")
            return
        hdd.check_hdd_name(conf.names)
        for index in xrange(len(conf.names)):
            hdd.check_hdd_size(conf.names[index], conf.sizes[index])
            hdd.check_hdd_vendor(conf.names[index], conf.vendors[index])
            hdd.check_hdd_version(conf.names[index], conf.versions[index])
