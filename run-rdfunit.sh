#!/bin/bash

(cd ./RDFUnit && ./bin/rdfunit -A -d ../../ontology/dbpedia_2016-10.owl -s dbo -r extended)
exit 0
