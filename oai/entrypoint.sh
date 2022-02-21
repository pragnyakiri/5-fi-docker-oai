#!/bin/bash

export AMF_ADDR="$(host -4 amf |awk '/has.*address/{print $NF; exit}')" 
sed -i "s/CI_MME_IP_ADDR/$AMF_ADDR/" /opt/oai-gnb/etc/gnb.conf
sed -i 's/CI_GNB_IP_ADDR/10.100.200.50/' /opt/oai-gnb/etc/gnb.conf
sed -i 's/em1/eth0/' /opt/oai-gnb/etc/gnb.conf