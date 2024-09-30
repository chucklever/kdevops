#!/bin/bash

trap cleanup EXIT

reset_pid=-1
local_ip=0
remote_ip=0
duration=30
wait_for_connection=0
rds_port=16385

cleanup()
{
	[[ "$reset_pid" == -1 ]] || kill -9 "$reset_pid"
}

start_connection_reset()
{
	while true
	do
		sleep 10
		ss -Kt "( sport =  :"$rds_port"  or  dport  =  :"$rds_port"  )" > /dev/null 2>&1
	done
}

run_test()
{
	if (( wait_for_connection ))
	then
		iptables -F; rds-stress --use-cong-monitor=1 -r $local_ip -t 32 -d 32 \
			-q 8448 -T $duration
	else
		iptables -F; rds-stress --use-cong-monitor=1 -r $local_ip -s $remote_ip \
			-t 32 -d 32 -q 8448 -T $duration
	fi
	return $?
}

usage()
{
	echo "Usage: $(basename $0) 
		-l local_ip_addr
		-r remote_ip_addr
		-c count
		[-w -- for server]"
	exit 1
}

while getopts 'hwWc:C:l:L:r:R:' opt
do
	case "$opt" in
		c | C)
			count="$OPTARG"
			;;
		l | L)
			local_ip="$OPTARG"
			echo "Local IP $local_ip"
			;;
		r | R)
			remote_ip="$OPTARG"
			echo "Remote $remote_ip"
			;;
		w | W)
			wait_for_connection=1
			;;
		h | ?)
			usage
			;;
	esac
done

if [[ -z $local_ip ]] || [[ -z $remote_ip ]] || [[ $count -eq 0 ]]
then
	usage
fi

##start_connection_reset &
##reset_pid=$!
modprobe rds_tcp
while (( count > 0 ))
do
modprobe rds_tcp
let count=count-1
if (( ! wait_for_connection ))
then
	sleep 10
fi
run_test
rds_ret=$?
if [[ $rds_ret -ne 0 ]]
then
	echo "FAILED"
	exit $rds_ret
else
	echo "PASSED"
fi

modprobe -r rds_tcp
done

exit $rds_ret
