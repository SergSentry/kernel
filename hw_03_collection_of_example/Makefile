PWD := $(shell pwd)

EX_LIST_PATH := $(PWD)/ex_list
EX_STACK_PATH := $(PWD)/ex_stack
EX_QUEUE_PATH := $(PWD)/ex_queue

all: format clear build check

build: ex_list ex_stack ex_queue

check: ex_list_check ex_stack_check ex_queue_check

ex_list:
	@echo "\nBuild ex_list..."
	$(MAKE) -C $(EX_LIST_PATH) kbuild

ex_list_check:
	@echo "\nCheck ex_list..."
	$(MAKE) -C $(EX_LIST_PATH) check

ex_stack:
	@echo "\nBuild ex_stack..."
	$(MAKE) -C $(EX_STACK_PATH) kbuild

ex_stack_check:
	@echo "\nCheck ex_stack..."
	$(MAKE) -C $(EX_STACK_PATH) check

ex_queue:
	@echo "\nBuild ex_queue..."
	$(MAKE) -C $(EX_QUEUE_PATH) kbuild

ex_queue_check:
	@echo "\nCheck ex_queue..."
	$(MAKE) -C $(EX_QUEUE_PATH) check

format:
	@echo "\nFormating up..."
	$(MAKE) -C $(EX_LIST_PATH) format
	$(MAKE) -C $(EX_STACK_PATH) format
	$(MAKE) -C $(EX_QUEUE_PATH) format

clean:
	@echo "\nCleaning up..."
	$(MAKE) -C $(EX_LIST_PATH) clean
	$(MAKE) -C $(EX_STACK_PATH) clean
	$(MAKE) -C $(EX_QUEUE_PATH) clean

.PHONY: all build check format clean ex_list ex_list_check ex_stack ex_stack_check ex_queue ex_queue_check
