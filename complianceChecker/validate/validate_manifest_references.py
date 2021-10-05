#This file is a part of the eFMI Compliance Checker which is a python open-source 
# library intended for checking the compliance of an eFMU with the standard specification

#Copyright © ESI ITI GmbH, 2021
               
#This program is a free software distributed WITHOUT ANY WARRANTY and the use is 
#completely at your own risk; it can be redistributed and/or modified under the 
#terms of the BSD 3-Clause license. For license conditions (including the 
#disclaimer of warranty) visit: https://opensource.org/licenses/BSD-3-Clause.

#ESI ITI GmbH, Zwinger-Forum, Schweriner Straße 1, 01067 Dresden, Germany


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
                        with open(os.path.join(Representation.workingDir, Representation.efmuContent, rep1.getName(), rep1.getManifest()), "rU") as FILE:
                            xml_file_lines = FILE.readlines()
    
                        manifestTree = ET.fromstringlist(xml_file_lines, parser=LineNumberingParser()) 

                        #modelManifest = manifestTree.findall('Manifest')
                        id = manifestTree.get('id')
                        if id == ref.getManifestRefId():
                            refIdFound = 1
                            if ref.getChecksum() != "":
                                calculatedChecksum = sha_hash(os.path.join(Representation.workingDir, Representation.efmuContent, rep1.getName(), rep1.getManifest()))
                                if ref.getChecksum() != calculatedChecksum:
                                    #print(ref.getChecksum())
                                    print(calculatedChecksum)
                                    s = "The checksum of the ManifestReference (id = " + ref.getId() + ") in the " + rep.getName() + " representation does not match the calculated checksum"
                                    if rep.getKind() in messages.keys():
                                        messages[rep.getKind()].updat({ref.getId() : s})
                                    else:
                                        messages[rep.getKind()] = {ref.getId() : s}
                if refIdFound == 0:
                    s = "The manifestRefId of the ManifestReference (id = " + ref.getId() + ") in the " + rep.getKind() + " representation does not match any of the existing representaion manifests"
                    if rep.getName() in messages.keys():
                        messages[rep.getKind()].updat({ref.getId() : s})
                    else:
                        messages[rep.getKind()] = {ref.getId() : s}
    return messages
