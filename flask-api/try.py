import docker
import json
import datetime
import sqlite3

def get_handover_ue(client,id):
    container=client.containers.list(filters={"id":id})[0]
    print(container.name)
    run=container.exec_run('nr-cli --dump')
    temp1=(run.output.decode("utf-8")).split("\n")
    gnb_id=temp1[0]
    temp1=container.exec_run('nr-cli ' + gnb_id + ' -e ue-list')
    #print(type(temp1))
    print(temp1)
    #temp2=(temp1.output.decode("utf-8")).split("pdu-sessions:")

#@app.route("handover-prepare/<gnb-containerid and gnb-id and ueid>")
# run handover prepare command

#@app.route("path-switch/<gnb-containerid and gnb-id and ueid>")
# run path switch

client=docker.from_env()
id = "7f4c89c095e7040ff0e7d05b6a0c20de40ff406f6cda8415c2e705fd0bb94ce6"
get_handover_ue(client,id)
