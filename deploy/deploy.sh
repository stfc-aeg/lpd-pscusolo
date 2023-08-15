#!/bin/bash

script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ansible_home=${script_dir}/ansible

export ANSIBLE_CONFIG=$ansible_home/ansible.cfg
export ANSIBLE_INVENTORY=$ansible_home/hosts
export ANSIBLE_LIBRARY=$ansible_home
# export ANSIBLE_LOG_PATH=$ansible_home/logs/"$(date +'%Y%m%d-%H%M%S')".log
export ANSIBLE_LOG_PATH=/tmp/"$(date +'%Y%m%d-%H%M%S')".log

ansible-playbook "$@" $ansible_home/deploy_pscu.yml
