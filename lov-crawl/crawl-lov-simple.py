import requests
import subprocess
import re
import os
import sys

# url to get all vocabs and their resource
datasetUrl="https://lov.linkeddata.es/dataset/lov/api/v2/vocabulary/list"

urlRegex=r"https?://(.+?)/(.*)(\.\w+)?"

dataPath=sys.argv[1]

default_version="0.0.1"

def downloadSource(uri, path, name):
    try:
        acc_header = {'content-type': 'application/rdf+xml'}
        with open(path + "/" + name + ".ont", "w+") as ontfile:
            response=requests.get(uri, headers=acc_header, timeout=60, allow_redirects=True)
            print("Status: " + str(response.status_code))
            if response.status_code < 400:
                print(response.text, file=ontfile)
    except requests.exceptions.TooManyRedirects:
        print("Too many redirects, cancel parsing...")
    except TimeoutError:
        print("Timed out during parsing: "+uri)
    except requests.exceptions.ConnectionError:
        print("Bad Connection "+ uri)
    except requests.exceptions.ReadTimeout:
        print("Connection timed out for URI ", uri)

def rapperTheSource(uri, path, name):
    try:
        acc_header = {'content-type': 'application/rdf+xml'}
        header=requests.head(uri, headers=acc_header, timeout=30, allow_redirects=True)
        print("File response: "+str(header.status_code))
        if header.status_code < 400:
            with open(path + "/" + name + ".nt", "w+") as ontfile:
                process = subprocess.Popen(["rapper", "-g", uri], stdout=ontfile, stderr=subprocess.PIPE)
                none, stderr=process.communicate()
                print(stderr.decode("utf-8"))
    except requests.exceptions.TooManyRedirects:
        print("Too many redirects, cancel parsing...")
    except requests.exceptions.ConnectionError:
        print("Bad Connection "+ uri)
    except TimeoutError:
        print("Timed out during parsing: "+uri)
    except requests.exceptions.ReadTimeout:
        print("Connection timed out for URI ", uri)

def makeTheDirs(path):
    # i dont know why os.makedirs was not working
    dirs=path.split("/")
    
    for directory in dirs:
        if dirs.index(directory) == 0:
            fullpath=directory
        else:
            fullpath="/".join(dirs[0:dirs.index(directory)]) + "/" + directory
        if not os.path.isdir(fullpath):
            os.mkdir(fullpath)

req = requests.get(datasetUrl)
json_data=req.json()

for dataObject in json_data:
    vocab_uri=dataObject["uri"]
    print("Processing: VocabURI: " + vocab_uri)
    matcher=re.search(urlRegex, vocab_uri)
    groupId=matcher.group(1)
    artifact=matcher.group(2)
    if artifact != "":
        if artifact[-1] == "#" or artifact[-1] == "/":
            artifact=artifact[:-1]
        artifact=artifact.replace("/", ".")
    else:
        artifact="vocabulary"
    print("Artifact: <"+artifact+">")
    filePath=dataPath + "/" + groupId + "/" + artifact + "/" + default_version
    makeTheDirs(filePath)
    #rapperTheSource(vocab_uri, filePath, artifact)
    if not os.path.isfile(filePath + "/" + artifact + ".nt"):
        #downloadSource(vocab_uri, filePath, artifact)
        rapperTheSource(vocab_uri, filePath, artifact)
    else:
        print("Already loaded: " + filePath + "/" + artifact + ".nt")
