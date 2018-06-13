# -*- coding: utf-8 -*-
from base_check.common.shell import shell
from base_check.common import log as logging

LOG = logging.getLogger(__name__)


class SystemBaseCheckFunc():

    def kernel_release_check(self, kernel_release_conf):
        # 获取linux内核版本
        cmd = "uname -a | awk '{print $3}'"
        kernel_release = shell(cmd).stdout.strip()
        if kernel_release == kernel_release_conf:
            LOG.debug('Kernel_Check:OK')
        else:
            LOG.error('Kernel_Check:Error(%s)' % kernel_release)

    def os_release_check(self, os_release_conf):
        # 获取Linux系统版本
        cmd = "a=$(cat /etc/redhat-release | awk '{print $1}');" \
              "b=$(cat /etc/redhat-release | awk '{print $4}');echo ${a}_${b}"
        os_release = shell(cmd).stdout.strip()
        if os_release == os_release_conf:
            LOG.debug('OS_Check:OK')
        else:
            LOG.error('OS_check:Error(%s)' % os_release)

    def os_service_check(self, service, service_software, service_state_conf):
        # 查看服务软件是否已经安装
        cmd1 = "rpm -qa | grep %s >/dev/null;echo $?" % service_software
        # 获取指定服务的运行状态
        cmd2 = "systemctl status %s | grep Active|" \
              "awk -F '(' '{print $2}' | awk -F ')' '{print $1}'" % service
        service_exist = shell(cmd1).stdout.strip()
        service_state = shell(cmd2).stdout.strip()
        # 判断服务是否已经安装，如果返回值不为0，则代表服务未安装
        if service_exist != '0':
            LOG.error('%s:NotExist' % service)
            return
        if service_state == service_state_conf:
            LOG.debug('%s:OK(%s)' % (service, service_state))
        else:
            LOG.error('%s:Error(%s)' % (service, service_state))

    def os_disk_partition(self):
        # 确保磁盘分区正确，如果正确则返回值为'3'
        cmd = "lsblk | grep  -w -E 'sda|/var|/' | wc -l"
        # 分别获取磁盘sda、/、/var的存储空间
        cmd1 = "lsblk | grep -w sda | awk '{print $4}'"
        cmd2 = "lsblk | grep sda | grep -w / | awk '{print $4}'"
        cmd3 = "lsblk | grep sda  |grep -w /var | awk '{print $4}'"
        disk_partition_format = shell(cmd).stdout.strip()
        sda_disk_size = shell(cmd1).stdout.strip()
        root_partition_size = shell(cmd2).stdout.strip()
        var_partition_size = shell(cmd3).stdout.strip()
        if disk_partition_format != '3':
            LOG.error('Disk_Part:Error')
            return
        # 对比计算各个分区的大小，要求sda分两个分区：系统盘50G，剩余空间都分给/var,否则就报错
        if int(float(root_partition_size.strip('G'))) == 50 \
                and int(float(root_partition_size.strip('G'))) + \
                        int(float(var_partition_size.strip('G'))) \
                        == int(float(sda_disk_size.strip('G'))):
            LOG.debug('sda:%s root:%s var:%s ' %
                      (sda_disk_size, root_partition_size, var_partition_size))
        if int(float(root_partition_size.strip('G'))) != 50:
            LOG.error('root_size:Error(%s)' % root_partition_size)
        if int(float(root_partition_size.strip('G'))) \
                + int(float(var_partition_size.strip('G'))) \
                != int(float(sda_disk_size.strip('G'))):
            LOG.error('var_size:Error(%s)' % var_partition_size)

    def os_disk_raid_check(self):
        # 查看系统磁盘是否配置了RAID,配置返回'0'，没配置返回'1'
        cmd = "lspci -knn | grep 'RAID' > /dev/null && echo 0 || echo 1"
        raid_conf = shell(cmd).stdout.strip()
        if raid_conf == '0':
            LOG.debug('raid_check:OK')
        else:
            LOG.error('raid_check:Error')

    def package_check(self, package):
        # 查看指定软件包是否安装，安装返回'0'，没安装返回'1'
        cmd = "rpm -qa | grep -w %s >/dev/null && echo 0 || echo 1" % package
        package_status_code = shell(cmd).stdout.strip()
        if package_status_code == '0':
            LOG.debug('%s:OK' % package)
        else:
            LOG.error('%s:Error' % package)
