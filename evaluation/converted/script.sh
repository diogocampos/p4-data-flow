#!/bin/bash

files=$@

for i in $(echo $files); do
  echo "processing $i..."
  python3.7 ~/p4-data-flow/p4df.py -d -s $i > $i.nodrop.simple.txt 2> $i.err;
  #python3.7 ~/p4-data-flow/p4df.py -g $i > $i.graph.txt 2> $i.err;
  #python3.7 ~/p4-data-flow/p4df.py -v $i > $i.verbose.txt 2>> $i.err;
  #python3.7 ~/p4-data-flow/p4df.py -s $i > $i.simple.txt 2>> $i.err;
  #python3.7 ~/p4-data-flow/p4df.py $i > $i.full.txt 2>> $i.err;
done
