import os
import sys

# some defaults for the pom generation
default_license="http://ontotrack.dbpedia.org/issue?license=unknown"
default_parentArtifact="common-metadata"
default_repo="https://databus.dbpedia.org/repo"
default_version="0.0.0-notRelevant"

# edit for your dataset
downloadUrl="http://akswnc7.informatik.uni-leipzig.de/dstreitmatter/timed-lov-crawl/${project.groupId}/${project.artifactId}/${project.version}/"
packDir="/home/dstreitmatter/www/timed-lov-crawl/${project.groupId}/${project.artifactId}/"
pub="https://yum-yab.github.io/webid.ttl#onto"

def generateParentPom(groupId, packaging, modules, packageDirectory, downloadUrlPath, publisher, maintainer, groupdocu, license=default_license, deployRepoURL=default_repo, version=default_version, artifactId=default_parentArtifact):

    modlueStrings = [f"    <module>{module}</module>" for module in modules]
    
    if modules == []:
        moduleString = ""
    else:
        moduleString = "   <modules>"+"\n".join(modlueStrings)+"\n   </modules>\n "

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
    f'{moduleString}'  
    '   <properties>  \n'  
    '       <databus.tryVersionAsIssuedDate>false</databus.tryVersionAsIssuedDate>  \n'  
    '       <databus.packageDirectory>  \n'  
    f'          {packageDirectory} \n '  
    '       </databus.packageDirectory>  \n'   
    '       <databus.pkcs12File>${user.home}/.m2/onto_webid_bundle.p12</databus.pkcs12File>  \n'  
    '       <databus.downloadUrlPath>  \n'  
    f'          {downloadUrlPath} \n '  
    '       </databus.downloadUrlPath>  \n'  
    f'       <databus.deployRepoURL>{deployRepoURL}</databus.deployRepoURL>  \n'  
    f'       <databus.publisher>{publisher}</databus.publisher>  \n'  
    f'       <databus.maintainer>{maintainer}</databus.maintainer>  \n'  
    f'       <databus.license>{license}</databus.license>  \n'  
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

def generateChildPom(groupId, artifactId, packaging, version, license=None, parentArtifactId=default_parentArtifact, parentVersion=default_version):
    if version == None or version == "":
        versionString = ""
    else:
        versionString = f"<version>{version}</version>"

    if license == None or license == "":
        licenseString = ""
    else:
        licenseString = (
                        '   <properties>\n'
                        f'      <databus.license>{license}</databus.license>\n'
                        '   </properties>\n'
                        )
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
        f'{versionString}'
        '\n'
        f'  <groupId>{groupId}</groupId>  \n' 
        '\n'    
        f'  <artifactId>{artifactId}</artifactId>  \n'  
        '\n'  
        f'  <packaging>{packaging}</packaging>  \n'  
        '\n'
        f'{licenseString}' 
        '</project>\n')


def writeMarkdownDescription(path, artifact, label, explaination, description=""):

  with open(path  + os.sep + artifact + ".md", "w+") as mdfile:
    mdstring=(f"# {label}\n"
            f"{explaination}\n"
            "\n"
            f"{description}")
    print(mdstring, file=mdfile)



