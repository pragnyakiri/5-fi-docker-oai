# 5-fi-docker-oai
## 1. Building the images

Clone the git

'git clone https://gitlab.eurecom.fr/oai/openairinterface5g.git
cd openairinterface5g
git checkout develop'

Build images

'docker build --target ran-base --tag ran-base:latest --file docker/Dockerfile.base.ubuntu18 .
docker build --target ran-build --tag ran-build:latest --file docker/Dockerfile.build.ubuntu18 .
docker build --target oai-gnb --tag oai-gnb:latest --file docker/Dockerfile.gNB.ubuntu18 .
docker build --target oai-nr-ue --tag oai-nr-ue:latest --file docker/Dockerfile.nrUE.ubuntu18 .'

## 2. Running docker-compose

Clone the git

'cd ~
git clone https://github.com/pragnyakiri/5-fi-docker-oai.git
cd 5-fi-docker-oai/free5gc-compose/'
'make base
docker-compose build
docker-compose up -d'


# python-api
Pre-requisites:
Python3
flask (pip3 install flask)

go to flask-api folder and run python_api.py like below

`cd flask-api`
`python3 python_api.py <port number>`

The following are the url calls you can make:
 
 1. List all containers:
 `<ip.address>:<port>/monitor_home`
 
 2. Display container stats:
 `<ip.address>:<port>/monitor_nf/<container_id>`
 
 3. List all gNBs:
` <ip.address>:<port>/manage_ran/list_ran_nodes`
  
The steps in the process of handover in the demo and corresponding url calls:
  
  1. Go to source gNB monitor page by following url:

 `<ip.address>:<port>/monitor_nf/<source_gnb_container_id>`
 
 2. Click on handover-prepare button that opens a popup of avaialble ues to handover. The url to get available ues to populate in popup:
  
 `<ip.address>:<port>/uelist/<source_gnb_container_id>`
 
 3. select one of the ues in the popup and click ok. this should call following url:
 
 `<ip.address>:<port>/handover_prepare/<source_gnb_container_id>?ueid= <ueid of selected ue in the popup>`
 
 4. Go to target gNB monitor page by follwoing url:
 
 `<ip.address>:<port>/monitor_nf/<target_gnb_container_id>`
 
 5. click on path switch request button. A popup will appear.That should call following url to populate popup:
 
 `<ip.address>:<port>/list_pathsw`
 
 6. select one of the items in the popup, that should call following url:
 
 `<ip.address>:<port>/pathsw/<target_gnb_container_id>?id=<id of selected entry in the popup>`
  
