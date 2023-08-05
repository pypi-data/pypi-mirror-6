#!/bin/bash
echo "Creating instance with AMI: $1. Instance could be accessed with key $2. Please wait..."
quantgo run-instances --image-id $1 --instance-type t1.micro --count 1 --key-name $2 --login-protocol ssh