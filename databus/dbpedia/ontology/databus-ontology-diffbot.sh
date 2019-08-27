#!/usr/bin/env bash 

# CARE: this script needs to be located directly next to the parent pom of ontology repo 
# all data is saved in a data-Diretory right next to the pom, so write that to the gitignore to not commit it to the repository

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

	mkdir -p $repoPomDir/data/ontology/dbo-snapshots/$fullVersion
	cp $repoPomDir/pom.xml $repoPomDir/data/ontology/pom.xml
	cp $repoPomDir/dbo-snapshots/pom.xml $repoPomDir/data/ontology/dbo-snapshots/pom.xml
	cp $repoPomDir/dbo-snapshots/dbo-snapshots.md $repoPomDir/data/ontology/dbo-snapshots/dbo-snapshots.md
	
}

commitAndRelease() {
	
	
	cd $dataPomDir

	# Handling the git process
	echo "Commiting the data to git"
	git add --all
	git commit -m "$data_commit_info"
	git push

	# Releasing the new Version to maven
	file_commit=$(git rev-parse HEAD)
	echo "Commit-Hash of the files: ${file_commit}"

	# Generates commit-Message for the dataId-Release
	dataId_commit_info="Upload dataid.ttl for version: ${fullVersion}"
	
	
	# generates the dataid.ttl for the right version
	mvn versions:set -DnewVersion=${fullVersion}   
	mvn package -DfileHash=$file_commit

	# Copying the new dataId into the git
	cp dbo-snapshots/target/databus/$fullVersion/dataid.ttl $repoPomDir/dbo-snapshots/dataid.ttl
	
	# Commiting the new dataId to github
	echo "Commitig DataId to Git..."
	git add --all
	git commit -m "$dataId_commit_info"
	git push
	
	# deploy the data to the databus
	dataId_commit=$(git rev-parse HEAD)
	echo "DataId Hash: $dataId_commit"
	
	mvn databus:deploy -DfileHash=$file_commit -DdataIdHash=$dataId_commit
}

######################## BEGIN ##################################################


repoPomDir=$(realpath -s $0)
repoPomDir=${repoPomDir%/*}
startdir=$PWD

if ! [ -f $repoPomDir/pom.xml ] || ! [ -d $repoPomDir/dbo-snapshots ]
then
	echo "Started from the wrong directory! The script needs to be right at the parent-pom of the Group!"
	exit 1
fi

# cd into the repo to pull and generate the files
cd $repoPomDir
# pulls from the repo to use changes and be able to push
git pull

fullVersion=$(date "+%Y.%m.%d-%H%M%S")

createDirectories

data_commit_info="Upload new ontology snapshot version: ${fullVersion}"

newVersionDirectory=$repoPomDir/data/ontology/dbo-snapshots/$fullVersion

dataPomDir=$repoPomDir/data/ontology

# Downloads the DBpedia-Ontology from http://mappings.dbpedia.org/server/ontology/dbpedia.owl
wget -O $newVersionDirectory/dbo-snapshots.owl http://mappings.dbpedia.org/server/ontology/dbpedia.owl


# Generates ntriples from new ontology, sorts them and check if its different from the old nt file
rapper -i rdfxml -o ntriples $newVersionDirectory/dbo-snapshots.owl | LC_ALL=C sort -u > $newVersionDirectory/dbo-snapshots.nt
LC_ALL=C sort -u "${repoPomDir}"/dbo-snapshots/dbo-snapshots.nt > $newVersionDirectory/old-dbo-snapshots.nt
checkDiff $newVersionDirectory/old-dbo-snapshots.nt $newVersionDirectory/dbo-snapshots.nt


# If is_equal is 1, they are not equal and therefore there needs to be a new version commited
if [ $is_equal -eq 1 ]
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

