#!/usr/bin/env bash
#
# DBpedia Ontology commit bot by Gustavo Publio

# Get version based on datetime
VERSION=`date -u "+%Y-%m-%dT%H:00:00Z"` #:%M:%SZ"`

# URL to download the ontology
URL="http://mappings.dbpedia.org/server/ontology/dbpedia.owl"

##########################
# build the latest version
##########################
mkdir -p /tmp/dbo-snapshots/$VERSION

# get current version
wget -q -O /tmp/dbo-snapshots/$VERSION/dbo.owl $URL
# get DL Axioms
java -cp DisplayAxioms.jar DisplayAxioms /tmp/dbo-snapshots/$VERSION/dbo.owl | LC_ALL=C sort -u > /tmp/dbo-snapshots/$VERSION/dbo.dl
# get ntriples
rapper -i rdfxml -o ntriples /tmp/dbo-snapshots/$VERSION/dbo.owl | ascii2uni -a U | LC_ALL=C sort -u > /tmp/dbo-snapshots/$VERSION/dbo.nt




exit

YEAR=`date "+%Y"`
MONTH=`date "+%m"`
DAY=`date "+%d"`

INFO="Commit: $(date)"


# clean previous version
cd ~/ontology-tracker/ontology && rm -Rf ./*.owl ./*.ttl

# get today's version
wget -q -O ~/ontology-tracker/ontology/ontology.owl $URL

# print an initial line containing the commit ID and the rest of the file as Turtle
{
	printf "# This version was published on: $YEAR.$MONTH.$DAY\n# Commit \$Id$\n"
	rapper -q -i rdfxml -o turtle ~/ontology-tracker/ontology/ontology.owl
} > ~/ontology-tracker/ontology/ontology.ttl

# generate datasets
cd ~/ontology-tracker/release/deploy && mvn versions:set -DnewVersion=$YEAR.$MONTH.$DAY && mvn databus:metadata && mvn databus:package-export

# rename
cd ~/ontology-tracker/release/ontology/$YEAR.$MONTH.$DAY/

# commit it
cd ~/ontology-tracker/
git add --all
git commit -m "$INFO"
git push origin master

# publish in databus
cd ~/ontology-tracker/release/deploy && mvn databus:deploy
