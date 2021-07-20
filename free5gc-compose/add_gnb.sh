#!/bin/bash

echo "$1"
docker run --name "gnb3" --network-alias \
"gnb3" --ip "10.100.200.22" --network="free5gc-compose_privnet" \
-v "/home/manoj/5-fi-docker/free5gc-compose/config/pcap.sh:/pcap.sh" -v "/home/manoj/5-fi-packetdata:/pcapdata" --env AMF_ADDR=$1 ueransim:3.2.2 gnbz
