import os
import sys


def generateParentPom(groupId, artifactId, packaging, version, modules, packageDirectory, downloadUrlPath, deployRepoURL, publisher, maintainer, groupdocu, license):

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

def generateChildPom(groupId, parentArtifactId, version, artifactId, packaging, license=None):
    if license == None:
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
    else:
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
        '   <properties>\n'
        f'    <databus.license>{license}</databus.license>\n'  
        '   </properties>\n' 
        '</project>\n')


def writeMarkdownDescription(path, artifact, label, explaination, description=""):

  with open(path  + os.sep + artifact + ".md", "w+") as mdfile:
    mdstring=(f"# {label}\n"
            f"{explaination}\n"
            "\n"
            f"{description}")
    print(mdstring, file=mdfile)



