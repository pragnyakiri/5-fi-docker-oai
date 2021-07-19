
import os
from flask import Flask
import sys

app= Flask(__name__)
@app.route('/start_demo')
def docker_start():
    os.system('docker-compose up -d')
@app.route('/restart_demo')
def docker_restart():
    os.system('docker-compose down')
    os.system('docker-compose up -d')
    return "success", 200

if __name__=='__main__':
    app.run(host = '0.0.0.0',port=sys.argv[1])
