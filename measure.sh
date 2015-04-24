#!/bin/bash

set -o verbose
timeout 10 ./bin/access -w ${1} -M WISP5 -T 6250 -n 200 -l log.txt 192.168.10.102

cat log.txt | grep "NumWordsWritten': ${1}" | wc -l
mv log.txt "results/bwr_70cm_log_${1}.txt"
