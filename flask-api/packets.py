import os
import json
def get_packets(name):
    cmd= 'tshark -r ~/5-fi-packetdata/'+ name+'.pcap -Y " ngap || sctp || nas-5gs || pfcp || icmp || gtp" -e _ws.col.No. -e frame.time -e ip.src -e ip.dst -e _ws.col.Protocol -e _ws.col.Info -l -n -T json'
    stream=os.popen(cmd)
    out= stream.read()
    try:
        pout=json.loads(out)
        return pout
    except:
        return {'packet data': 'Not available'}
