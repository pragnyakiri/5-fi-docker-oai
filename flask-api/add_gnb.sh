#!/bin/bash

export PCAP_NAME="gnb1"
export AMF_HOSTNAME="amf"
export GNB_HOSTNAME="gnb1"
export MCC="'208'"
export MNC="'93'"
export SST="0x01"
export SD="0x010203"
export NCI="'0x0000000122'"

docker run -e PCAP_NAME -e AMF_HOSTNAME -e GNB_HOSTNAME -e MCC -e MNC -e SS-e SD -e NCI ueransim:3.2.2
