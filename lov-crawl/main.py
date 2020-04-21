import inspectVocabs
import generatePoms
import sys
import os
import crawlURIs
from datetime import datetime
from dateutil.parser import parse as parsedate
import ontoFiles

parentArtifact="common-metadata"
downloadUrl="http://akswnc7.informatik.uni-leipzig.de/dstreitmatter/timed-lov-crawl/${project.groupId}/${project.artifactId}/${project.version}/"
packDir="/home/dstreitmatter/www/timed-lov-crawl/${project.groupId}/${project.artifactId}/"
deployRepo="https://databus.dbpedia.org/repo"
pub="https://yum-yab.github.io/webid.ttl#onto"
default_license="http://ontotrack.dbpedia.org/issue?license=unknown"

def handleArtifact(pathToArtifactFiles):
    versionDir=""
    groupPath, artifactName=os.path.split(pathToArtifactFiles)
    groupName = os.path.split(groupPath)[1]
    for versionDir in os.listdir(pathToArtifactFiles):
        if os.path.isdir(pathToArtifactFiles + os.sep + versionDir):
            versionDir=pathToArtifactFiles + os.sep + versionDir
            break
    if os.path.isfile(versionDir + os.sep + artifactName + "_type=parsed.ttl"):         
        vocab_graph=inspectVocabs.getGraphOfVocabFile(versionDir + os.sep + artifactName + "_type=parsed.ttl")
        vocab_uri,  rdfs_label, rdfs_comment, rdfs_description = inspectVocabs.getRelevantRDFSVocabInfo(vocab_graph)
        dcterms_license, dcterms_title, dcterms_abstract, dcterms_description = inspectVocabs.getRelevantDCTERMSVocabInfo(vocab_graph)[1:]
        dc_title, dc_description = inspectVocabs.getRelevantDCVocabInfo(vocab_graph)[1:]
        if vocab_uri != None:
            print("Handling the metadata for " + vocab_uri)
        else:
            print(f"Error: No valid ontology-uri for: group: {groupName}; artifact: {artifactName}")

        if rdfs_label != None:
            label = rdfs_label
        elif dcterms_title != None:
            label = dcterms_title
        elif dc_title != None:
            label=dc_title
        else:
            label=artifactName + " ontology"

        explaination="This ontology is part of the Databus Archivo - A Web-Scale OntologyInterface for Time-Based and SemanticArchiving and Developing Good Ontologies"

        if rdfs_description != None:
            description = rdfs_description
        elif dcterms_description != None:
            description = dcterms_description
        elif dc_description != None:
            description=dc_description
        elif rdfs_comment != None:
            description=rdfs_comment
        elif dcterms_abstract != None:
            description = dcterms_abstract
        else:
            description=""

        generatePoms.writeMarkdownDescription(pathToArtifactFiles, artifactName, label, explaination, description=description)
        with open(pathToArtifactFiles + os.sep + "pom.xml", "w+") as childpomfile:
            childpomString=generatePoms.generateChildPom(
                                                groupId=groupName,
                                                parentArtifactId=parentArtifact,
                                                version=version,
                                                artifactId=artifactName,
                                                packaging="jar",
                                                license=dcterms_license
                                                )
            print(childpomString, file=childpomfile)
    else:
        print("No proper vocab for " + pathToArtifactFiles)
    

def handleGroup(pathToGroup):
    groupName = os.path.split(pathToGroup)[1]
    moduleList=[]
    for directory in os.listdir(pathToGroup):
        if os.path.isdir(pathToGroup + os.sep + directory):
            moduleList.append(directory)
            handleArtifact(pathToGroup + os.sep + directory)


    groupDoc=(f"#This group is for all vocabularies hosted on {groupName}\n\n"
            "All the artifacts in this group refer to one vocabulary, deployed in different formats.\n"
            "The ontologies are part of the Databus Archivo - A Web-Scale Ontology Interface for Time-Based and Semantic Archiving and Developing Good Ontologies.")

    with open(pathToGroup + os.sep + "pom.xml", "w+") as pomfile:
        pomString=generatePoms.generateParentPom(
                                        groupId=groupName,
                                        artifactId=parentArtifact,
                                        packaging="pom",
                                        version=version,
                                        modules=moduleList,
                                        packageDirectory=packDir,
                                        downloadUrlPath=downloadUrl,
                                        deployRepoURL=deployRepo, 
                                        publisher=pub,
                                        maintainer=pub,
                                        groupdocu=groupDoc,
                                        license=default_license
                                        )
        print(pomString, file=pomfile)

rootdir=sys.argv[1]
#version=datetime.now().strftime("%Y.%m.%d-%H%M%S")
version="2020.04.20-130532"
crawlURIs.crawlLOV(rootdir, version)
ontoFiles.deleteEmptyDirsRecursive(rootdir)
for directory in os.listdir(rootdir):
    if os.path.isdir(rootdir + os.sep + directory):
        handleGroup(rootdir + os.sep + directory)