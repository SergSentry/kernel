PWD := $(shell pwd)

EX_MUTEX_PATH := $(PWD)/ex_mutex
EX_SPINLOCK_PATH := $(PWD)/ex_spinlock
EX_SEMAPHORE_PATH := $(PWD)/ex_semaphore
EX_RWLOCK_PATH := $(PWD)/ex_rwlock
EX_WAITER_PATH := $(PWD)/ex_waiter


all: format clean build check

build: ex_mutex ex_spinlock ex_semaphore ex_rwlock ex_waiter

check: ex_mutex_check ex_spinlock_check ex_semaphore_check ex_rwlock_check ex_waiter_check

ex_mutex:
	@echo "\nBuild ex_mutex..."
	$(MAKE) -C $(EX_MUTEX_PATH) kbuild

ex_mutex_check:
	@echo "\nCheck ex_mutex..."
	$(MAKE) -C $(EX_MUTEX_PATH) check

ex_spinlock:
	@echo "\nBuild ex_spinlock..."
	$(MAKE) -C $(EX_SPINLOCK_PATH) kbuild

ex_spinlock_check:
	@echo "\nCheck ex_spinlock..."
	$(MAKE) -C $(EX_SPINLOCK_PATH) check

ex_semaphore:
	@echo "\nBuild ex_semaphore..."
	$(MAKE) -C $(EX_SEMAPHORE_PATH) kbuild

ex_semaphore_check:
	@echo "\nCheck ex_semaphore..."
	$(MAKE) -C $(EX_SEMAPHORE_PATH) check

ex_rwlock:
	@echo "\nBuild ex_rwlock..."
	$(MAKE) -C $(EX_RWLOCK_PATH) kbuild

ex_rwlock_check:
	@echo "\nCheck ex_rwlock..."
	$(MAKE) -C $(EX_RWLOCK_PATH) check

ex_waiter:
	@echo "\nBuild ex_waiter..."
	$(MAKE) -C $(EX_WAITER_PATH) kbuild

ex_waiter_check:
	@echo "\nCheck ex_waiter..."
	$(MAKE) -C $(EX_WAITER_PATH) check


format:
	@echo "\nFormating up..."
	$(MAKE) -C $(EX_MUTEX_PATH) format
	$(MAKE) -C $(EX_SPINLOCK_PATH) format
	$(MAKE) -C $(EX_SEMAPHORE_PATH) format
	$(MAKE) -C $(EX_RWLOCK_PATH) format
	$(MAKE) -C $(EX_WAITER_PATH) format

clean:
	@echo "\nCleaning up..."
	$(MAKE) -C $(EX_MUTEX_PATH) clean
	$(MAKE) -C $(EX_SPINLOCK_PATH) clean
	$(MAKE) -C $(EX_SEMAPHORE_PATH) clean
	$(MAKE) -C $(EX_RWLOCK_PATH) clean
	$(MAKE) -C $(EX_WAITER_PATH) clean

.PHONY: all build check format clean ex_mutex ex_mutex_check ex_spinlock ex_spinlock_check ex_semaphore ex_semaphore_check  ex_rwlock ex_rwlock_check ex_waiter ex_waiter_check
