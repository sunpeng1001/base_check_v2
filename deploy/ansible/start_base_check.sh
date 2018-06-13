#!/bin/bash
PWD=$(pwd)
cp hosts .hosts
sed -i "s#PWD#$PWD#g" .hosts
#######################################################
echo "usage:sh start_base_check.sh or sh start_base_check.sh --debug/--info"
if [ "$1" == "" ];then
    ansible-playbook roles/base_check/site.yml -e "nodes=tmp" --tags info | grep -v change | grep -v '""' | grep -B 1 msg
elif [ "$1" == "--debug" ];then
    ansible-playbook roles/base_check/site.yml -e "nodes=tmp" --tags debug
elif [ "$1" == "--info" ];then
    ansible-playbook roles/base_check/site.yml -e "nodes=tmp" --tags info
elif [ "$1" == "--vvv" ];then
    ansible-playbook roles/base_check/site.yml -e "nodes=tmp" --tags debug -vvv
else
    exit 1
fi
