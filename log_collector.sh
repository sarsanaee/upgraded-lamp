#!/bin/bash
cd /var/log/uwsgi/upgraded-lamp/
rm /var/www/data/*
count=`ls -l | grep -v ^l | wc -l`
file=farm_uwsgi.log.${count}
cat farm_uwsgi.log > ${file}
gzip ${file}
cp ${file}.gz /var/www/data
mv /var/www/data/${file}.gz latest_log.gz
truncate -s 0 farm_uwsgi.log