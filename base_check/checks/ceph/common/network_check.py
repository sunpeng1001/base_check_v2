# -*- coding:utf-8 -*-
import os
from base_check.common.shell import shell
from base_check.common import log as logging

LOG = logging.getLogger(__name__)


class NetworkExamine():

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

    def check_network_number(self, counts):
        cmd1 = "lspci | grep Ethernet | awk '{print $1}'"
        pci_buses = shell(cmd1).stdout.split('\n')
        for pci_bus in pci_buses:
            for key in counts.keys():
                cmd2 = "cat lshw.tmp.txt | grep -A5 %s | grep -i %s " \
                       % (pci_bus, key)
                if shell(cmd2).returncode == 0:
                    counts[key] = counts[key] - 1
        flag = True
        for key, val in counts.iteritems():
            if val != 0:
                flag = False
                LOG.error("number of %s network card: ERROR" % key)
        return flag

    def get_network_name(self, speeds):
        if not os.path.isfile('lshw.tmp.txt'):
            LOG.error("lshw.tmp.txt doesn't exist!")
            return
        cmd1 = "lspci | grep Ethernet | awk '{print $1}'"
        pci_buses = shell(cmd1).stdout.split('\n')
        network_name = dict()
        for speed in speeds:
            network_name[speed] = list()
        for pci_bus in pci_buses:
            for speed in speeds:
                cmd2 = "cat lshw.tmp.txt | grep -A5 %s | grep -i %s " \
                       % (pci_bus, speed)
                if shell(cmd2).returncode == 0:
                    cmd3 = "cat lshw.tmp.txt | grep -A1 %s | grep 'logical name' | " \
                           "awk '{print $3}'" % pci_bus
                    network_name[speed].append(shell(cmd3).stdout)
        # network_name.sort()
        return network_name

    def check_network_mac(self, mac):
        if not os.path.isfile('lshw.tmp.txt'):
            LOG.error("lshw.tmp.txt doesn't exist!")
            return
        all_eth = self.get_network_name(mac.keys())
        for speed, eths in all_eth.iteritems():
            for eth in eths:
                cmd = "ip link | grep -A1 ' %s:' | grep ether | " \
                      "awk '{print $2}' | sed 's/[ \t]*//g'" % eth
                detect_network_mac = shell(cmd).stdout
                if detect_network_mac.lower() not in mac[speed]:
                    LOG.error("network %s mac: ERROR" % eth)
                else:
                    LOG.debug("network %s mac: OK" % eth)

    def check_network_numa_node(self, speeds):
        for num, speed in speeds.iteritems():
            if int(num) >= 10:
                all_eth = self.get_network_name([speed])
                eths = all_eth[speed]
                if len(eths) > 1:
                    cmd1 = "lscpu | grep 'NUMA node(s)' | awk -F: " \
                           "'{printf $2}' | sed 's/[ \t]*//g'"
                    num_of_numa = int(shell(cmd1).stdout)
                    numa_nodes = list()
                    for index in xrange(num_of_numa):
                        numa_nodes.append(0)
                    for eth in eths:
                        cmd2 = "cat /sys/class/net/%s/device/numa_node" % eth
                        detect_numa_node = int(shell(cmd2).stdout)
                        numa_nodes[detect_numa_node] = \
                            1 + numa_nodes[detect_numa_node]
                    numa_nodes.sort()
                    if numa_nodes[0] == numa_nodes[-1] and numa_nodes[0] != 0:
                        LOG.debug("%s network numa balance : OK" % speed)
                    else:
                        LOG.error("%s network numa balance : ERROR" % speed)

    def check_network_interrupt_node(self, speeds):
        for num, speed in speeds.iteritems():
            if int(num) >= 10:
                all_eth = self.get_network_name([speed])
                eths = all_eth[speed]
                for eth in eths:
                    cmd1 = "cat /sys/class/net/%s/device/numa_node" % eth
                    detect_numa_node = int(shell(cmd1).stdout)
                    cmd2 = "cat /proc/interrupts | grep %s | " \
                           "awk -F: 'NR==1 {print $1}' | sed 's/^[ \t]*//g'" \
                           % eth
                    interrupt = shell(cmd2).stdout
                    cmd3 = "cat /proc/irq/%s/node | awk '{print $1}'" \
                           % interrupt
                    detect_interrupt_node = int(shell(cmd3).stdout)
                    if detect_interrupt_node != detect_numa_node:
                        LOG.error("network %s interrupt node: ERROR" % eth)
                    else:
                        LOG.debug("network %s interrupt node: OK" % eth)

    def check_network_vendor(self, vendor):
        if not os.path.isfile('lshw.tmp.txt'):
            LOG.error("lshw.tmp.txt doesn't exist!")
            return
        all_eth = self.get_network_name(vendor.keys())
        for speed, eths in all_eth.iteritems():
            for eth in eths:
                cmd = "cat lshw.tmp.txt | grep -B4 %s | grep vendor | " \
                      "awk -F: '{print $2}' | sed 's/^[ \t]*//g'" % eth
                detect_vendor = shell(cmd).stdout
                if detect_vendor not in vendor[speed]:
                    LOG.error("network %s vendor: ERROR" % eth)
                else:
                    LOG.debug("network %s vendor: OK" % eth)

    def check_network_version(self, version):
        if not os.path.isfile('lshw.tmp.txt'):
            LOG.error("lshw.tmp.txt doesn't exist!")
            return
        all_eth = self.get_network_name(version.keys())
        for speed, eths in all_eth.iteritems():
            for eth in eths:
                cmd = "cat lshw.tmp.txt | grep -B4 %s | grep product | " \
                      "awk -F: '{print $2}' | sed 's/^[ \t]*//g'" % eth
                detect_version = shell(cmd).stdout
                if detect_version not in version[speed]:
                    LOG.error("network %s version: ERROR" % eth)
                else:
                    LOG.debug("network %s version: OK" % eth)
