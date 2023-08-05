#!/bin/bash
res=`quantgo create-keypair --key-name $1`
key_name=`echo "$res" | jq .Message.KeyName | sed "s/\"//g"`
key_material=`echo "$res" | jq .Message.KeyMaterial | sed "s/\"//g"`
echo "Saving created key $key_name in file ${key_name}.pem"
echo "$key_material" > ${key_name}.pem
echo "Setting access permissions to key ${key_name}.pem as 600."
chmod 600 ${key_name}.pem