.PHONY: all build 

REGISTRY=docker.io
IMAGE=ueransim
TAG=3.2.2

build:
	docker build -t ${IMAGE}:${TAG} --build-arg version=v${TAG} .


all: build 

