#!/bin/bash


./bin/reset 192.168.10.102
sleep 5

for i in {16..1}; do
	for j in {1..5}; do
		./bin/access -P 32 -w 1 -c 0xb105 -m ${i}  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log${i}_${j}.txt 192.168.10.102
		sleep 5
	done
	./bin/reset 192.168.10.102
	sleep 5
done
