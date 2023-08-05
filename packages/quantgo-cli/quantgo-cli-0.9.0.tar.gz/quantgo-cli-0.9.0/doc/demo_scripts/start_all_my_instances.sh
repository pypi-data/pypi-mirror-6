#!/bin/bash
instances=`quantgo describe-instances | jq .Message.InstanceIds[] | awk -vORS=\  '{ print $1 }' | sed "s/\"//g"`
echo "Starting instances $instances. Please wait..."
echo "$instances" | xargs quantgo start-instances --instance-ids
