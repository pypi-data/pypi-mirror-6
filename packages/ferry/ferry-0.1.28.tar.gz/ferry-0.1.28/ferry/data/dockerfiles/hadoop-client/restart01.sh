#!/bin/bash

# Make sure we get the env variables in place. 
source /etc/profile
source /service/sbin/pophosts

pophosts
if [ $1 == "gluster" ]; then 
    sleep 3
	python /service/scripts/mounthelper.py mount $2  >> /tmp/gluster.log
	chown -R ferry:docker /service/data
	echo "Restart Gluster" >> /tmp/gluster.log
fi