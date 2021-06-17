#!/bin/bash

set -e

if [ $# -lt 1 ]
then
        echo "Usage : $0 [gnb|ue]"
        exit
fi

command=$1

sub=upfd
echo "entrypoint is called for:"$command
case "$command" in

*"$SUB"*)  echo "Launching upf"
    sysctl -w net.ipv4.ip_forward=1
    iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
    iptables -A FORWARD -p tcp -m tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss 1400
    systemctl stop ufw
    ;;
esac
