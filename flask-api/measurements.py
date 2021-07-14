import docker
import json
import datetime
import sqlite3

# 1. Data Volume measurement separately for DL and UL, per QCI per UE, by eNB
# 2. Throughput separately for DL and UL, per RAB per UE and per UE for the DL, per UE for the UL, by eNB
# 3. Packet Delay measurement, separately for DL and UL, per QCI per UE
# 4. Packet Loss rate measurement, separately for DL and UL per QCI per UE, by the eNB
# 5. Number of active UEs in RRC_CONNECTED

def get_num_ActiveUEs(client):
    Num_ActiveUEs=[]
    for container in client.containers.list():
        if 'gnb' in str(container.name):
            print(container.name)
            run=container.exec_run('nr-cli --dump')
            temp1=(run.output.decode("utf-8")).split("\n")
            gnb_id=temp1[0]
            temp1=container.exec_run('nr-cli ' + gnb_id + ' -e ue-list')
            #print(type(temp1))
            #print(temp1)
            temp2=temp1.output.decode("utf-8")
            st = "ue-id:"
            res = [i for i in range(len(temp2)) if temp2.startswith(st, i)]
            #print(len(res))
            Num_ActiveUEs.append(len(res)) 
            #return len(res)
    print(Num_ActiveUEs)
    sum=0
    for i in Num_ActiveUEs:
        sum = sum + i      
    print(sum)
    return(sum)  
            
#@app.route("handover-prepare/<gnb-containerid and gnb-id and ueid>")
# run handover prepare command

client=docker.from_env()
#id = "7f4c89c095e7040ff0e7d05b6a0c20de40ff406f6cda8415c2e705fd0bb94ce6"
get_num_ActiveUEs(client)
