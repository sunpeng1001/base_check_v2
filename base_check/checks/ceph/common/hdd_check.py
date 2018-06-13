# -*- coding:utf-8 -*-
import os
from base_check.common.shell import shell
from base_check.common import log as logging

LOG = logging.getLogger(__name__)


class HDDExamine():

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

    def get_hdd_number(self):
        cmd = "lsblk | grep disk | grep sd | awk '{print $1}' | wc -l"
        return int(shell(cmd).stdout)

    def get_hdd_name(self):
        cmd = "lsblk | grep disk | grep sd | awk '{print $1}'"
        return shell(cmd).stdout.split('\n')

    def check_hdd_name(self, names):
        detect_hdd_names = self.get_hdd_name()
        for index in xrange(len(names)):
            if detect_hdd_names[index] != names[index]:
                LOG.error("hdd %s: ERROR" % names[index])
            else:
                LOG.debug("hdd %s: OK" % names[index])

    def check_hdd_size(self, device, size):
        if not os.path.isfile('lshw.tmp.txt'):
            LOG.error("lshw.tmp.txt doesn't exist!")
            return
        cmd = "cat lshw.tmp.txt | grep -A3 '/dev/%s$' | grep 'size:' | " \
              "awk -F: '{print $2}' | sed 's/^[ \t]*//g'" % device
        detect_size = shell(cmd).stdout
        if detect_size != size:
            LOG.error("hdd %s size: ERROR" % device)
        else:
            LOG.debug("hdd %s size: OK" % device)

    def check_hdd_vendor(self, device, vendor):
        if not os.path.isfile('lshw.tmp.txt'):
            LOG.error("lshw.tmp.txt doesn't exist!")
            return
        cmd = "cat lshw.tmp.txt | grep -B4 '/dev/%s$' | grep vendor | " \
              "awk -F: '{print $2}' | sed 's/^[ \t]*//g'" % device
        detect_vendor = shell(cmd).stdout
        if detect_vendor != vendor:
            LOG.error("hdd %s vendor: ERROR" % device)
        else:
            LOG.debug("hdd %s vendor: OK" % device)

    def check_hdd_version(self, device, version):
        if not os.path.isfile('lshw.tmp.txt'):
            LOG.error("lshw.tmp.txt doesn't exist!")
            return
        cmd = "cat lshw.tmp.txt | grep -B4 '/dev/%s$' | grep product | " \
              "awk -F: '{print $2}' | sed 's/^[ \t]*//g'" % device
        detect_version = shell(cmd).stdout
        if detect_version != version:
            LOG.error("hdd %s version: ERROR" % device)
        else:
            LOG.debug("hdd %s version: OK" % device)
