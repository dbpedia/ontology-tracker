import re
import os

urlRegex=r"https?://(?:www\.)?(.+?)/(.*)"

# regex for parsing the file ending of an url
uriFileExtensionRegex = re.compile(r"^.*\/.+(\.\w+)$")

#should be extended maybe
fileTypeDict = {"turtle": ".ttl", "rdf+xml": ".rdf", "ntriples": ".nt", "rdf+n3":".n3", "html":".html", "xml":".xml"}

# regex to get the content type
contentTypeRegex = re.compile(r"\w+/([\w+-]+)(?:.*)?")

def isNoneOrEmpty(string):
  if string != None and string != "":
    return False
  else:
    return True

def getFileExtensionFromUri(uri):
  match = uriFileExtensionRegex.match(uri)
  if match != None:
    return match.group(1)
  else:
    return ""

def generateGroupAndArtifactFromUri(vocab_uri):
  matcher=re.search(urlRegex, vocab_uri)
  if matcher != None:
    groupId=matcher.group(1)
    artifact=matcher.group(2)
  else:
    groupId = "default-group"
    artifact = "default-artifact"
  if artifact != "":
    if artifact[-1] == "#" or artifact[-1] == os.sep:
      artifact=artifact[:-1]
    artifact=artifact.replace(os.sep, "--").replace("_", "--").replace(".", "--")
  else:
    artifact="vocabulary"
  return groupId, artifact


def getLastModifiedFromResponse(response):
  if "last-modified" in response.headers.keys():
    return response.headers["last-modified"]
  else:
    return ""


def getEtagFromResponse(response):
  if "ETag" in response.headers.keys():
    return response.headers["ETag"]
  else:
    return ""

def getFileEnding(response):
  if "Content-Type" in response.headers.keys():
    contentType = response.headers["content-type"]
    match = contentTypeRegex.search(contentType)
    fileEnding = ""
    if match == None:
      fileEnding = ""
    else:
      fileEnding = fileTypeDict.get(match.group(1), "")
    if contentType == "":
      fileEnding = getFileExtensionFromUri(response.url)
    return fileEnding
  else:
    return ""