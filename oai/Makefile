.PHONY: all build 

REGISTRY=docker.io

build:
     sudo docker build --target ran-base --tag ran-base:latest --file Dockerfile.base.ubuntu18 .
	#sudo docker build --target ran-build --tag ran-build:latest --file Dockerfile.build.ubuntu18 .
    #sudo docker build --target oai-gnb --tag oai-gnb:latest --file Dockerfile.gNB.ubuntu18 .
	#sudo docker build --target oai-nr-ue --tag oai-nr-ue:latest --file Dockerfile.nrUE.ubuntu18 .

all: build