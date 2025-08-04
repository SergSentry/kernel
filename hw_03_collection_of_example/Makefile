PWD := $(shell pwd)

EX_LIST_PATH := $(PWD)/ex_list
EX_STACK_PATH := $(PWD)/ex_stack
EX_QUEUE_PATH := $(PWD)/ex_queue
EX_BITMAP_PATH := $(PWD)/ex_bitmap
EX_RB_TREE_PATH := $(PWD)/ex_rb_tree
EX_HASH_PATH := $(PWD)/ex_hash
EX_BIN_SEARCH_PATH := $(PWD)/ex_bin_search

all: format clean build check

build: ex_list ex_stack ex_queue ex_bitmap ex_rb_tree ex_hash ex_bin_search

check: ex_list_check ex_stack_check ex_queue_check ex_bitmap_check ex_rb_tree_check ex_hash_check ex_bin_search_check

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

ex_bitmap:
	@echo "\nBuild ex_bitmap..."
	$(MAKE) -C $(EX_BITMAP_PATH) kbuild

ex_bitmap_check:
	@echo "\nCheck ex_bitmap..."
	$(MAKE) -C $(EX_BITMAP_PATH) check

ex_rb_tree:
	@echo "\nBuild ex_rb_tree..."
	$(MAKE) -C $(EX_RB_TREE_PATH) kbuild

ex_rb_tree_check:
	@echo "\nCheck ex_rb_tree..."
	$(MAKE) -C $(EX_RB_TREE_PATH) check

ex_hash:
	@echo "\nBuild ex_hash..."
	$(MAKE) -C $(EX_HASH_PATH) kbuild

ex_hash_check:
	@echo "\nCheck ex_hash..."
	$(MAKE) -C $(EX_HASH_PATH) check

ex_bin_search:
	@echo "\nBuild ex_bin_search..."
	$(MAKE) -C $(EX_BIN_SEARCH_PATH) kbuild

ex_bin_search_check:
	@echo "\nCheck ex_bin_search..."
	$(MAKE) -C $(EX_BIN_SEARCH_PATH) check

format:
	@echo "\nFormating up..."
	$(MAKE) -C $(EX_LIST_PATH) format
	$(MAKE) -C $(EX_STACK_PATH) format
	$(MAKE) -C $(EX_QUEUE_PATH) format
	$(MAKE) -C $(EX_BITMAP_PATH) format
	$(MAKE) -C $(EX_RB_TREE_PATH) format
	$(MAKE) -C $(EX_HASH_PATH) format
	$(MAKE) -C $(EX_BIN_SEARCH_PATH) format

clean:
	@echo "\nCleaning up..."
	$(MAKE) -C $(EX_LIST_PATH) clean
	$(MAKE) -C $(EX_STACK_PATH) clean
	$(MAKE) -C $(EX_QUEUE_PATH) clean
	$(MAKE) -C $(EX_BITMAP_PATH) clean
	$(MAKE) -C $(EX_RB_TREE_PATH) clean
	$(MAKE) -C $(EX_HASH_PATH) clean
	$(MAKE) -C $(EX_BIN_SEARCH_PATH) clean

.PHONY: all build check format clean ex_list ex_list_check ex_stack ex_stack_check ex_queue ex_queue_check  ex_bitmap ex_bitmap_check ex_rb_tree ex_rb_tree_check ex_hash ex_hash_check ex_bin_search ex_bin_search_check
