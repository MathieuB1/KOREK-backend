#!/bin/bash

HOSTNAME="${COLLECTD_HOSTNAME:-`hostname -f`}"
INTERVAL_VALUE=10
INTERVAL="${COLLECTD_INTERVAL:-$INTERVAL_VALUE}"

mkdir -p /var/log/nginx/
touch /var/log/nginx/requests.log

while sleep "$INTERVAL"
do

# Loop on all nginx instances
> /var/log/nginx/requests.log
for i in $(docker ps | grep _nginx_ | awk '{print $NF}')
do
  echo -e "$(docker logs --since ${INTERVAL_VALUE}s "${i}")" >> /var/log/nginx/requests.log
done

# Send to influxdb
log=""
while read p; do
	if [ ! -z "$p" ]
	then
		log=$(echo $p | sed 's/[^a-zA-Z0-9\.:/]/_/g' | awk '{print "nginx_logs,log="$0" value=1 "}')
		log_for_influx=$log$(date +%s%N)
		curl -i -s -XPOST 'http://influxdb:8086/write?db=collectd' --data-binary "$log_for_influx" &> /dev/null
	fi
done </var/log/nginx/requests.log

done