PWD := $(shell pwd)

EX_TIMER_PATH := $(PWD)/ex_timer
EX_HRTIMER_PATH := $(PWD)/ex_hrtimer


all: format clean build check

build: ex_timer ex_hrtimer

check: ex_timer_check ex_hrtimer_check

ex_timer:
	@echo "\nBuild ex_timer..."
	$(MAKE) -C $(EX_TIMER_PATH) kbuild

ex_timer_check:
	@echo "\nCheck ex_timer..."
	$(MAKE) -C $(EX_TIMER_PATH) check

ex_hrtimer:
	@echo "\nBuild ex_hrtimer..."
	$(MAKE) -C $(EX_HRTIMER_PATH) kbuild

ex_hrtimer_check:
	@echo "\nCheck ex_hrtimer..."
	$(MAKE) -C $(EX_HRTIMER_PATH) check

format:
	@echo "\nFormating up..."
	$(MAKE) -C $(EX_TIMER_PATH) format
	$(MAKE) -C $(EX_HRTIMER_PATH) format

clean:
	@echo "\nCleaning up..."
	$(MAKE) -C $(EX_TIMER_PATH) clean
	$(MAKE) -C $(EX_HRTIMER_PATH) clean

.PHONY: all build check format clean ex_timer ex_timer_check ex_hrtimer ex_hrtimer_check
