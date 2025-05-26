MODULE_NAME := hello

PWD := $(shell pwd)
KERNEL_DIR := /lib/modules/$(shell uname -r)/build/
SRC_DIR := $(PWD)/src
TEST_DIR := $(PWD)/test
BUILD_DIR := $(PWD)/build


$(shell mkdir -p $(BUILD_DIR))

kbuild:
	make -C $(KERNEL_DIR) M=$(PWD) modules
	mv $(SRC_DIR)/$(MODULE_NAME).ko $(BUILD_DIR)/
info: 
	@if [ -f $(BUILD_DIR)/$(MODULE_NAME).ko ]; then \
		sudo modinfo $(BUILD_DIR)/$(MODULE_NAME).ko; \
	else \
		echo "Build first"; \
	fi
format:
	clang-format -i $(SRC_DIR)/*.[ch]
indent-format:
	indent -kr -i8 -ts8 -sob -l80 -ss -bs -psl $(SRC_DIR)/*.[ch]
insmod:
	sudo insmod $(BUILD_DIR)/$(MODULE_NAME).ko
rmmod:
	sudo rmmod $(MODULE_NAME)
check:
	sudo pytest -v $(TEST_DIR)/check.py
clean:
	make -C $(KERNEL_DIR) M=$(PWD) clean
	sudo rm -rf $(TEST_DIR)/__pycache__/
	sudo rm -rf $(TEST_DIR)/modules/__pycache__/
	sudo rm -rf $(TEST_DIR)/tools/__pycache__/

.PHONY: kbuild info format insmod rmmod check clean 
