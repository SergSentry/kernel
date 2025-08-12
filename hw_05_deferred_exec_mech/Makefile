PWD := $(shell pwd)

EX_TASKLET_PATH := $(PWD)/ex_tasklet
EX_WORKQUEUE_PATH := $(PWD)/ex_workqueue


all: format clean build check

build: ex_tasklet ex_workqueue

check: ex_tasklet_check ex_workqueue_check

ex_tasklet:
	@echo "\nBuild ex_tasklet..."
	$(MAKE) -C $(EX_TASKLET_PATH) kbuild

ex_tasklet_check:
	@echo "\nCheck ex_tasklet..."
	$(MAKE) -C $(EX_TASKLET_PATH) check

ex_workqueue:
	@echo "\nBuild ex_workqueue..."
	$(MAKE) -C $(EX_WORKQUEUE_PATH) kbuild

ex_workqueue_check:
	@echo "\nCheck ex_workqueue..."
	$(MAKE) -C $(EX_WORKQUEUE_PATH) check

format:
	@echo "\nFormating up..."
	$(MAKE) -C $(EX_TASKLET_PATH) format
	$(MAKE) -C $(EX_WORKQUEUE_PATH) format

clean:
	@echo "\nCleaning up..."
	$(MAKE) -C $(EX_TASKLET_PATH) clean
	$(MAKE) -C $(EX_WORKQUEUE_PATH) clean

.PHONY: all build check format clean ex_tasklet ex_tasklet_check ex_workqueue ex_workqueue_check
