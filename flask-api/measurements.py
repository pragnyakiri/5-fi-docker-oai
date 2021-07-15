import docker
import json
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

def get_db():
    conn=sqlite3.connect('db_for_flask.db',isolation_level=None)
    return conn

def make_meas_table():
    conn = get_db()
    cursor=conn.cursor()
    """Clear existing data and create new table for measurements"""
    sql = "DROP TABLE IF EXISTS measurements"
    cursor.execute(sql)
    sql="CREATE TABLE measurements (nf_name TEXT NOT NULL, id TEXT NOT NULL, time_stamp TEXT NOT NULL, DL_Thp REAL, UL_Thp REAL, Latency REAL)"
    cursor.execute(sql)
    return cursor
    
def if_table_exists(cursor,table_name):
    sql="SELECT name FROM sqlite_master WHERE type='table' AND name='"+table_name+"'; "
    listOfTables = cursor.execute(sql).fetchall()
    if listOfTables == []:
        return False
    else:
        return True

def get_IPaddress(client,id):
    container=client.containers.list(filters={"id":id})
    if len(container)==0:
        print ("no container running with given id")
        return
    run=container[0].exec_run('ip -j a')
    ipraw= run.output.decode("utf-8")
    ipjson=json.loads(ipraw)
    for dicts in ipjson:
        if dicts['ifname']=='uesimtun0':
            for subdicts in dicts['addr_info']: 
                if  subdicts['label']=='uesimtun0':
                    return subdicts['local']

def write(client):
    cursor = make_meas_table()
    for container in client.containers.list():
        if 'ue' in str(container.name):
            IPaddr = get_IPaddress(client,container.id)
            str1 = 'docker exec -it' + container.name + '/bin/bash'
            container.exec_run(str1)
            str2 = 'speedtest-cli --source ' + IPaddr + ' --json --timeout 40'
            try:
                run=container.exec_run(str2)
                temp1=(run.output.decode("utf-8"))
                print(temp1)
                temp2=json.loads(temp1)
                dl_thp = temp2['download'] # bits per second
                ul_thp = temp2['upload']
                ts = temp2['timestamp']
                latency = temp2['server']['latency']
            except:
                print ("Error in running speedtest")
            try:
                cursor.execute("INSERT INTO measurements (nf_name,id,time_stamp,DL_Thp,UL_Thp,latency) VALUES ( ?, ?, ?, ?, ?, ?)", (container.name, container.id, ts, dl_thp, ul_thp, latency) )
            except:
                print ("measurements insert not executing")


def read():
    conn=get_db()
    cursor=conn.cursor()
    sql="SELECT * FROM measurements"
    if if_table_exists(cursor,'measurements'):
        cursor.execute(sql)
        args=cursor.fetchall()
    else:
        args=0
        print("No data exists")
    cursor.close()
    conn.close()
    print(args)
    return args


#client=docker.from_env()
#id = "b840504ac9a7984ab2fbf6fca067363e1ba4038a3a522acb52b60ae623bc10e7"
#get_num_ActiveUEs(client)
#write(client)
#res=read()
#print(res)
#get_IPaddress(client,id)