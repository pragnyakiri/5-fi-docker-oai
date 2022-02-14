.PHONY: all build 

REGISTRY=docker.io

build:
	# sudo docker build --target ran-base --tag ran-base:latest --file Dockerfile.base.ubuntu18 .
	sudo docker build --target ran-build --tag ran-build:latest --progress=plain --no-cache --file Dockerfile.build.ubuntu18 .

all: build 

