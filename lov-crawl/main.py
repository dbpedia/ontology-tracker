import inspectVocabs
import generatePoms
import sys
import os
import crawlURIs
from datetime import datetime
from dateutil.parser import parse as parsedate
import ontoFiles


rootdir=sys.argv[1]
crawlURIs.crawlLOV(rootdir)
ontoFiles.deleteEmptyDirsRecursive(rootdir)