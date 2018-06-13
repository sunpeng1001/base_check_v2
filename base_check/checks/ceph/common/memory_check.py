# -*- coding:utf-8 -*-
import os
import re

from base_check.common.shell import shell
from base_check.common import log as logging

LOG = logging.getLogger(__name__)


class MemoryExamine():

    def __init__(self):
        if not os.path.isfile('lshw.tmp.txt'):
            if not self.pre_check():
                cmd1 = "yum install lshw -y"
                is_installed = shell(cmd1).returncode
                if is_installed == 0:
                    LOG.debug("installed 'lshw' successfully!")
                    cmd2 = "lshw > lshw.tmp.txt"
                    shell(cmd2)
                else:
                    LOG.error("Can not install 'lshw'!")
            else:
                cmd3 = "lshw > lshw.tmp.txt"
                shell(cmd3)

    def pre_check(self):
        cmd = "which lshw"
        is_exist = shell(cmd).returncode
        if is_exist == 0:
            return True
        else:
            return False

    def get_memory_number(self):
        cmd = "dmidecode -t 17 | grep Size | grep -v No | wc -l"
        return int(shell(cmd).stdout)

    def get_memory_slot(self):
        cmd = "dmidecode -t 17 | grep -A3 Size | " \
              "grep -v 'No Module Installed' | grep -E 'Size|Locator' | " \
              "sed -n '/Size:/,+1p' | grep Locator | awk '{print $2}'"
        return shell(cmd).stdout.split('\n')

    def check_memory_slot(self, slots):
        detect_memory_slots = self.get_memory_slot()
        str_info = re.compile('\s+')
        for index in xrange(len(detect_memory_slots)):
            detect_memory_slots[index] = \
                str_info.sub('', detect_memory_slots[index]).lower()

        for slot in slots:
            if slot.lower() in detect_memory_slots:
                LOG.debug("memory slot %s: OK" % slot)
            else:
                LOG.error("memory slot %s: ERROR" % slot)

    def get_memory_channel(self):
        cmd = "dmidecode -t 17 | grep -A4 Size | " \
              "grep -v 'No Module Installed' | grep -E 'Size|Bank' | " \
              "sed -n '/Size:/,+1p' | grep 'Bank Locator' | " \
              "awk -F: '{print $2}' | sed 's/^[ \t]*//g'"
        return shell(cmd).stdout.split('\n')

    def check_memory_channel(self, channels):
        detect_memory_channels = self.get_memory_channel()
        str_info = re.compile('\s+')
        for index in xrange(len(detect_memory_channels)):
            detect_memory_channels[index] = \
                str_info.sub('', detect_memory_channels[index]).lower()
        for channel in channels:
            if channel.lower() in detect_memory_channels:
                LOG.debug("memory channel %s: OK" % channel)
            else:
                LOG.error("memory channel %s: ERROR" % channel)

    def compare_info(self, count, detect_infos, info, attribute):
        detect_memory_slots = self.get_memory_slot()
        str_info = re.compile('\s+')
        info = str_info.sub('', info)
        for index in xrange(count):
            detect_info = str_info.sub('', detect_infos[index])
            if detect_info.lower() != info.lower():
                LOG.error("memory slot %s %s: ERROR"
                          % (detect_memory_slots[index], attribute))
            else:
                LOG.debug("memory slot %s %s: OK"
                          % (detect_memory_slots[index], attribute))

    def get_memory_size(self):
        cmd = "dmidecode -t 17 | grep Size | " \
              "grep -v 'No Module Installed' | " \
              "awk -F: '{print $2}' | sed 's/[ \t]*//g'"
        return shell(cmd).stdout.split('\n')

    def check_memory_size(self, count, size):
        detect_memory_sizes = self.get_memory_size()
        self.compare_info(count, detect_memory_sizes, size, 'size')

    def get_memory_speed(self):
        cmd = "dmidecode -t 17 | grep Speed | grep -v -E 'Unknown|Clock' | " \
              "awk -F: '{print $2}' | sed 's/[ \t]*//g'"
        return shell(cmd).stdout.split('\n')

    def check_memory_speed(self, count, speed):
        detect_memory_speeds = self.get_memory_speed()
        self.compare_info(count, detect_memory_speeds, speed, 'speed')

    def get_memory_vendor(self):
        if not os.path.isfile('lshw.tmp.txt'):
            return None
        vendors = list()
        for slot in self.get_memory_slot():
            cmd = "cat lshw.tmp.txt | grep -B4 %s | grep vendor | " \
                  "awk '{print $2}'" % slot
            vendor = shell(cmd).stdout
            vendors.append(vendor)
        return vendors

    def check_memory_vendor(self, count, vendor):
        detect_memory_vendors = self.get_memory_vendor()
        self.compare_info(count, detect_memory_vendors, vendor, 'vendor')

    def get_memory_version(self):
        if not os.path.isfile('lshw.tmp.txt'):
            return None
        versions = list()
        for slot in self.get_memory_slot():
            cmd = "cat lshw.tmp.txt | grep -B4 %s | grep product | " \
                  "awk '{print $2}'" % slot
            version = shell(cmd).stdout
            versions.append(version)
        return versions

    def check_memory_version(self, count, version):
        detect_memory_versions = self.get_memory_version()
        self.compare_info(count, detect_memory_versions, version, 'version')

    def is_numa_balance(self):
        # numa node number
        cmd1 = "lscpu | grep 'NUMA node(s)' | awk -F: '{print $2}' | " \
               "sed 's/[ \t]*//g'"
        num_of_numa = int(shell(cmd1).stdout)
        # memmory channel number of each numa node
        cmd2 = "dmidecode -t 17 | grep -A4 Size | " \
               "grep -v 'No Module Installed' | grep -E 'Size|Bank' | " \
               "sed -n '/Size:/,+1p' | grep 'Bank Locator' | " \
               "awk -F_ '{print $3}' | sort -u | wc -l"
        num_of_channel = int(shell(cmd2).stdout)
        # memory number of each channel
        num_of_mems = list()
        for node in xrange(num_of_numa):
            for channel in xrange(num_of_channel):
                num_of_mem_sh = "dmidecode -t 17 | grep -A4 Size | " \
                                "grep -v 'No Module Installed' | " \
                                "grep -E 'Size|Bank' | sed -n '/Size:/,+1p'" \
                                " | grep 'Bank Locator' | awk -F_ " \
                                """ '$2=="Node%d" && $3=="Channel%d" """ \
                                "{print $2 $3 $4}' | wc -l" % (node, channel)
                num_of_mem = int(shell(num_of_mem_sh).stdout)
                num_of_mems.append(num_of_mem)
        num_of_mems.sort()
        if num_of_mems[0] == num_of_mems[-1]:
            LOG.debug("memory numa balance: OK")
        else:
            LOG.error("memory numa balance: ERROR")
