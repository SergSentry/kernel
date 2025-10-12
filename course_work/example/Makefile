PWD := $(shell pwd)

BASIC_PATH := $(PWD)/basic
EXTENDED_PATH := $(PWD)/extended
IOCTL_PATH := $(PWD)/ioctl
PROC_PATH := $(PWD)/proc
SYS_PATH := $(PWD)/sys	

all: format clean build

build: basic extended ioctl proc solve sys

basic:
	@echo "\nBuild basic..."
	$(MAKE) -C $(BASIC_PATH)

extended:
	@echo "\nBuild extended..."
	$(MAKE) -C $(EXTENDED_PATH)

ioctl:
	@echo "\nBuild ioctl..."
	$(MAKE) -C $(IOCTL_PATH)

proc:
	@echo "\nBuild proc..."
	$(MAKE) -C $(PROC_PATH)

sys:
	@echo "\nBuild sys..."
	$(MAKE) -C $(SYS_PATH)

format:
	@echo "\nFormating up..."
	$(MAKE) -C $(BASIC_PATH) format
	$(MAKE) -C $(EXTENDED_PATH) format
	$(MAKE) -C $(IOCTL_PATH) format
	$(MAKE) -C $(PROC_PATH) format
	$(MAKE) -C $(SYS_PATH) format

clean:
	@echo "\nCleaning up..."
	$(MAKE) -C $(BASIC_PATH) clean
	$(MAKE) -C $(EXTENDED_PATH) clean
	$(MAKE) -C $(IOCTL_PATH) clean
	$(MAKE) -C $(PROC_PATH) clean
	$(MAKE) -C $(SYS_PATH) clean

.PHONY: all format clean basic extended ioctl proc sys
