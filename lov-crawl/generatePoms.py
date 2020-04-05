import os
import sys

parentArtifact="common-metadata"
downloadUrl="http://akswnc7.informatik.uni-leipzig.de/dstreitmatter/timed-lov-crawl/${project.groupId}/${project.artifactId}/${project.version}/"
packDir="/home/dstreitmatter/www/timed-lov-crawl/${project.groupId}/${project.artifactId}/"
deployVersion="2020.04.03-141057"
deployRepo="https://databus.dbpedia.org/repo"
pub="https://yum-yab.github.io/webid.ttl#onto"


def generateParentPom(groupId, artifactId, packaging, version, modules, packageDirectory, downloadUrlPath, deployRepoURL, publisher, maintainer):

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
    '       <databus.documentation><![CDATA[  \n'  
    '       ## Attribution fulfilled by  \n'  
    '       * (when deriving another dataset and releasing to the Databus) adding the Databus link to the provenance https://databus.dbpedia.org/dbpedia/${project.groupId}/${project.artifactId}/${project.artifactId}/${project.version}  \n' 
    '       * on your website:  \n'  
    '       * include the DBpedia logo and mention the usage of DBpedia with this link: https://databus.dbpedia.org/dbpedia  \n'  
    '       * include backlinks from your pages to the individual entities, e.g. http://dbpedia.org/resource/Berlin  \n'  
    '       * in academic publications cite: DBpedia - A Large-scale, Multilingual Knowledge Base Extracted from Wikipedia, J. Lehmann, R. Isele, M. Jakob, A. Jentzsch, D. Kontokostas, P. Mendes, S. Hellmann, M. Morsey, P. van Kleef, S. Auer, and C. Bizer. Semantic Web Journal 6 (2): 167--195 (2015)  \n' 
    '     \n'  
    '       ## How to contribute  \n'  
    '       DBpedia is a community project, help us with:  \n'  
    '       * editing the mappings at http://mappings.dbpedia.org  \n'  
    '       * improve this documentation at https://github.com/dbpedia/databus-maven-plugin/tree/master/dbpedia/mappings/${project.artifactId}/${project.artifactId}.md  \n'  
    '       * help with the software relevant for extraction:  \n'  
    '       ** https://github.com/dbpedia/extraction-framework/tree/master/core/src/main/scala/org/dbpedia/extraction/mappings  \n' 
    '       ** in particular https://github.com/dbpedia/extraction-framework/blob/master/core/src/main/scala/org/dbpedia/extraction/mappings/InfoboxMappingsExtractor.scala  \n' 
    '       \n'  
    '       ## Debug  \n'  
    '       Parselogs are currently kept here: http://downloads.dbpedia.org/temporary/parselogs/  \n'  
    '     \n'  
    '       ## Origin  \n'  
    '       This dataset was extracted using the wikipedia-dumps available on https://dumps.wikimedia.org/  \n' 
    '       using the DBpedia Extraction-Framework available at https://github.com/dbpedia/extraction-framework  \n' 
    '       For more technical information on how these datasets were generated, please visit http://dev.dbpedia.org  \n' 
    '     \n'  
    '       # Changelog  \n'  
    '       ## since 2018.09.12  \n'   
    '       * were created as new modular releases, some issues remain  \n'  
    '       * we used rapper 2.0.14 to parse and `LC_ALL=C sort` to sort and ascii2uni -a U to unescape unicdoe xcharacters  \n'  
    '       * parsing removed 250k triples total, debugging pending  \n'  
    '       * object-uncleaned was not transformed into objects-cleaned and is missing  \n'  
    '       * link to Wikimedia dump version is missing  \n'  
    '       ## 2016.10.01  \n'  
    '       * was taken from the previous BIG DBpedia releases under http://downloads.dbpedia.org/2016-10/ and included for completeness  \n'  
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

def generateMarkdownDescription(label, explaination, description=""):
    return(f"# {label}\n"
        f"{explaination}\n"
        "\n"
        f"{description}")


def handleGroup(groupPath):
    pathToGroup, groupId=os.path.split(groupPath)
    print(f"Handling group: {groupId}")
    moduleList=[]



    if os.path.isdir(groupPath):
        for directory in os.listdir(groupPath):
            groupLabel=f"{groupId} ontologies"
            groupExplaination=f"From https://lov.linkeddata.es/ automatically crawled vocabularies hosted on {groupId}. This is the vocabulary {directory}\n\n."
            groupExplaination=groupExplaination + f"The {directory}.json file contains the ontology-uri, the last modified date (http last-modified) and the rapper error/warnings"

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

                with open(groupPath+os.sep+directory+os.sep+directory+".md", "w+") as mdfile:
                    print(generateMarkdownDescription(groupLabel, groupExplaination), file=mdfile)

    print(f"Modules found: {len(moduleList)}")

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
                                        version=deployVersion
                                        )
            print(pomstring, file=pomfile)



dataPath=sys.argv[1]
for groupDir in os.listdir(dataPath):
    if os.path.isdir(dataPath+os.sep+groupDir):
        handleGroup(dataPath+os.sep+groupDir)


