#!/bin/sh

#echo "payload,messages_sent,messages_resent,resend_ratio,success_reports,total_reports,efficiency,success_opm,total_opm,runtime,time_per_message,messages_per_second,time_per_op,success_ops,total_ops,goodput,throughput" > result.csv
echo "payload, total, success, efficiency, throughput, ops" >> result.csv
for f in *.txt; do ../../../postprocess.py $f >> result.csv; done
