#!/bin/bash
instances=`quantgo describe-instances | jq .Message.InstanceIds[] | awk -vORS=\  '{ print $1 }' | sed "s/\"//g"`
echo "Stopping instances $instances. Please wait..."
echo "$instances" | xargs quantgo stop-instances --instance-ids