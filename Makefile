# TODO Check out https://philpep.org/blog/a-makefile-for-your-dockerfiles
.PHONY: help docker docker docker-push test integration-test

# Full path to dir containing this Makefile
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))


.DEFAULT: help
help:
	@echo
	@echo "make test"
	@echo "     :::  Run tests -- automatically rebuilds docker container if notectl/requirements.txt changes"
	@echo "make shell"
	@echo "     :::  Drop into a shell (docker). Useful for debugging / development."
	@echo "make docker-release"
	@echo "     :::  Build release container; uses notectl/docker-prod.sh to deploy a production release."
	@echo "make package APP_NAME=<app_name> [VERSION=<version> REGISTRY_HOST=<registry_host>]"
	@echo "     :::  Build release app; uses notectl/make-app.sh to deploy an app to your registry."
	@echo

test:
	./run-tests.sh ;

integration-test:
	HUB_IP=$(HUB_IP) ./notectl/run-tests.sh integration ;

gatling:
	docker run --network noteworthy --rm -it -v $(ROOT_DIR)/perftest/gatling/user-files:/opt/gatling/user-files -v $(ROOT_DIR)/perftest/gatling/results:/opt/gatling/results --name noteworthy-gatling-$(shell date +"%H-%M_%m-%d") denvazh/gatling -s $(SIM_NAME) ;

docker:
	docker build --build-arg GIT_COMMIT=$(GIT_COMMIT) --build-arg RELEASE_TAG=$(RELEASE_TAG) -t decentralabs/noteworthy:$(ROLE)-$(RELEASE_TAG) -f Dockerfile.$(ROLE) . ;

docker-push:
	echo ${DOCKERHUB_PSW}| docker login -u ${DOCKERHUB_USR} --password-stdin ;
	docker tag decentralabs/noteworthy:$(ROLE)-$(RELEASE_TAG) decentralabs/noteworthy:$(ROLE)-$(RELEASE_TAG)-$(GIT_COMMIT) ;
	docker push decentralabs/noteworthy:$(ROLE)-$(RELEASE_TAG) ;
	docker push decentralabs/noteworthy:$(ROLE)-$(RELEASE_TAG)-$(GIT_COMMIT) ;

.dev-last-build: requirements.base.txt requirements.dev.txt
	docker build -t noteworthy:dev -f Dockerfile.dev . ;
	echo $(shell date) > .dev-last-build ;

dev shell: .dev-last-build
	docker run --network noteworthy --rm -it -e NOTEWORTHY_DEV_BIND_MOUNT_PATH=$(ROOT_DIR) -v /usr/local/bin/docker:/usr/local/bin/docker -v /var/run/docker.sock:/var/run/docker.sock -v $(ROOT_DIR):/opt/noteworthy --name noteworthy-dev-$(shell date +"%H-%M_%m-%d") noteworthy:dev;
