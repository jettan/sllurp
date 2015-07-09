#!/bin/bash


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

./bin/reset 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 15  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log15_1.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 15  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log15_2.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 15  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log15_3.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 15  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log15_4.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 15  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log15_5.txt 192.168.10.102

./bin/reset 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 14  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log14_1.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 14  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log14_2.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 14  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log14_3.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 14  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log14_4.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 14  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log14_5.txt 192.168.10.102

./bin/reset 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 13  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log13_1.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 13  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log13_2.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 13  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log13_3.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 13  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log13_4.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 13  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log13_5.txt 192.168.10.102

./bin/reset 192.168.10.102

sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 12  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log12_1.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 12  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log12_2.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 12  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log12_3.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 12  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log12_4.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 12  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log12_5.txt 192.168.10.102

./bin/reset 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 11  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log11_1.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 11  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log11_2.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 11  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log11_3.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 11  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log11_4.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 11  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log11_5.txt 192.168.10.102

./bin/reset 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 10  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log10_1.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 10  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log10_2.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 10  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log10_3.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 10  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log10_4.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 10  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log10_5.txt 192.168.10.102

./bin/reset 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 9  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log9_1.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 9  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log9_2.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 9  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log9_3.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 9  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log9_4.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 9  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log9_5.txt 192.168.10.102

./bin/reset 192.168.10.102

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

./bin/reset 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 7  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log7_1.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 7  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log7_2.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 7  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log7_3.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 7  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log7_4.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 7  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log7_5.txt 192.168.10.102

./bin/reset 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 6  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log6_1.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 6  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log6_2.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 6  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log6_3.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 6  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log6_4.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 6  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log6_5.txt 192.168.10.102

./bin/reset 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 5  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log5_1.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 5  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log5_2.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 5  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log5_3.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 5  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log5_4.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 5  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log5_5.txt 192.168.10.102

./bin/reset 192.168.10.102

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

./bin/reset 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 3  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log3_1.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 3  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log3_2.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 3  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log3_3.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 3  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log3_4.txt 192.168.10.102
sleep 5
./bin/access -P 32 -w 1 -c 0xb105 -m 3  -f hex/simple2.hex -M WISP5 -T 6250 -n 200 -l log3_5.txt 192.168.10.102

./bin/reset 192.168.10.102
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

./bin/reset 192.168.10.102
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
