Demo Scripts Readme
===================

List of demo scripts:

* create_key_pair.sh - allows to create key pair and save key to file. Example: `./create_key_pair.sh myKey`
* create_linux_instance.sh - creates linux instance based on ami which is passed as first argument and key that must be passed as second argument. Example: `./create_linux_instance.sh ami-9b85eef2 mykey`
* describe_my_instances.sh - displays information about all user instances. Example: `./describe_my_instances.sh`
* get_login_information_for_my_instances.sh - returns information aboud port forwarding for all user instances. Example: `./get_login_information_for_my_instances.sh`
* start_all_my_instances.sh - starts all stopped user instances. Example: `./start_all_my_instances.sh`
* stop_all_my_instances.sh - stops all started user instances. Example: `./stop_all_my_instances.sh`
* terminate_all_my_instances.sh - terminates all user instances if they are stopped. Example: `./terminate_all_my_instances.sh`