# Copyright (c) 2021, ESI ITI GmbH, Modelica Association and contributors
# 
# Licensed under the 3-Clause BSD license (the "License");
# you may not use this software except in compliance with
# the "License".
# 
# This software is not fully developed or tested.
# 
# THE SOFTWARE IS PROVIDED "as is", WITHOUT ANY WARRANTY
# of any kind, either express or implied, and the use is 
# completely at your own risk.
# 
# The software can be redistributed and/or modified under
# the terms of the "License".
# 
# See the "License" for the specific language governing
# permissions and limitations under the "License".

import os
from data.Representations import Representation
from lxml import etree as ET

from data.Representations import sha_hash, LineNumberingParser

def validateReferences (representations):
    messages = {}
    #refIdFound = 0
    for rep in representations:
        if len(rep.getManifestReferences()) > 0:
            for ref in rep.getManifestReferences():
                refIdFound = 0
                for rep1 in representations:
                    if rep1.getManifestRefId() != rep.getManifestRefId():
                        with open(os.path.join(Representation.workingDir, Representation.efmuContent, rep1.getName(), rep1.getManifest()), mode="rU", encoding='utf-8-sig') as FILE:
                            xml_file_lines = FILE.readlines()
    
                        manifestTree = ET.fromstringlist(xml_file_lines, parser=LineNumberingParser()) 

                        #modelManifest = manifestTree.findall('Manifest')
                        id = manifestTree.get('id')
                        if id == ref.getManifestRefId():
                            refIdFound = 1
                            if ref.getChecksum() != "":
                                calculatedChecksum = sha_hash(os.path.join(Representation.workingDir, Representation.efmuContent, rep1.getName(), rep1.getManifest()))
                                if ref.getChecksum() != calculatedChecksum:
                                    s = "The checksum [" + ref.getChecksum() + "] of the ManifestReference [" + ref.getId() + "] in the [" + rep.getName() + "] container does not match the calculated checksum [" + calculatedChecksum + "]."
                                    if rep.getName() in messages.keys():
                                        messages[rep.getName()].update({ref.getId() : s})
                                    else:
                                        messages[rep.getName()] = {ref.getId() : s}
                if refIdFound == 0:
                    s = "The manifestRefId of the ManifestReference [" + ref.getId() + "] in the [" + rep.getName() + "] container does not match any of the existing representation manifests"
                    if rep.getName() in messages.keys():
                        messages[rep.getName()].update({ref.getId() : s})
                    else:
                        messages[rep.getName()] = {ref.getId() : s}
    return messages
