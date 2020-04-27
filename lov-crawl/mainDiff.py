import inspectVocabs
import sys
import crawlURIs
import json
import os
import ontoFiles
import diffOntologies

rootdir = sys.argv[1]

localDiffDir = ".tmpDiffDir"

for groupdir in [dir for dir in os.listdir(rootdir) if os.path.isdir(os.path.join(rootdir, dir))]:
    for artifactDir in [dir for dir in os.listdir(os.path.join(rootdir, groupdir)) if os.path.isdir(os.path.join(rootdir, groupdir, dir))]:
        print("Checking ", groupdir, artifactDir)
        versionDirs = [dir for dir in os.listdir(os.path.join(rootdir, groupdir, artifactDir)) if os.path.isdir(os.path.join(rootdir, groupdir, artifactDir, dir))]
        versionDirs.sort(reverse=True)
        latestVersion = versionDirs[0]
        latestVersionDir = os.path.join(rootdir, groupdir, artifactDir, latestVersion)
        if os.path.isfile(os.path.join(latestVersionDir, artifactDir + "_type=meta.json")):
            with open(os.path.join(latestVersionDir, artifactDir + "_type=meta.json"), "r")as jsonFile:
                metadata = json.load(jsonFile)
        else:
            print("No metadata", groupdir, artifactDir)
            continue
        
        if not os.path.isfile(os.path.join(latestVersionDir, artifactDir + "_type=parsed.ttl")):
            print("No parseable source, continue", groupdir, artifactDir)
            continue

        oldETag = metadata["E-Tag"]
        oldLastMod = metadata["lastModified"]
        uri = metadata["ontology-resource"]
        bestHeader = metadata["best-header"]

        if bestHeader == "":
            continue

        isDiff = diffOntologies.checkForNewVersion(uri, oldETag, oldLastMod, bestHeader)

        if isDiff != None and isDiff:
            success, sourcePath, response = crawlURIs.downloadSource(uri, localDiffDir, "tmpSource", bestHeader)
            if not success:
                print("Uri not reachable")
                continue
            ontoFiles.parseRDFSource(sourcePath, os.path.join(localDiffDir, "tmpSourceParsed.ttl"), "turtle", deleteEmpty=True, silent=False)
            if not os.path.isfile(os.path.join(localDiffDir, "tmpSourceParsed.ttl")): 
                print("File not parseable")
                continue
            oldGraph = inspectVocabs.getGraphOfVocabFile(os.path.join(latestVersionDir, artifactDir + "_type=parsed.ttl"))
            newGraph = inspectVocabs.getGraphOfVocabFile(os.path.join(localDiffDir, "tmpSourceParsed.ttl"))
            both, old, new = diffOntologies.graphDiff(oldGraph, newGraph)
            if len(old) == 0 and len(new) == 0:
                print("Not different")
            else:
                print("Different!")
        elif isDiff != None and not isDiff:
            print("No new Version available!")
        else:
            print("Not reachable URL")