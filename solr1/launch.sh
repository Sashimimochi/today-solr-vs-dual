#!/bin/bash

#set -eu

launch() {
    docker-compose up -d
    while [ `curl -LI http://localhost:8983/solr -o /dev/null -w '%{http_code}\n' -s` -ne 200 ]; do
        sleep 30 # wait launch services
    done
}

# Solrのコレクション作成
create_collection() {
    if [ `curl -LI "http://localhost:8983/solr/$1/admin/ping?distrib=true" -o /dev/null -w '%{http_code}\n' -s` -ne 200 ]; then
        docker-compose exec solr_node1 server/scripts/cloud-scripts/zkcli.sh -zkhost zookeeper1:2181 -cmd upconfig -confdir /opt/solr/server/solr/configsets/$1/conf -confname $1_conf
        curl "http://localhost:8983/solr/admin/collections?action=CREATE&name=$1&collection.configName=$1_conf&numShards=$2&replicationFactor=1&maxShardsPerNode=$2"
    fi
}

launch
create_collection basic 1
create_collection mini 1
