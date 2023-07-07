#!/bin/bash

function func() {
  echo -n " finishing"
  for container in $(docker stats --all --no-stream --format {{.Name}})
  do
    echo "TIMESTAMP,CONTAINER ID,NAME,CPU %,MEM USAGE / LIMIT,MEM %,NET I/O,BLOCK I/O,PIDS" > $dir/$container.csv
    cat $dir/$CSV_FILE | grep $container >> $dir/$container.csv
    echo -n "."
  done

  status=$?
  echo "done!"
  echo "stats saved $(pwd)/$dir"
  exit $status
}

trap 'func' 1 2 3 15

dir=stats_$(date "+%Y-%m%d-%H%M-%S")
mkdir $dir
CSV_FILE=stats-all.csv

echo "TIMESTAMP,CONTAINER ID,NAME,CPU %,MEM USAGE / LIMIT,MEM %,NET I/O,BLOCK I/O,PIDS" > $dir/$CSV_FILE
while true
do
  docker stats --all --no-stream --format "$(date "+%H:%M:%S"),{{.ID}},{{.Name}},{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}},{{.NetIO}},{{.BlockIO}},{{.PIDs}}" >> $dir/$CSV_FILE
done
