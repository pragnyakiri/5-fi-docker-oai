DOCKER_IMAGE_OWNER = 'free5gc'
DOCKER_IMAGE_NAME = 'base'
DOCKER_IMAGE_TAG = 'latest'
DIR ='5-fi-packetdata'

.PHONY: base
base:
	docker build -t ${DOCKER_IMAGE_OWNER}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} ./base
	if [ ! -d /home/${USER}/${DIR} ]; then \
		mkdir /home/${USER}/${DIR}; \
	fi
	docker image ls ${DOCKER_IMAGE_OWNER}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}
