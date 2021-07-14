  #!/bin/sh
    
  ### run tshark to capture packets within upf
  ### goto 5-fi-packetdata folder and run tail -c +1 -f upf-1.pcap | wireshark -k -i - to view the traffic live
  NF=$1
  tcpdump -i any -U -w ../pcapdata/${NF}.pcap
