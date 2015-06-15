#!/bin/bash


# Payloadsize: 16
# OperationCountValue: hardcoded
./bin/reset 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 16  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log16_1.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 16  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log16_2.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 16  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log16_3.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 16  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log16_4.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 16  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log16_5.txt 192.168.10.102

sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 8  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log8_1.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 8  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log8_2.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 8  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log8_3.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 8  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log8_4.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 8  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log8_5.txt 192.168.10.102

sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 4  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log4_1.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 4  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log4_2.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 4  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log4_3.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 4  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log4_4.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 4  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log4_5.txt 192.168.10.102

sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 2  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log2_1.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 2  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log2_2.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 2  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log2_3.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 2  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log2_4.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 2  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log2_5.txt 192.168.10.102

sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 1  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log1_1.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 1  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log1_2.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 1  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log1_3.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 1  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log1_4.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 1  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log1_5.txt 192.168.10.102
