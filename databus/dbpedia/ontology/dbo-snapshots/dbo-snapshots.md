# DBpedia Ontology Snapshots
DBpedia Ontology snapshots in several serialization formats updated every 30 minutes if changes occured.

## Workflow
DBpedia Ontology snapshots are fetched from http://mappings.dbpedia.org/server/ontology/dbpedia.owl every 30 minutes but are published on the Databus and committed to the [DBpedia Ontology Github repository](https://github.com/dbpedia/ontology-tracker/ "DBpedia Ontology Github repository") if and only if changes in the ontology were detected.
The DBpedia Ontology and Mappings can be edited in the [mappings wiki](http://mappings.dbpedia.org/server/ontology/dbpedia.owl  "mappings wiki").
The Github repository contains the [Databus repo](https://github.com/dbpedia/ontology-tracker/tree/master/databus/dbpedia/ontology/dbo-snapshots "Databus repo") for publishing the ontology and therefore can be used to diff the changes between versions. The file `dbo-snapshots.dl` shows the changes of axioms while `dbo-snapshots.nt` is ideal for line-based diffs of the entire ontology since it is sorted (bytewise sort order).
The code for the service can be found [here](https://github.com/dbpedia/ontology-tracker/blob/master/databus/dbpedia/ontology/databus-ontology-diffbot.sh "databus-ontology-diffbot.sh").


## Artifact changelog
### 2019-08-27
introduced new 30 minute diff-based publishing approach
### 2019-02-21
Initial manual commit, deployment as chronjob pending

