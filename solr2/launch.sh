#!/bin/bash

set -eu

create_log_dir() {
  LOG_DIR=./solr/logs/
  if [ ! -d $LOG_DIR ]; then
    mkdir -p $LOG_DIR
    sudo chmod 777 $LOG_DIR
  fi
}

launch() {
    create_log_dir
    docker-compose up -d
    while [ `curl -LI http://localhost:8984/solr -o /dev/null -w '%{http_code}\n' -s` -ne 200 ]; do
        sleep 30 # wait launch services
    done
}

create_collection() {
    if [ `curl -LI "http://localhost:8984/solr/$1/admin/ping?distrib=true" -o /dev/null -w '%{http_code}\n' -s` -ne 200 ]; then
        docker-compose exec solr_node2 server/scripts/cloud-scripts/zkcli.sh -zkhost zookeeper2:2181 -cmd upconfig -confdir /opt/solr/server/solr/configsets/$1/conf -confname $1_conf
        curl "http://localhost:8984/solr/admin/collections?action=CREATE&name=$1&collection.configName=$1_conf&numShards=$2&replicationFactor=1&maxShardsPerNode=$2"
    fi
}

launch
create_collection basic2 1
create_collection mini_dual 1
