#! /bin/bash

checkDiff() {
old_file=$1
new_file=$2

regex_pattern="<http:\/\/dbpedia\.org\/ontology\/> <http:\/\/purl\.org\/dc\/terms\/modified> \".*\" \."

diff_output=$(LC_ALL=C comm -3 $old_file $new_file)

is_equal=0

while read line; do
        if ! [[ "$line" =~ $regex_pattern ]]
        then
                is_equal=1
                break
        fi
done <<<$diff_output
}

commitAndRelease() {

# Handling the git process
git add --all
git commit -m "$data_commit_info"
git push

# Releasing the new Version to maven
last_commit=$(git rev-parse HEAD)
dataId_commit_info="dataId for the release on $(date), Commit-Hash:${last_commit}"
cd $pomdir
mvn versions:set -DnewVersion=$last_commit
mvn deploy
	
# Commiting the new dataId to github
git add --all
git commit -m "$dataId_commit_info"
git push
}

pomdir=$1
startdir=$PWD

mkdir -p ./tmp/

data_commit_info="New ontology version on $(date)."

# Downloads the DBpedia-Ontology from http://mappings.dbpedia.org/server/ontology/dbpedia.owl
wget -O ./tmp/dbo-snapshots.owl http://mappings.dbpedia.org/server/ontology/dbpedia.owl

rapper -i rdfxml -o ntriples ./tmp/dbo-snapshots.owl | LC_ALL=C sort -u > ./tmp/dbo-snapshots.nt

# Diffs the Ontology checks if sth important changed

LC_ALL=C sort -u "${pomdir}"/dbo-snapshots/2019.02.21T08.00.00Z/dbo-snapshots.nt > ./tmp/old-dbo-snapshots.nt

checkDiff ./tmp/old-dbo-snapshots.nt ./tmp/dbo-snapshots.nt

# If is_equal is 1, they are not equal and therefore there needs to be a new version commited
if [ $is_equal -eq 1 ]
then
	echo "Some new Version!"
	java -cp ./dbo-snapshots/DisplayAxioms.jar DisplayAxioms ./tmp/new-dbo-snapshots.owl | LC_ALL=C sort -u > ./tmp/dbo-snapshots.dl
	# Is the turtlefile needed in the release?
	# rapper -i rdfxml -o turtle ./tmp/new-dbo-snapshots.owl > ./tmp/dbo-snapshots.ttl
	# Remove old release
	rm "${pomdir}"/dbo-snapshots/2019.02.21T08.00.00Z/*.*
	mv ./tmp/dbo-snapshots.* "${pomdir}"/dbo-snapshots/2019.02.21T08.00.00Z/
	rm -rf ./tmp/
else
	echo "No new Version!"
	rm -r ./tmp/

fi



