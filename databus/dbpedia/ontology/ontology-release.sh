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


createDirectories() {

	mkdir -p ./data/ontology/dbo-snapshots/$fullVersion
	cp $repoPomDir/pom.xml data/ontology/pom.xml
	cp $repoPomDir/dbo-snapshots/pom.xml data/ontology/dbo-snapshots/pom.xml
	cp $repoPomDir/dbo-snapshots/dbo-snapshots.md data/ontology/dbo-snapshots/dbo-snapshots.md
	
}

commitAndRelease() {
	
	
	cd $dataPomDir

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

	# Copying the new dataId into the git
	if [ -f dbo-snapshots/target/databus/$fullVersion/dataid.ttl ]
	then 
		cat dbo-snapshots/target/databus/$fullVersion/dataid.ttl
	else
		echo "No dataid available!"
	fi
	cp dbo-snapshots/target/databus/$fullVersion/dataid.ttl $repoPomDir/dbo-snapshots/dataid.ttl
	
	# Commiting the new dataId to github
	echo "Commitig DataId to Git..."
	git add --all
	git commit -m "$dataId_commit_info"
	git push
	
	dataId_commit=$(git rev-parse HEAD)
	echo "DataId Hash: $dataId_commit"
	
	#mvn databus:deploy -DfileHash=$file_commit -DdataIdHash=$dataId_commit
}

repoPomDir=$PWD
startdir=$PWD

fullVersion=$(date "+%Y.%m.%dT%H:%M:%SZ")

createDirectories

data_commit_info="New ontology version on $(date)."

newVersionDirectory=data/ontology/dbo-snapshots/$fullVersion

dataPomDir=data/ontology

# Downloads the DBpedia-Ontology from http://mappings.dbpedia.org/server/ontology/dbpedia.owl
wget -O $newVersionDirectory/dbo-snapshots.owl http://mappings.dbpedia.org/server/ontology/dbpedia.owl

rapper -i rdfxml -o ntriples $newVersionDirectory/dbo-snapshots.owl | LC_ALL=C sort -u > $newVersionDirectory/dbo-snapshots.nt

LC_ALL=C sort -u "${repoPomDir}"/dbo-snapshots/dbo-snapshots.nt > $newVersionDirectory/old-dbo-snapshots.nt

checkDiff $newVersionDirectory/old-dbo-snapshots.nt $newVersionDirectory/dbo-snapshots.nt

# If is_equal is 1, they are not equal and therefore there needs to be a new version commited
if [ $is_equal -eq 0 ]
then
	echo "Some new Version!"
	rm $newVersionDirectory/old-dbo-snapshots.nt
	
	
	# Generating the turtle and dl files from the ontology	
	java -cp ./DisplayAxioms.jar DisplayAxioms $newVersionDirectory/dbo-snapshots.owl | LC_ALL=C sort -u > $newVersionDirectory/dbo-snapshots.dl
	rapper -i rdfxml -o turtle $newVersionDirectory/dbo-snapshots.owl > $newVersionDirectory/dbo-snapshots.ttl
	

	cp $newVersionDirectory/dbo-snapshots.* "${repoPomDir}"/dbo-snapshots/
	commitAndRelease
else
	echo "No new Version!"
	rm -r $newVersionDirectory 

fi

cd $startdir

