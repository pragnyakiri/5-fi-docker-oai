  #!/bin/sh
    
  ### run tshark to capture packets within upf
  ### goto /data/5-fi-packetdata and run tail -c +1 -f upf-1.pcap | wireshark -k -i - to view the traffic live
  UPFNS="upf-1"
  tcpdump -i any -w ../pcapdata/${UPFNS}.pcap
