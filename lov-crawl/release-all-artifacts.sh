#! /bin/bash

parentDir="$1"
startDir=$PWD

for groupDir in $parentDir/*; do
	if [[ -d $groupDir ]]
	then
		for artifactDir in $groupDir/*; do
			if [[ -d $artifactDir ]]
			then
				cd $artifactDir
				mvn package 
				cd $startDir
			fi
		done
	fi
done
