MODULE_NAME := ex_get_page

PWD := $(shell pwd)
KERNEL_DIR := /lib/modules/$(shell uname -r)/build/
SRC_DIR := $(PWD)/src
TEST_DIR := $(PWD)/test
BUILD_DIR := $(PWD)/build
TEST_RESULT_DIR := $(TEST_DIR)/result

PY_TEST := $(shell whereis pytest | cut -d : -f2 | tr -d '^ \n')
CLANG_FORMAT := $(shell whereis clang-format | cut -d : -f2 | tr -d '^ \n')
INDENT := $(shell whereis indent | cut -d : -f2 | tr -d '^ \n')

$(shell mkdir -p $(BUILD_DIR))

kbuild:
	make -C $(KERNEL_DIR) M=$(PWD) modules
	@if [ -f $(SRC_DIR)/$(MODULE_NAME).ko ]; then \
		mv $(SRC_DIR)/$(MODULE_NAME).ko $(BUILD_DIR)/; \
	else \
		echo "Build error"; \
	fi

info: 
	@if [ -f $(BUILD_DIR)/$(MODULE_NAME).ko ]; then \
		sudo modinfo $(BUILD_DIR)/$(MODULE_NAME).ko; \
	else \
		echo "Build first"; \
	fi

format:
	@if [ -n "$(CLANG_FORMAT)" ]; then \
		clang-format -i $(SRC_DIR)/*.[ch]; \
	else \
		echo "clang-format no found"; \
	fi

indent-format:
	@if [ -n "$(INDENT)" ]; then \
		indent -kr -i8 -ts8 -sob -l80 -ss -bs -psl $(SRC_DIR)/*.[ch]; \
	else \
		echo "indent no found"; \
	fi

insmod:
	@if [ -f $(BUILD_DIR)/$(MODULE_NAME).ko ]; then \
		sudo insmod $(BUILD_DIR)/$(MODULE_NAME).ko; \
	else \
		echo "Build first"; \
	fi

rmmod:
	sudo rmmod $(MODULE_NAME) 2>/dev/null

check:
	@if [ -f $(BUILD_DIR)/$(MODULE_NAME).ko ]; then \
		mkdir -p $(TEST_RESULT_DIR); \
		if [ -n "$(PY_TEST)" ]; then \
			sudo pytest -v $(TEST_DIR)/check.py; \
		else \
			sudo python3 -m unittest -v $(TEST_DIR)/check.py; \
		fi; \
	else \
		echo "Build first"; \
	fi;

clean:
	make -C $(KERNEL_DIR) M=$(PWD) clean
	sudo rm -rf $(PWD)/build/
	sudo rm -rf $(PWD)/.pytest_cache/
	sudo rm -rf $(TEST_RESULT_DIR)
	sudo rm -rf $(TEST_DIR)/__pycache__/
	sudo rm -rf $(TEST_DIR)/modules/__pycache__/
	sudo rm -rf $(TEST_DIR)/tools/__pycache__/

.PHONY: kbuild info format insmod rmmod check clean 
