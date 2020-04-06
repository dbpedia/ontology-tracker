import os
import sys

parentArtifact="common-metadata"
downloadUrl="http://akswnc7.informatik.uni-leipzig.de/dstreitmatter/timed-lov-crawl/${project.groupId}/${project.artifactId}/${project.version}/"
packDir="/home/dstreitmatter/www/timed-lov-crawl/${project.groupId}/${project.artifactId}/"
deployVersion="2020.04.03-141057"
deployRepo="https://databus.dbpedia.org/repo"
pub="https://yum-yab.github.io/webid.ttl#onto"


def generateParentPom(groupId, artifactId, packaging, version, modules, packageDirectory, downloadUrlPath, deployRepoURL, publisher, maintainer, groupdocu):

    modlueStrings = []
    for module in modules:
        modlueStrings.append(f"    <module>{module}</module>")


    return ('<?xml version="1.0" encoding="UTF-8"?>  \n'  
    '<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"  \n'  
    '            xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">  \n'  
    '   <modelVersion>4.0.0</modelVersion>  \n'  
    '   <parent>  \n'  
    '       <groupId>org.dbpedia.databus</groupId>  \n'  
    '       <artifactId>super-pom</artifactId> \n '  
    '       <version>1.3-SNAPSHOT</version>  \n'  
    '   </parent>  \n'  
    '     \n'  
    f'  <groupId>{groupId}</groupId>  \n'  
    f'  <artifactId>{artifactId}</artifactId>  \n'  
    f'  <packaging>{packaging}</packaging>  \n'  
    f'  <version>{version}</version> \n '  
    '   <modules>  \n'
    ""+"\n".join(modlueStrings) + "\n"  
    '   </modules>  \n'   
    '   <properties>  \n'  
    '       <databus.tryVersionAsIssuedDate>false</databus.tryVersionAsIssuedDate>  \n'  
    '       <databus.packageDirectory>  \n'  
    f'          {packageDirectory} \n '  
    '       </databus.packageDirectory>  \n'   
    '       <databus.pkcs12File>${user.home}/.m2/onto_webid_bundle.p12</databus.pkcs12File>  \n'  
    '       <databus.downloadUrlPath>  \n'  
    f'          {downloadUrlPath} \n '  
    '       </databus.downloadUrlPath>  \n'  
    f'      <databus.deployRepoURL>{deployRepoURL}</databus.deployRepoURL>  \n'  
    f'      <databus.publisher>{publisher}</databus.publisher>  \n'  
    f'      <databus.maintainer>{maintainer}</databus.maintainer>  \n'  
    '       <databus.license>http://purl.oclc.org/NET/rdflicense/cc-by3.0</databus.license>  \n'  
    '       <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>  \n'  
    '       <databus.documentation><![CDATA[\n'
    f'      {groupdocu}\n'    
    '       ]]></databus.documentation>  \n'  
    '   </properties>  \n'  
    '     \n'  
    '   <!-- currently still needed to find the super-pom, once the super-pom is in maven central,  \n'  
    '       this can be removed as well -->  \n'  
    '   <repositories>  \n'  
    '       <repository>  \n'  
    '           <id>archiva.internal</id>  \n'  
    '           <name>Internal Release Repository</name>  \n'  
    '           <url>http://databus.dbpedia.org:8081/repository/internal</url>  \n'   
    '       </repository>  \n'  
    '       <repository>  \n'   
    '           <id>archiva.snapshots</id>  \n'  
    '           <name>Internal Snapshot Repository</name>  \n'   
    '           <url>http://databus.dbpedia.org:8081/repository/snapshots</url>  \n'  
    '           <snapshots>  \n'  
    '               <updatePolicy>always</updatePolicy>  \n'  
    '           </snapshots>  \n'  
    '       </repository>  \n'  
    '   </repositories>  \n'  
    '     \n'  
    '</project>  \n')  

def generateChildPom(groupId, parentArtifactId, version, artifactId, packaging):
    return ('<?xml version="1.0" ?>  '  
    '<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">  \n'  
    '\n'  
    '\n'  
    '   <parent>  \n'   
    f'      <groupId>{groupId}</groupId>  \n'  
    '\n'    
    f'      <artifactId>{parentArtifactId}</artifactId>  \n'  
    '\n'  
    f'      <version>{version}</version>  \n'  
    '\n'  
    '   </parent>  \n'  
    '\n'  
    '   <modelVersion>4.0.0</modelVersion>  \n'  
    '\n'  
    f'  <groupId>{groupId}</groupId>  \n' 
    '\n'    
    f'  <artifactId>{artifactId}</artifactId>  \n'  
    '\n'  
    f'  <packaging>{packaging}</packaging>  \n'  
    '\n'   
    '</project>\n')

def handleGroup(groupPath):
    groupId=os.path.split(groupPath)[1]
    print(f"Handling group: {groupId}")
    moduleList=[]



    if os.path.isdir(groupPath):
        for directory in os.listdir(groupPath):
            if os.path.isdir(groupPath+os.sep+directory):
                moduleList.append(directory)

                with open(groupPath+os.sep+directory+os.sep+"pom.xml", "w+") as pomfile:
                    childpomString=generateChildPom(groupId=groupId,
                                            parentArtifactId=parentArtifact,
                                            version=deployVersion,
                                            artifactId=directory,
                                            packaging="jar"
                                            )
                    print(childpomString, file=pomfile)

    print(f"Modules found: {len(moduleList)}")

    groupDoc=(f"#This group is for all vocabularies hosted on {groupId}\n\n"
            "All the artifacts in this group refer to one vocabulary, deployed in different formats.\n"
            "The ontologies are part of the Databus Archivo - A Web-Scale Ontology Interface for Time-Based and Semantic Archiving and Developing Good Ontologies.")

    if os.path.isdir(groupPath):
        with open(groupPath+os.sep+"pom.xml", "w+") as pomfile:
            pomstring=generateParentPom(groupId=groupId,
                                        artifactId=parentArtifact,
                                        packaging="pom",
                                        modules=moduleList,
                                        packageDirectory=packDir,
                                        downloadUrlPath=downloadUrl,
                                        deployRepoURL=deployRepo,
                                        publisher=pub,
                                        maintainer=pub,
                                        version=deployVersion,
                                        groupdocu=groupDoc
                                        )
            print(pomstring, file=pomfile)



dataPath=sys.argv[1]
for groupDir in os.listdir(dataPath):
    if os.path.isdir(dataPath+os.sep+groupDir):
        handleGroup(dataPath+os.sep+groupDir)


