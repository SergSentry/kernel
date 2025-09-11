PWD := $(shell pwd)
DATE_TIME := $(shell date)

PROJECT_REPORT_FILE := report.md
TEST_REPORT_FILE := test_report.md

EX_KMALLOC_PATH := $(PWD)/ex_kmalloc
EX_KMALLOC_REPORT_PATH := $(EX_KMALLOC_PATH)/test/result/$(TEST_REPORT_FILE)
EX_VMALLOC_PATH := $(PWD)/ex_vmalloc
EX_VMALLOC_REPORT_PATH := $(EX_VMALLOC_PATH)/test/result/$(TEST_REPORT_FILE)
EX_KMEM_CACHE_PATH := $(PWD)/ex_kmem_cache
EX_KMEM_CACHE_REPORT_PATH := $(EX_KMEM_CACHE_PATH)/test/result/$(TEST_REPORT_FILE)
EX_MEMPOOL_PATH := $(PWD)/ex_mempool
EX_MEMPOOL_REPORT_PATH := $(EX_MEMPOOL_PATH)/test/result/$(TEST_REPORT_FILE)
EX_GET_PAGE_PATH := $(PWD)/ex_get_page
EX_GET_PAGE_REPORT_PATH := $(EX_GET_PAGE_PATH)/test/result/$(TEST_REPORT_FILE)

all: format clean build check

build: ex_kmalloc ex_vmalloc ex_kmem_cache ex_mempool ex_get_page

check: report_init ex_kmalloc_check ex_vmalloc_check ex_kmem_cache_check ex_mempool_check ex_get_page_check report_finish

ex_kmalloc:
	@echo "\nBuild ex_kmalloc..."
	$(MAKE) -C $(EX_KMALLOC_PATH) kbuild

ex_kmalloc_check:
	@echo "\nCheck ex_kmalloc..."
	$(MAKE) -C $(EX_KMALLOC_PATH) check

ex_vmalloc:
	@echo "\nBuild ex_vmalloc..."
	$(MAKE) -C $(EX_VMALLOC_PATH) kbuild

ex_vmalloc_check:
	@echo "\nCheck ex_vmalloc..."
	$(MAKE) -C $(EX_VMALLOC_PATH) check

ex_kmem_cache:
	@echo "\nBuild ex_kmem_cache..."
	$(MAKE) -C $(EX_KMEM_CACHE_PATH) kbuild

ex_kmem_cache_check:
	@echo "\nCheck ex_kmem_cache..."
	$(MAKE) -C $(EX_KMEM_CACHE_PATH) check

ex_mempool:
	@echo "\nBuild ex_mempool..."
	$(MAKE) -C $(EX_MEMPOOL_PATH) kbuild

ex_mempool_check:
	@echo "\nCheck ex_mempool..."
	$(MAKE) -C $(EX_MEMPOOL_PATH) check

ex_get_page:
	@echo "\nBuild ex_get_page..."
	$(MAKE) -C $(EX_GET_PAGE_PATH) kbuild

ex_get_page_check:
	@echo "\nCheck ex_get_page..."
	$(MAKE) -C $(EX_GET_PAGE_PATH) check

format:
	@echo "\nFormating up..."
	$(MAKE) -C $(EX_KMALLOC_PATH) format
	$(MAKE) -C $(EX_VMALLOC_PATH) format
	$(MAKE) -C $(EX_KMEM_CACHE_PATH) format
	$(MAKE) -C $(EX_MEMPOOL_PATH) format
	$(MAKE) -C $(EX_GET_PAGE_PATH) format

clean:
	@echo "\nCleaning up..."
	$(MAKE) -C $(EX_KMALLOC_PATH) clean
	$(MAKE) -C $(EX_VMALLOC_PATH) clean
	$(MAKE) -C $(EX_KMEM_CACHE_PATH) clean
	$(MAKE) -C $(EX_MEMPOOL_PATH) clean
	$(MAKE) -C $(EX_GET_PAGE_PATH) clean
	sudo rm -rf $(PWD)/$(PROJECT_REPORT_FILE)

report_init:
	@echo "\nReport init..."
	echo "## PROJECT REPORT\n" > $(PWD)/$(PROJECT_REPORT_FILE)
	echo "OTUS course homework hw_07_mem\n" >> $(PWD)/$(PROJECT_REPORT_FILE)
	echo "<br>\n" >> $(PWD)/$(PROJECT_REPORT_FILE)
	echo "### Memory info\n" >> $(PWD)/$(PROJECT_REPORT_FILE)
	cat /proc/meminfo | grep -e "^Mem[Total|Free]" | tr '\n' '@' | sed 's/@/\n\n/g' >> $(PWD)/$(PROJECT_REPORT_FILE)
	echo "<br>\n" >> $(PWD)/$(PROJECT_REPORT_FILE)
	echo "### Test results\n\n" >> $(PWD)/$(PROJECT_REPORT_FILE)


report_finish:
	@echo "\nReport assemble..."
	@if [ -f $(EX_KMALLOC_REPORT_PATH) ] && [ -r $(EX_KMALLOC_REPORT_PATH) ]; then \
		cat $(EX_KMALLOC_REPORT_PATH) >> $(PWD)/$(PROJECT_REPORT_FILE); \
	fi
	@if [ -f $(EX_VMALLOC_REPORT_PATH) ] && [ -r $(EX_VMALLOC_REPORT_PATH) ]; then \
		cat $(EX_VMALLOC_REPORT_PATH) >> $(PWD)/$(PROJECT_REPORT_FILE); \
	fi
	@if [ -f $(EX_KMEM_CACHE_REPORT_PATH) ] && [ -r $(EX_KMEM_CACHE_REPORT_PATH) ]; then \
		cat $(EX_KMEM_CACHE_REPORT_PATH) >> $(PWD)/$(PROJECT_REPORT_FILE); \
	fi
	@if [ -f $(EX_MEMPOOL_REPORT_PATH) ] && [ -r $(EX_MEMPOOL_REPORT_PATH) ]; then \
		cat $(EX_MEMPOOL_REPORT_PATH) >> $(PWD)/$(PROJECT_REPORT_FILE); \
	fi
	@if [ -f $(EX_GET_PAGE_REPORT_PATH) ] && [  -r $(EX_GET_PAGE_REPORT_PATH) ]; then \
		cat $(EX_GET_PAGE_REPORT_PATH) >> $(PWD)/$(PROJECT_REPORT_FILE); \
	fi
	echo "\n<br>\n" >> $(PWD)/$(PROJECT_REPORT_FILE)
	echo "\n---\n$(DATE_TIME)\n" >> $(PWD)/$(PROJECT_REPORT_FILE)
	@echo "\nDone\n"

.PHONY: all build check format clean ex_kmalloc ex_kmalloc_check ex_vmalloc ex_vmalloc_check ex_kmem_cache ex_kmem_cache_check ex_mempool ex_mempool_check ex_get_page ex_get_page_check
