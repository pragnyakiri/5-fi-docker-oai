import docker
import json
import datetime
import multiprocessing as mp
from flask import Flask, request, jsonify
import stats
import threading
import time
app= Flask(__name__)
client=docker.from_env()
stop=0

def get_logs(client,id):
    for container in client.containers.list():
        if id in str(container.id):
            logs = container.logs().decode("utf-8")
            #print(logs)
            return logs

def num_PDUsessions(client,id):
    for container in client.containers.list():
        if id in str(container.id):
            run=container.exec_run('nr-cli --dump')
            temp1=(run.output.decode("utf-8")).split("\n")
            ue_imsi=temp1[0]
            temp1=container.exec_run('nr-cli ' + ue_imsi + ' -e status')
            temp2=(temp1.output.decode("utf-8")).split("pdu-sessions:")
            st = "id:"
            res = [i for i in range(len(temp2[1])) if temp2[1].startswith(st, i)]
            return len(res)

def num_servedUEs(client,id):
    for container in client.containers.list():
        if id in str(container.id):
            #print(container.name)
            logs = container.logs().decode("utf-8")
            #print(logs)
            st = 'Total number of UEs'
            res = logs.rfind(st) 
            #print("The Number of UEs served is : " + logs[res+21])
            return logs[res+21]


#################################################


list_nfs=['nrf','amf','upf','gnb','ue','udm','udr','smf','ausf','nssf','pcf']    

@app.route('/monitor_home')
def monitor_home():

    monitor_home_page={"count_active_cells":0,
    "count_available_cells":0,
    "List_NFs":[],
    "counts_in_topo":{}}
    #NF_details={"type":'',"name":'', 'count': 0, "containerid":"", "internet":""}
    counts_details={"nfs":0,"upfs":0, 'gnbs': 0, "rrhs":0, "ues":0}
    for container in client.containers.list():
        NF_details={}
        if 'port' in str(container.name) or 'mongo' in str(container.name) or 'webui' in str(container.name) or 'mytb' in str(container.name):
            continue
        NF_details["name"]=container.name
        match = next((x for x in list_nfs if x in container.name), False)
        NF_details["type"] = match#remove_numbers(container.name)
        NF_details["containerid"]=container.id
        NF_details["count"] =len(client.containers.list(filters={'name':NF_details['type']+'.*'}))
        NF_details["internet"] = 'yes'
        monitor_home_page["List_NFs"].append(NF_details)
        if "free5gc" in str(container.image):
            counts_details["nfs"]+=1
        
    counts_details["upfs"]= len(client.containers.list(filters={'name':'upf.*'}))
    counts_details["gnbs"]= len(client.containers.list(filters={'name':'gnb.*'}))
    counts_details["rrhs"]= len(client.containers.list(filters={'name':'gnb.*'}))
    counts_details["ues"]= len(client.containers.list(filters={'name':'ue.*'}))
    monitor_home_page["counts_in_topo"]=counts_details
    monitor_home_page["count_active_cells"]=counts_details["gnbs"]
    monitor_home_page["count_available_cells"]=counts_details['gnbs']
    return (jsonify(monitor_home_page))


@app.route('/monitor_nf/<id>')
def monitor_nf(id):
#dictionaries for json
    stats_data={ "time_stamp":'',
    "cpu_percent_usage":0,
    "mem_percent_usage":0,
    "Transmit_bytes":0,
    "Received_bytes":0}
    monitor_nf={"name_of_nf":'',
    "no_PDUsessions":0,
    "no_UEsserved":0,
    "State":'',
    "Health":'',
    "DNN":'',
    "NF_stats":[],
    "NF_Logs":''}
    ct = datetime.datetime.now()
    #print("current time:-", ct)
    container=client.containers.list(filters={"id":id})
    if len(container)==0:
        print ("no container running with given id")
        return
    #print(container)    
    state= 'active' 
    health= 'good'
    DNN=''
    no_PDUsessions=0
    no_servedUEs=0
    monitor_nf["name_of_nf"]=container[0].name
    if 'upf' in container[0].name:
        DNN = 'internet'
    if 'ue' in container[0].name:
        no_PDUsessions = num_PDUsessions(client,container[0].id)
    if 'gnb' in container[0].name:
        no_servedUEs = num_servedUEs(client,container[0].id)
    
    # res = get_stats(client,container[0].id)
    monitor_nf["no_PDUsessions"]=no_PDUsessions
    monitor_nf["no_UEsserved"]=no_servedUEs
    monitor_nf["State"]=state
    monitor_nf["Health"]=health
    monitor_nf["DNN"]=DNN
    monitor_nf["NF_Logs"]=get_logs(client,id)
    raw_stats=stats.read_stats_db(id)
    print ("raw stats are", raw_stats)
    for row in raw_stats:
        stats_data["time_stamp"]=row[2]
        stats_data["cpu_percent_usage"]=row[3]
        stats_data["mem_percent_usage"]=row[4]
        stats_data["Received_bytes"]=row[6]
        stats_data["Transmit_bytes"]=row[5]
        monitor_nf["NF_stats"].append(stats_data)
        print (stats_data)
        stats_data={}

    return json.dumps(monitor_nf)

@app.route("/stop")
def stop_loop():
    stats.kill_stats_collection()
    return "successfuly stopped the loop"

#@app.route("/handover/<id>")#Give gNB container id
#run nr-cli <gnb-id> and run list ues that we will give back
def get_handover_ue(client,id):
    container=client.containers.list(filters={"id":id})[0]
    print(container.name)
    run=container.exec_run('nr-cli --dump')
    temp1=(run.output.decode("utf-8")).split("\n")
    gnb_id=temp1[0]
    temp1=container.exec_run('nr-cli ' + gnb_id + ' -e info')
    #print(type(temp1))
    print(temp1)
    #temp2=(temp1.output.decode("utf-8")).split("pdu-sessions:")
@app.route("/uelist/<id>")
def list_ues(id):
    container=client.containers.list(filters={"id":id})[0]
    run=container.exec_run('nr-cli --dump')
    temp1=(run.output.decode("utf-8")).split("\n")
    gnb_id=temp1[0]
    run=container.exec_run('nr-cli ' + gnb_id + ' -e ue-list')
    temp1=run.output.decode("utf-8").split("\n")
    ue_list=[]
    ue_details={}
    for item in temp1:
        print(item)
        if "ue-id" in item:
            if len(ue_details.keys())>0:
                ue_list.append(ue_details)
            ue_details={}
        try:
            ue_details[item.split(':')[0]]= item.split(':')[1]
        except IndexError:
            continue
    ue_list.append(ue_details)
    return json.dumps({'UElist':ue_list})
    
def container_exec_run(container,cmd):
    container.exec_run(cmd)
    return
@app.route("/handover_prepare/<id>") #handover-prepare/<gnb-containerid and gnb-id and ueid>
# run handover prepare command
def handover_prepare(id):
    url_params=request.args
    #print (id, url_params)
    container=client.containers.list(filters={"id":id})[0]
    run=container.exec_run('nr-cli --dump')
    temp1=(run.output.decode("utf-8")).split("\n")
    gnb_id=temp1[0]
    cmd='nr-cli ' + gnb_id + ' -e "handover-prepare ' + url_params['ueid']+'"'
    run=container.exec_run(cmd)
    temp1=run.output.decode("utf-8")
    print (temp1)
    details={}
    if 'copy for handover' in temp1:
        details={}
        raw_str=temp1.split('copy for')[-1]
        for item in raw_str.split('\n'):
            if ':' in item:
                if '[debug]' in item:
                    item=item.split('[debug]')[-1]
                details[item.split(':')[0].strip()]= item.split(':')[1].strip()
    #handover_thread.join()
    return json.dumps({'handover details':details})


#@app.route("path-switch/<gnb-containerid and gnb-id and ueid>")
# run path switch

# start a thread to dump packet data and stats data into db

stats_thread=threading.Thread(target=stats.get_stats, args=(client,), name="docker_stats")
stats_thread.start()

#start flask app

if __name__=='__main__':
    app.run(port=5001)