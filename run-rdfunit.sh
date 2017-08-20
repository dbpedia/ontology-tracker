#!/bin/bash

OUTPUT="$(cd ./RDFUnit && ./bin/rdfunit -A -d https://rawgit.com/gcpdev/ontology-tracker/master/ontology/dbpedia_2016-10.owl -s dbo -r extended 2>&1)"
FAIL=$(echo "$OUTPUT" | grep "Tests run" | cut -d ',' -f2 | tr -dc '0-9')
echo $FAIL;
if [ $FAIL = 0 ]; then
  exit 0
else
  exit 1
fi
