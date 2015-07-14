#!/bin/bash

./bin/reset 192.168.10.102
sleep 5

for j in {1..32}; do
	for i in {1..5}; do
		./bin/access -P 32 -M WISP5 -n 200 -w $j -l "log_${j}_${i}.txt" 192.168.10.102 && sleep 3
	done
	
	./bin/reset 192.168.10.102
	sleep 5
done
