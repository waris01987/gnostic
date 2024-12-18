# Determine the operating system
OS := $(shell uname)

# Use different commands based on the operating system
ifeq ($(OS), Linux)
    # Commands for Linux (Ubuntu)
    DC := docker-compose
    PS := sudo docker ps
    BUILD := sudo $(DC) -f docker-compose.yml build
    UP := sudo $(DC) -f docker-compose.yml up
    DOWN := sudo $(DC) -f docker-compose.yml down
    REMOVE_IMAGES := sudo docker rmi -f $$(docker images -q)
    TEST-BUILD := sudo $(DC) -f docker-compose-test.yml build
    TEST-UP := sudo $(DC) -f docker-compose-test.yml up
else ifeq ($(OS), Windows_NT)
    # Commands for Windows
    DC := docker-compose
    PS := docker ps
    BUILD := $(DC) build
    UP := $(DC) up
    DOWN := $(DC) down
    REMOVE_IMAGES := docker rmi -f $$(docker images -q)
    TEST-BUILD := $(DC) -f docker-compose-test.yml build
    TEST-UP := $(DC) -f docker-compose-test.yml up
else
    $(error Unsupported operating system)
endif

# Define targets
ps:
	$(PS)

build:
	$(BUILD)

up:
	$(UP)

down d:
	$(DOWN)

remove-images:
	$(REMOVE_IMAGES)

down-all: down remove-images

test-build:
	$(TEST-BUILD)

test-up:
	$(TEST-UP)

run r: build up

test t: test-build test-up