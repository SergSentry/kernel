SRC_DIR := ./
CLANG_FORMAT := $(shell whereis clang-format | cut -d : -f2 | tr -d '^ \n')
INDENT := $(shell whereis indent | cut -d : -f2 | tr -d '^ \n')

all: basic

basic:
	gcc -I../../module/src/include basic.c -o basic
	strip basic

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

clean:
	rm -rf basic

.PHONY: basic clean
