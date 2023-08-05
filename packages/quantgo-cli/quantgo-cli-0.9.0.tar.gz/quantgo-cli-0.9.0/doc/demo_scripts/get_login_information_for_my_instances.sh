#!/bin/bash
instances=`quantgo describe-instances | jq .Message.InstanceIds[]`
for instance_id in $instances
do
    echo "--------------------------------------------------------"
    echo "|     Login Information For Instance $instance_id      |"
    echo "--------------------------------------------------------"
    echo "$instance_id" |  xargs quantgo get-login-ports --instance-id
done