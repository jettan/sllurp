#!/bin/bash

echo "Number of firmwares flashed:"
cat log.txt | grep "Words to send" | wc -l
echo "Time elapsed: (sorted)"
cat log.txt | grep "EOF" | sort -n
echo "Tags seen per flash session:"
cat log.txt | grep "total #" | sort -n
