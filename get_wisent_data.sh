#!/bin/bash


./bin/reset 192.168.10.102
sleep 5

for i in {16..1}; do
	for j in {1..5}; do
		./bin/wisent -f hex/test_${i}.hex -l log${i}_${j}.txt 192.168.10.102
		sleep 5
	done
	./bin/reset 192.168.10.102
	sleep 5
done
