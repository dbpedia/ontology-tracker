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
echo "Commiting the data to git"
git add --all
git commit -message="$data_commit_info"
git push

# Releasing the new Version to maven
file_commit=$(git rev-parse HEAD)
echo "Commit-Hash of the files: ${file_commit}"
dataId_commit_info="dataId for the release on $(date), Commit-Hash:${last_commit}"
mvn versions:set -DnewVersion=${fullVersion}   
mvn package -DfileHash=$file_commit
	
# Commiting the new dataId to github
echo "Commitig DataId to Git..."
git add --all
git commit -message="$dataId_commit_info"
git push

dataId_commit=$(git rev-parse HEAD)
echo "DataId Hash: $dataId_commit"

mvn databus:deploy -DfileHash=$file_commit -DdataIdHash=$dataId_commit
}

pomdir=$1
startdir=$PWD

cd $pomdir

mkdir -p ./tmp/

data_commit_info="New ontology version on $(date)."

# Downloads the DBpedia-Ontology from http://mappings.dbpedia.org/server/ontology/dbpedia.owl
wget -O ./tmp/dbo-snapshots.owl http://mappings.dbpedia.org/server/ontology/dbpedia.owl

rapper -i rdfxml -o ntriples ./tmp/dbo-snapshots.owl | LC_ALL=C sort -u > ./tmp/dbo-snapshots.nt

# Diffs the Ontology checks if sth important changed

LC_ALL=C sort -u "${pomdir}"/dbo-snapshots/2019.02.21T08.00.00Z/dbo-snapshots.nt > ./tmp/old-dbo-snapshots.nt

checkDiff ./tmp/old-dbo-snapshots.nt ./tmp/dbo-snapshots.nt

# If is_equal is 1, they are not equal and therefore there needs to be a new version commited
if [ $is_equal -eq 0 ]
then
	echo "Some new Version!"
	java -cp ./dbo-snapshots/DisplayAxioms.jar DisplayAxioms ./tmp/dbo-snapshots.owl | LC_ALL=C sort -u > ./tmp/dbo-snapshots.dl
	rapper -i rdfxml -o turtle ./tmp/dbo-snapshots.owl > ./tmp/dbo-snapshots.ttl
	# Remove old release
	rm "${pomdir}"/dbo-snapshots/2019.02.21T08.00.00Z/*.*
	mv ./tmp/dbo-snapshots.* "${pomdir}"/dbo-snapshots/2019.02.21T08.00.00Z/
	rm -rf ./tmp/
	commitAndRelease
else
	echo "No new Version!"
	rm -r ./tmp/

fi

cd $startdir

