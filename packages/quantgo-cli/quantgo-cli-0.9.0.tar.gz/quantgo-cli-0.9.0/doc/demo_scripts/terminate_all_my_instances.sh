#!/bin/bash
instances=`quantgo describe-instances | jq .Message.InstanceIds[] | awk -vORS=\  '{ print $1 }' | sed "s/\"//g"`
echo "Terminating instances $instances. Please wait..."
echo "$instances" | xargs quantgo terminate-instances --instance-ids
