#! /usr/bin/bash

SRC_PATH=$1
if [ ! -d $SRC_PATH ]; then
    SRC_PATH=$PWD
else
   SRC_PATH=$PWD$SRC_PATH
fi

echo "Script source path: $SRC_PATH"
echo "Script app path: $SRC_PATH/scripts/config"

set -e

$SRC_PATH/scripts/config --set-str LOCALVERSION -otus-dev

$SRC_PATH/scripts/config -d SECURITY_SELINUX
$SRC_PATH/scripts/config -d SECURITY_SMACK
$SRC_PATH/scripts/config -d SECURITY_TOMOYO
$SRC_PATH/scripts/config -d SECURITY_APPARMOR
$SRC_PATH/scripts/config -d SECURITY_YAMA

$SRC_PATH/scripts/config -d RANDOMIZE_BASE

$SRC_PATH/scripts/config -d CPU_MITIGATIONS
$SRC_PATH/scripts/config -d MITIGATION_SPECTRE_BHI
$SRC_PATH/scripts/config -d MITIGATION_RFDS
$SRC_PATH/scripts/config -d PAGE_TABLE_ISOLATION
$SRC_PATH/scripts/config -d ZSWAP

#Uncomment it if no needs EBPF
#$SRC_PATH/scripts/config -d BPF
#$SRC_PATH/scripts/config -d BPF_SYSCALL
#$SRC_PATH/scripts/config -d EBPF_JIT
#$SRC_PATH/scripts/config -d BPF_EVENTS
#$SRC_PATH/scripts/config -d BPFILTER

#By default is On
#$SRC_PATH/scripts/config -e DEBUG_FS
#$SRC_PATH/scripts/config -e FTRACE
#$SRC_PATH/scripts/config -e FUNCTION_TRACER
#$SRC_PATH/scripts/config -e DYNAMIC_FTRACE
#$SRC_PATH/scripts/config -e FUNCTION_GRAPH_TRACER
#$SRC_PATH/scripts/config -e STACK_TRACER

$SRC_PATH/scripts/config -e KUNIT
$SRC_PATH/scripts/config -e KUNIT_TEST

$SRC_PATH/scripts/config -e KASAN
$SRC_PATH/scripts/config -e STACKTRACE
$SRC_PATH/scripts/config -e KASAN_GENERIC
$SRC_PATH/scripts/config -e KASAN_INLINE
$SRC_PATH/scripts/config -e KASAN_EXTRA_INFO

$SRC_PATH/scripts/config -e KGDB
$SRC_PATH/scripts/config -e KGDB_SERIAL_CONSOLE
$SRC_PATH/scripts/config -e DEBUG_INFO
$SRC_PATH/scripts/config -e SERIAL_CONSOLE
$SRC_PATH/scripts/config -e CONSOLE_POLL

$SRC_PATH/scripts/config -e KPROBES
$SRC_PATH/scripts/config -e KPROBE_EVENTS

echo "complete"
