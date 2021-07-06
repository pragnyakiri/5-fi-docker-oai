import docker
import json
import datetime
import sqlite3
import sched
import time

def remove_numbers(nf_name):
    return ''.join([i for i in nf_name if not i.isdigit()])
list_nfs=['nrf','amf','upf','gnb','ue','udm','udr','smf','ausf','nssf','pcf']    
def calculate_cpu_percent(d):
    cpu_count = len(d["cpu_stats"]["cpu_usage"]["percpu_usage"])
    cpu_percent = 0.0
    cpu_delta = float(d["cpu_stats"]["cpu_usage"]["total_usage"]) - \
                float(d["precpu_stats"]["cpu_usage"]["total_usage"])
    system_delta = float(d["cpu_stats"]["system_cpu_usage"]) - \
                   float(d["precpu_stats"]["system_cpu_usage"])
    if system_delta > 0.0:
        cpu_percent = cpu_delta / system_delta * 100.0 * cpu_count
    return cpu_percent
def calculate_mem_percent(d):
    mem_percent = 0.0
    mem_usage = float(d["memory_stats"]["usage"])
    mem_lim = float(d["memory_stats"]["limit"])
    if mem_usage > 0.0:
        mem_percent = mem_usage / mem_lim * 100.0
    return mem_percent
def get_network_stats(d):
    rx_bytes = float(d["networks"]["eth0"]["rx_bytes"])
    tx_bytes = float(d["networks"]["eth0"]["tx_bytes"])
    return rx_bytes,tx_bytes
def monitor_home(client):
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
    print (json.dumps(monitor_home_page))
def monitor_nf(client,id):
    monitor_nf={"no_PDUsessions":0,
    "no_UEsserved":0,
    "State":'',
    "Health":'',
    "DNN":'',
    "cpu_percent_usage":0,
    "mem_percent_usage":0,
    "Transmit_bytes":0,
    "Received_bytes":0,
    "NF_Logs":''}
    ct = datetime.datetime.now()
    print("current time:-", ct)
    container=client.containers.list(filters={"id":st})
    if len(container)==0:
        print ("no container running with given id")
        return
    print(container)    
    state= 'active' 
    health= 'good'
    DNN=''
    no_PDUsessions=0
    no_servedUEs=0
    if 'upf' in container[0].name:
        DNN = 'internet'
    if 'ue' in container[0].name:
        no_PDUsessions = num_PDUsessions(client,container[0].id)
    if 'gnb' in container[0].name:
        no_servedUEs = num_servedUEs(client,container[0].id)
    
    res = get_stats(client,container[0].id)
    monitor_nf["no_PDUsessions"]=no_PDUsessions
    monitor_nf["no_UEsserved"]=no_servedUEs
    monitor_nf["State"]=state
    monitor_nf["Health"]=health
    monitor_nf["DNN"]=DNN
    monitor_nf["cpu_percent_usage"]=res[0]
    monitor_nf["mem_percent_usage"]=res[1]
    monitor_nf["Transmit_bytes"]=res[2]
    monitor_nf["Received_bytes"]=res[3]
    monitor_nf["NF_Logs"]=get_logs(client,id)
    print (json.dumps(monitor_nf))
    #cmd='/bin/sh -c nr-cli "'
    #cmd='/bin/sh -c nr-cli "'

def create_DB():
    conn = sqlite3.connect('NF_Stats.db')
    print("Opened database successfully")
    st = "CREATE TABLE NFStats (name text, id text, timestamp text, CPU_percent_usage real, Mem_percent_usage real, Tx_bytes real, Rx_bytes real)"
    conn.execute(st)
    print("Table created successfully")
    #return conn

create_DB()
#s = sched.scheduler(time.time, time.sleep)

def save_stats_in_DB(client):
    ct = datetime.datetime.now()
    print("current time: ", ct) 
    conn = sqlite3.connect('NF_Stats.db')
    for container in client.containers.list(): 
        if 'port' in str(container.name) or 'mongo' in str(container.name) or 'webui' in str(container.name) or 'mytb' in str(container.name):
            continue   
        print(container.name + " " + container.id)
        res = get_stats(client,container.id)
        conn.execute("INSERT INTO NFStats (name,id,timestamp,CPU_percent_usage,Mem_percent_usage,Tx_bytes,Rx_bytes) VALUES ( ?, ?, ?, ?, ?, ?, ?)", (container.name, container.id, ct, res[0], res[1], res[2], res[3]) )
    #print("Saving")
    #s.enter(1, 1, save_stats_in_DB, (client,))

#s.enter(1, 1, save_stats_in_DB, (s,client))
#s.run()


def get_logs(client,id):
    for container in client.containers.list():
        if id in str(container.id):
            logs = container.logs().decode("utf-8")
            #print(logs)
            return logs

def num_PDUsessions(client,id):
    for container in client.containers.list():
        if id in str(container.id):
            print(container.name)
            run=container.exec_run('nr-cli --dump')
            temp1=(run.output.decode("utf-8")).split("\n")
            ue_imsi=temp1[0]
            temp1=container.exec_run('nr-cli ' + ue_imsi + ' -e status')
            #print(type(temp1))
            #print(temp1)
            temp2=(temp1.output.decode("utf-8")).split("pdu-sessions:")
            #print(temp2)
            #temp3=temp2.split("pdu-sessions:")
            print(temp2[1])
            #if 'pdu-sessions:' in temp1
            #temp2=(temp1.output.decode("utf-8")).split("pdu-sessions:")
            #print(temp2[1])
            st = "id:"
            res = [i for i in range(len(temp2[1])) if temp2[1].startswith(st, i)] 
            print("The number of PDU sessions indices is : " + str (len(res)))
            return len(res)

def num_servedUEs(client,id):
    for container in client.containers.list():
        if id in str(container.id):
            print(container.name)
            logs = container.logs().decode("utf-8")
            #print(logs)
            st = 'Total number of UEs'
            res = logs.rfind(st) 
            print("The Number of UEs served is : " + logs[res+21])
            return logs[res+21]

def get_stats(client,id):
    for container in client.containers.list():
        if id in str(container.id):
            #print(container.name)
            stats=container.stats(stream=False)
            #print(stats)
            cpu_st = calculate_cpu_percent(stats)
            #print(cpu_st)
            mem_st = calculate_mem_percent(stats)
            #print(mem_st)
            result=get_network_stats(stats)
            #print(result[0])
            #print(result[1])
            return cpu_st, mem_st, result[0], result[1]

client = docker.from_env()
#monitor_home(client)
#st='gnb1'
#st='9cec765fbf802542814fff2491db91ae9866404ad2672e7a1decac36f2b7c4d1'
#monitor_nf(client,st)
#get_logs(client,st)
#num_PDUsessions(client,st)
#num_servedUEs(client,st)
#nf_stats(client,st)

#s = sched.scheduler(time.time, time.sleep)
#def repeat_save_DB(client): 
#    print("Saving")
#    s.enter(2, 1, save_stats_in_DB(client), (sc,))

#s.enter(2, 1, save_stats_in_DB(client), (s,))
#s.run()