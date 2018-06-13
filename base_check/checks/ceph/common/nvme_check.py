# -*- coding:utf-8 -*-
import re

from base_check.common.shell import shell
from base_check.common import log as logging

LOG = logging.getLogger(__name__)


class NVMeExamine():

    def __init__(self):
        if not self.pre_check():
            cmd = "yum install nvme-cli -y"
            is_installed = shell(cmd).returncode
            if is_installed == 0:
                LOG.debug("installed 'nvme-cli' successfully!")
            else:
                LOG.error("Can not install 'nvme-cli'!")

    def pre_check(self):
        cmd = "which nvme"
        is_exist = shell(cmd).returncode
        if is_exist == 0:
            return True
        else:
            return False

    def get_nvme_number(self):
        cmd = "nvme list | grep nvme | awk '{print $1}' | " \
              "awk -F/ '{print $3}' | wc -l"
        return int(shell(cmd).stdout)

    def get_nvme_name(self):
        cmd = "nvme list | grep nvme | awk '{print $1}' |awk -F/ '{print $3}'"
        return shell(cmd).stdout.split('\n')

    def get_nvme_numa_nodes(self):
        cmd = "ls /sys/class/nvme/ | sort"
        return shell(cmd).stdout.split('\n')

    def compare_info(self, count, detect_infos, info, attribute):
        detect_names = self.get_nvme_name()
        str_info = re.compile('\s+')
        info = str_info.sub('', info)
        for index in xrange(count):
            detect_info = str_info.sub('', detect_infos[index])
            if detect_info.lower() != info.lower():
                LOG.error("nvme %s %s: ERROR"
                          % (detect_names[index], attribute))
            else:
                LOG.debug("nvme %s %s: OK"
                          % (detect_names[index], attribute))

    def get_nvme_size(self):
        cmd = "nvme list | grep nvme | awk '{print $9 $10}'"
        return shell(cmd).stdout.split('\n')

    def check_nvme_size(self, count, size):
        detect_sizes = self.get_nvme_size()
        self.compare_info(count, detect_sizes, size, 'size')

    def get_nvme_version(self):
        cmd = " nvme list | grep nvme | awk '{print $3}'"
        return shell(cmd).stdout.split('\n')

    def check_nvme_version(self, count, version):
        detect_versions = self.get_nvme_version()
        self.compare_info(count, detect_versions, version, 'version')

    def get_nvme_life(self):
        for nvme in self.get_nvme_name():
            cmd = "nvme smart-log /dev/%s | grep percentage_used | " \
                  "awk '{print $3}'" % nvme
            life = shell(cmd).stdout
            LOG.debug("nvme %s life used %s" % (nvme, life))

    def get_nvme_numa_node(self, numa_count):
        numa_nodes = list()
        for index in xrange(numa_count):
            numa_nodes.append(0)
        for nvme in self.get_nvme_numa_nodes():
            cmd = "cat /sys/class/nvme/%s/device/numa_node | " \
                  "awk '{print $1}'" % nvme
            numa_node = int(shell(cmd).stdout)
            numa_nodes[numa_node] = numa_nodes[numa_node] + 1
        numa_nodes.sort()
        if numa_nodes[0] == numa_nodes[-1] and numa_nodes[0] != 0:
            LOG.debug("nvme ssd is located on different numa nodes")
        else:
            LOG.error("nvme ssd is located on the same numa node")

    def get_nvme_interrupt(self):
        for nvme in self.get_nvme_numa_nodes():
            cmd1 = "cat /proc/interrupts | grep %s | awk -F: " \
                   "'NR==1 {print $1}' | sed 's/^[ \t]*//g'" % nvme
            irq = shell(cmd1).stdout
            cmd2 = "cat /proc/irq/%s/node" % irq
            interrupt = int(shell(cmd2).stdout)
            cmd = "cat /sys/class/nvme/%s/device/numa_node | " \
                  "awk '{print $1}'" % nvme
            numa_node = int(shell(cmd).stdout)
            if interrupt == numa_node:
                LOG.debug("The interrupt of nvme ssd %s is binding on "
                          "the same numa node" % nvme)
            else:
                LOG.error("The interrupt of nvme ssd %s is binding on "
                          "different numa nodes" % nvme)
