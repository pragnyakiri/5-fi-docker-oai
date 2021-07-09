import docker
import json
import datetime
import sqlite3
from flask import Flask
app= Flask(__name__)
client=docker.from_env()
stop=0

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

####################################

def get_db():
    conn=sqlite3.connect('db_for_flask.db',isolation_level=None)
    #conn.execute('pragma synchronous = 0')
    #conn.execute('pragma journal_mode=wal')
    return conn


def init_db(cursor):
    """Clear existing data and create new tables."""
    sql = "DROP TABLE IF EXISTS stats"
    cursor.execute(sql)
    sql="CREATE TABLE stats (nf_name TEXT NOT NULL, id TEXT , time_stamp TEXT NOT NULL, CPU_percent_usage REAL, Mem_percent_usage REAL, Tx_bytes REAL, Rx_bytes REAL)"
    cursor.execute(sql)



##################################################################################

def save_stats_in_DB(): 
    global stop
    conn = get_db()
    cursor=conn.cursor()
    init_db(cursor)
    while True:
        for container in client.containers.list():
            if 'port' in str(container.name) or 'mongo' in str(container.name) or 'webui' in str(container.name) or 'mytb' in str(container.name):
                continue   
            #print(container.name + " " + container.id)
            ct = datetime.datetime.now()
            res = get_stats(client,container.id)
            try:
                cursor.execute("INSERT INTO stats (nf_name,id,time_stamp,CPU_percent_usage,Mem_percent_usage,Tx_bytes,Rx_bytes) VALUES ( ?, ?, ?, ?, ?, ?, ?)", (container.name, container.id, ct, res[0], res[1], res[2], res[3]) )
            except:
                print ("insert not executing")
            #print (datetime.datetime.now()-ct)
        if stop==1:
            stop =0
            break


def get_logs(client,id):
    for container in client.containers.list():
        if id in str(container.id):
            logs = container.logs().decode("utf-8")
            #print(logs)
            return logs

def num_PDUsessions(client,id):
    for container in client.containers.list():
        if id in str(container.id):
            #print(container.name)
            run=container.exec_run('nr-cli --dump')
            temp1=(run.output.decode("utf-8")).split("\n")
            ue_imsi=temp1[0]
            temp1=container.exec_run('nr-cli ' + ue_imsi + ' -e status')
            #print(type(temp1))
            #print(temp1)
            temp2=(temp1.output.decode("utf-8")).split("pdu-sessions:")
            #print(temp2)
            #temp3=temp2.split("pdu-sessions:")
            #print(temp2[1])
            #if 'pdu-sessions:' in temp1
            #temp2=(temp1.output.decode("utf-8")).split("pdu-sessions:")
            #print(temp2[1])
            st = "id:"
            res = [i for i in range(len(temp2[1])) if temp2[1].startswith(st, i)] 
            #print("The number of PDU sessions indices is : " + str (len(res)))
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
    #ct=datetime.datetime.now()
    container=client.containers.list(filters={"id":id})[0]
    #print(container.name)
    #client_lowlevel = docker.APIClient(base_url='unix://var/run/docker.sock')
    #stats=client_lowlevel.stats(container=container.name,decode=False, stream=False)
    stats=container.stats(stream=False)
    #print (datetime.datetime.now()-ct)
    cpu_st = calculate_cpu_percent(stats)
    mem_st = calculate_mem_percent(stats)
    result=get_network_stats(stats)
    return cpu_st, mem_st, result[0], result[1]
#################################################



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
    return (json.dumps(monitor_home_page))


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
    conn = get_db()
    sql='SELECT * FROM stats where id = "' + id +'"'
    cursor=conn.cursor()
    cursor.execute(sql)
    raw_stats=cursor.fetchall()
    for row in raw_stats:
        stats_data["time_stamp"]=row[2]
        stats_data["cpu_percent_usage"]=row[3]
        stats_data["mem_percent_usage"]=row[4]
        stats_data["Received_bytes"]=row[6]
        stats_data["Transmit_bytes"]=row[5]
        monitor_nf["NF_stats"].append(stats_data)
        stats_data={}

    return json.dumps(monitor_nf)

@app.route("/stop")
def stop_loop():
    global stop
    stop=1
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

#@app.route("handover-prepare/<gnb-containerid and gnb-id and ueid>")
# run handover prepare command

#@app.route("path-switch/<gnb-containerid and gnb-id and ueid>")
# run path switch

# start a thread to dump packet data and stats data into db
import threading
stats_thread=threading.Thread(target=save_stats_in_DB, name="docker_stats")
stats_thread.start()

#start flask app

if __name__=='__main__':
    app.run(port=5001)