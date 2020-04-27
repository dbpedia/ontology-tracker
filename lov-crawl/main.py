import inspectVocabs
import generatePoms
import sys
import os
import crawlURIs
from datetime import datetime
from dateutil.parser import parse as parsedate
import ontoFiles


rootdir=sys.argv[1]

index = ontoFiles.loadSimpleIndex()

new_uris = []

for uri in crawlURIs.getLovUrls():
    if not uri in index:
        new_uris.append(uri)

for uri in new_uris:
    crawlURIs.handleNewUri(uri, index, rootdir)

ontoFiles.writeSimpleIndex(index)