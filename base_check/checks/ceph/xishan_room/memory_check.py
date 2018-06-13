# -*- coding:utf-8 -*-
from base_check.common.utils import BaseCheck
from base_check.common import log as logging
from base_check.checks.ceph.common.memory_check import MemoryExamine

LOG = logging.getLogger(__name__)


class MemoryCheck(BaseCheck):

    def check_memory(self, conf):
        memory = MemoryExamine()

        if memory.get_memory_number() != conf.memory_info['count']:
            LOG.error("memory number: ERROR")
            return
        memory.check_memory_slot(conf.memory_info['slot'])
        memory.check_memory_channel(conf.memory_info['channel'])
        memory.check_memory_size(conf.memory_info['count'],
                                 conf.memory_info['size'])
        memory.check_memory_speed(conf.memory_info['count'],
                                  conf.memory_info['speed'])
        memory.check_memory_vendor(conf.memory_info['count'],
                                   conf.memory_info['vendor'])
        memory.check_memory_version(conf.memory_info['count'],
                                    conf.memory_info['version'])
        memory.is_numa_balance()
