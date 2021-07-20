IMAGE := amuench/schema-registry:0.1

build:
	docker build -t $(IMAGE) -f Dockerfile python