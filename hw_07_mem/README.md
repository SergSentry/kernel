# Linux Kernel Development
OTUS course  homework "Linux Kernel Development"


<br>
<br>

## HW_07_mem

### Домашнее задание

Написать модули ядра с использованием kmem_cache и mempool. Написать модули ядра с использованием различных malloc и показать их отличия

#### Цель:

Написать модули ядра, использующие механизмы управления памятью (kmem_cache, mempool, kmalloc/vmalloc);
Написать демонстрационные модули, сравнивающий kmalloc, vmalloc и kmem_cache, mempool, get_page.

Необходимо написать модули:

* ex_kmalloc.ko

* ex_vmalloc.ko

* ex_kmem_cache.ko

* ex_mempool.ko

* ex_get_page.ko

Каждый модуль должен перед аллокацией выводить сообщение в dmesg в формате:

> "kmalloc: %d byte\n",

> "kmalloc: SUCCSESS\n" или "kmalloc: FAIL , err_msg = %s\n"

Если удалось выделить, то

> "kmalloc: %d byte, %d ms, type: %s\n"
