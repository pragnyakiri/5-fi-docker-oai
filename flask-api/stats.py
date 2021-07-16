import docker
import multiprocessing as mp
import sqlite3
import datetime
stop=0

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

def get_db():
    conn=sqlite3.connect('db_for_flask.db',isolation_level=None)
    return conn


def init_db(cursor):
    """Clear existing data and create new tables."""
    sql = "DROP TABLE IF EXISTS stats"
    cursor.execute(sql)
    sql="CREATE TABLE stats (nf_name TEXT NOT NULL, id TEXT , time_stamp TEXT NOT NULL, CPU_percent_usage REAL, Mem_percent_usage REAL, Tx_bytes REAL, Rx_bytes REAL)"
    cursor.execute(sql)


def stats(container,cursor):
    global stop
    if 'port' in str(container) or 'mongo' in str(container) or 'webui' in str(container) or 'mytb' in str(container):
        return
    ct = datetime.datetime.now()
    try:
        client_lowlevel = docker.APIClient(base_url='unix://var/run/docker.sock')
        client_stats=client_lowlevel.stats(container=container.name, stream=False)
        cpu_st = calculate_cpu_percent(client_stats)
        mem_st = calculate_mem_percent(client_stats)
        result=get_network_stats(client_stats)
    except:
        print("stats are not being collected")
        return
    try:
        cursor.execute("INSERT INTO stats (nf_name,id,time_stamp,CPU_percent_usage,Mem_percent_usage,Tx_bytes,Rx_bytes) VALUES ( ?, ?, ?, ?, ?, ?, ?)", (container.name, container.id, ct, cpu_st, mem_st, result[0], result[1]) )
    except:
        print ("insert not executing")
    return


def get_stats(client):
    global stop
    conn = get_db()
    cursor=conn.cursor()
    init_db(cursor)
    while True:
        if stop ==1:
            stop=0
            break
        processes =[ mp.Process(target=stats, args=(server,cursor)) for server in client.containers.list()]
        """ processes =[]
        for container in client.containers.list():
            p=mp.Process(target=stats,args=(container))
            processes.append(p)
        """
        # Run processes
        for p in processes:
            p.start()

        # Exit the completed processes
        for p in processes:
            p.join()
        #print(output.get())


def read_stats_db(id):
    conn = get_db()
    sql='SELECT * FROM stats where id = "' + id +'"'
    cursor=conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()
def kill_stats_collection():
    global stop
    stop=1