#!/bin/bash
cd /var/log/uwsgi/upgraded-lamp/
count=`ls -l | grep -v ^l | wc -l`
file=farm_uwsgi.log.${count}
cat farm_uwsgi.log > ${file}
truncate -s 0 farm_uwsgi.log
gzip ${file}
cp * /var/www/data
