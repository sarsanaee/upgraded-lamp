#!/bin/bash
cd /var/log/uwsgi/upgraded-lamp/
rm /var/www/data/*
count=`ls -l | grep -v ^l | wc -l`
file=farm_uwsgi.log.${count}
cat farm_uwsgi.log > ${file}
gzip ${file}
mv ${file}.gz latest_log.gz
cp latest_log.gz /var/www/data
if [ $1 == "truncate" ]; then
truncate -s 0 farm_uwsgi.log
fi
