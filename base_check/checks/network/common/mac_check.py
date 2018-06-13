# -*- coding: utf-8 -*-
import os
from base_check.common.shell import shell


device_list = os.listdir('/sys/class/net/')


class MacExamine():

    def get_network_device_mac(self, device):
        cmd1 = "ip -o link|grep %s |grep master&>/dev/null;echo $?" % device
        bond_result = shell(cmd1).stdout
        # bond_result 变量为cmd1执行结果返回值，成功返回0，代表网卡为bond网卡，
        # 其他值则代表网卡不是bond设备
        if device not in device_list:
            return None
        elif int(bond_result) == 0:
            cmd2 = "ip -o link|grep %s |grep master|awk '{print $9}'" % device
            bond_master = shell(cmd2).stdout
            cmd3 = "cat /proc/net/bonding/%s |grep -C 5 $device|" \
                   "grep Permanent|wc -l" % bond_master.strip()
            slave_num = shell(cmd3).stdout
            # slave_num 变量表示bond设备绑定网卡的数量
            if int(slave_num) == 2:
                cmd4 = "cat /proc/net/bonding/%s|" \
                       "grep -C 5  %s|grep Permanent|awk NR==2|" \
                       "awk '{print $4}'" % (bond_master.strip(), device)
                slave_device_mac = shell(cmd4).stdout
                return slave_device_mac.strip()
            else:
                cmd5 = "cat /proc/net/bonding/%s|" \
                       "grep -C 5 %s|grep Permanent|" \
                       "awk '{print $4}'" % (bond_master.strip(), device)
                slave_device_mac = shell(cmd5).stdout
                return slave_device_mac.strip()
        else:
            cmd6 = "cat /sys/class/net/%s/address" % device
            device_mac = shell(cmd6).stdout
            return device_mac.strip()
