## PROJECT REPORT

OTUS course homework hw_07_mem

<br>

### Memory info

MemTotal:       16314896 kB

MemFree:         8743560 kB

<br>

### Test results


#### Report for ex_kmalloc.ko with kmalloc allocator.
> kmalloc: 4194303 byte, 232449 ms, type: CONTINUOUS

#### Report for ex_vmalloc.ko with vmalloc allocator.
> vmalloc: 8589934591 byte, 518080 ms, type: CONTINUOUS

#### Report for ex_kmem_cache.ko with kmem_cache allocator.
> kmem_cache: 4194304 byte, 322 ms, type: NOT CONTINUOUS

#### Report for ex_mempool with kmalloc allocator.
> mempool: 4194303 byte, 265 ms, type: CONTINUOUS

#### Report for ex_mempool.ko with mempool allocator.
> mempool: 4194304 byte, 280 ms, type: NOT CONTINUOUS

#### Report for ex_get_page.ko with many pages allocator.
> get_page: 8388608 byte, 3 ms, type: NOT CONTINUOUS

#### Report for ex_get_page.ko with one pager allocator.
> get_page: 4194304 byte, 197 ms, type: NOT CONTINUOUS


<br>


---
Thu Sep 11 09:21:21 PM MSK 2025

