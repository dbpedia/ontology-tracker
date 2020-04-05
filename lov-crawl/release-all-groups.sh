#! /bin/bash

parentDir="$1"
startDir=$PWD

for groupDir in $parentDir/*; do
	if [[ -d $groupDir ]]
	then
		cd $groupDir
		mvn package 
		cd $startDir
	fi
done
