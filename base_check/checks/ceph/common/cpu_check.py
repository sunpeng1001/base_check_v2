# -*- coding:utf-8 -*-
import os
import re

from base_check.common.shell import shell
from base_check.common import log as logging

LOG = logging.getLogger(__name__)


class CPUExamine():

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

    def get_cpu_numbers(self):
        if not os.path.isfile('lshw.tmp.txt'):
            return -1
        cmd = "cat lshw.tmp.txt | grep -A9 'description: CPU' | " \
              "grep slot | wc -l"
        return int(shell(cmd).stdout)

    def get_cpu_ids(self):
        cmd = "cat lshw.tmp.txt | grep -A9 'description: CPU' | " \
               "grep slot | awk -F: '{print $2}' | sed 's/^[ \t]*//g'"
        return shell(cmd).stdout.split('\n')

    def get_cpu_version(self):
        cmd = "cat lshw.tmp.txt | grep -A9 'description: CPU' | " \
              "grep version | awk -F: '{print $2}' | sed 's/^[ \t]*//g'"
        return shell(cmd).stdout.split('\n')

    def check_cpu_version(self, cpu_count, cpu_version):
        detect_cpu_versions = self.get_cpu_version()
        ids = self.get_cpu_ids()
        str_info = re.compile('\s+')
        cpu_version = str_info.sub('', cpu_version)
        for index in xrange(cpu_count):
            detect_cpu_version = str_info.sub('', detect_cpu_versions[index])
            if detect_cpu_version.lower() != cpu_version.lower():
                LOG.error("CPU %s version: ERROR" % ids[index])
            else:
                LOG.debug("CPU %s version: OK" % ids[index])

    def get_cpu_speed(self):
        cmd = "cat lshw.tmp.txt | grep -A9 'description: CPU' | " \
              "grep size | awk -F: '{print $2}' | sed 's/^[ \t]*//g'"
        return shell(cmd).stdout.split('\n')

    def check_cpu_speed(self, cpu_count, cpu_speed):
        detect_cpu_speeds = self.get_cpu_speed()
        ids = self.get_cpu_ids()
        str_info = re.compile('\s+')
        cpu_speed = str_info.sub('', cpu_speed)
        for index in xrange(cpu_count):
            detect_cpu_speed = str_info.sub('', detect_cpu_speeds[index])
            if detect_cpu_speed.lower() != cpu_speed.lower():
                LOG.error("CPU %s speed: ERROR" % ids[index])
            else:
                LOG.debug("CPU %s speed: OK" % ids[index])

    def get_cpu_max_speed(self):
        cmd = "cat lshw.tmp.txt | grep -A9 'description: CPU' | " \
              "grep capacity | awk -F: '{print $2}' | sed 's/^[ \t]*//g'"
        return shell(cmd).stdout.split('\n')

    def check_cpu_max_speed(self, cpu_count, cpu_max_speed):
        detect_cpu_max_speeds = self.get_cpu_max_speed()
        ids = self.get_cpu_ids()
        str_info = re.compile('\s+')
        cpu_max_speed = str_info.sub('', cpu_max_speed)
        for index in xrange(cpu_count):
            detect_cpu_max_speed = str_info.sub('', detect_cpu_max_speeds[index])
            if detect_cpu_max_speed.lower() != cpu_max_speed.lower():
                LOG.error("CPU %s max speed: ERROR" % ids[index])
            else:
                LOG.debug("CPU %s max speed: OK" % ids[index])
