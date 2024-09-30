#!/bin/bash

kill_rds_utils() {
    for H in localhost $REMHOST; do
	ssh $H killall -q rds-stress > /dev/null 2>&1
	ssh $H killall -q rds-ping   > /dev/null 2>&1
    done
}

unload_load_rds() {
    for H in $UNLOAD_HOSTS; do
	ssh $H "sudo rmmod rds_tcp; sudo rmmod rds; sudo modprobe rds_tcp"
    done
}

while getopts l:r:R: c; do
    case $c in
        l)  LIP=$OPTARG;;
        r)  RIP=$OPTARG;;
        R)  REMHOST=$OPTARG;;
  esac
done

FAILURES=0

for UNLOAD_HOSTS in "localhost $REMHOST" localhost "localhost $REMHOST" $REMHOST localhost $REMHOST; do
    TEST="rds-stress between $LIP to $RIP unloading on: \"$UNLOAD_HOSTS\""
    printf "%-80s: " "$TEST"

    kill_rds_utils
    unload_load_rds
    # Avoid rds-ping returning error if exec too early after modprobe
    sleep 5

    ssh -n $REMHOST "rds-stress -r $RIP >> /var/tmp/out 2>> /var/tmp/err" &
    PID=$!
    sleep 2;
    rds-stress -s $RIP -r $LIP -t 16 -d 4 -q 8448 -v -T 4 >> /var/tmp/out 2>> /var/tmp/err
    STS=$?

    STS2=$(jobs -l)
    while echo $STS2 | grep -q Running; do
	STS2=$(jobs -l)
    done

    FAILED=0
    if [ $STS != 0 ]; then
	echo -n 'FAILED (local rds-stress exited with status ' $STS
	FAILED=1
    fi
    if echo $STS2 | grep -q "Exit"; then
	    set $STS2
	if [ $FAILED == 0 ]; then
	    echo -n 'FAILED (remote rds-stress exited with status ' $4
	else
	    echo -n ', remote rds-stress exited with status ' $4
	fi
	FAILED=1
    fi

    N=$(rds-info -T | grep -c $LIP)
    if [ $N != 8 ]; then
        if [ $FAILED = 0 ]; then
            echo 'FAILED (Do not see 8 RDS TCP lanes)'
        else
            echo ', Do not see 8 RDS TCP lanes)'
        fi
    else
        if [ $FAILED = 0 ]; then
            echo PASSED
        else
            echo ')'
        fi
    fi
done


exit




for UNLOAD_HOSTS in "localhost $REMHOST" localhost "localhost $REMHOST" $REMHOST localhost $REMHOST; do
    TEST="rds-ping from $LIP to $RIP unloading on: \"$UNLOAD_HOSTS\""
    printf "%-80s: " "$TEST"

    kill_rds_utils
    unload_load_rds
    # Avoid rds-ping returning error if exec too early after modprobe
    sleep 5

    rds-ping -I $LIP -c 1 $RIP > /dev/null 2>&1 &
    PID=$!
    sleep 10
    RES=$(jobs -l) > /dev/null 2>&1
    FAILED=0
    if echo "$RES" | grep -q "Running" ; then
	echo -n 'FAILED (rds-ping is hanging'
	FAILED=1
    elif echo "$RES" | grep -q "Exit" ; then
	set $RES
	echo -n 'FAILED (rds-ping error exited with ' $4
	FAILED=1
    fi
    kill $PID 2> /dev/null
    wait $PID 2> /dev/null
    N=$(rds-info -T | grep -c $LIP)
    if [ $N != 8 ]; then
	if [ $FAILED = 0 ]; then
	    echo 'FAILED (Do not see 8 RDS TCP lanes)'
	else
	    echo ', Do not see 8 RDS TCP lanes)'
	fi
    else
	if [ $FAILED = 0 ]; then
	    echo PASSED
	else
	    echo ')'
	fi
    fi

    if [ $FAILED != 0 ]; then
	FAILURES=1;
    fi
done

exit $FAILURES


