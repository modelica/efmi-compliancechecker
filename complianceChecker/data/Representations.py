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
from lxml import etree as ET
import hashlib

BLOCKSIZE = 65536
ALGORITH_CODE_SCHEMA = 'efmiAlgorithmCodeManifest.xsd'
BEHAVIOR_MODEL_SCHEMA = 'efmiBehavioralModelManifest.xsd'
EQUATION_CODE_SCHEMA = 'efmiEquationCodeManifest.xsd'
BINARY_CODE_SCHEMA = 'efmiBinaryCodeManifest.xsd'
PRODUCTION_CODE_SCHEMA = 'efmiProductionCodeManifest.xsd'

def sha_hash(fileName):
    hasher = hashlib.sha1()
    with open(fileName, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()

def repSchemaFile(schemaFolder):
    for file in schemaFolder:
        if file == ALGORITH_CODE_SCHEMA:
            return ALGORITH_CODE_SCHEMA
        elif file == BEHAVIOR_MODEL_SCHEMA:
            return BEHAVIOR_MODEL_SCHEMA
        elif file == EQUATION_CODE_SCHEMA:
            return EQUATION_CODE_SCHEMA
        elif file == BINARY_CODE_SCHEMA:
            return BINARY_CODE_SCHEMA
        elif file == PRODUCTION_CODE_SCHEMA:
            return PRODUCTION_CODE_SCHEMA
    return None

def findDoc(pathToDir, docName):
    for file in (pathToDir):
        if file == docName:
            return True
    return False

class LineNumberingParser(ET.XMLParser):

    def __init__(self, *args, **kwargs):
        super(LineNumberingParser, self).__init__(*args, **kwargs)

    def feed(self, data):
        line = data.strip() + "\n"
        super(LineNumberingParser, self).feed(line)

class ManifetReference:
    
    def __init__(self, id, manifestRefId, checksum):
        self.id = id
        self.manifestRefId = manifestRefId
        self.checksum = checksum
    
    def getId (self):
        return self.id
    
    def getManifestRefId(self):
        return self.manifestRefId
    
    def getChecksum(self):
        return self.checksum


class Representation:

    workingDir = ""
    efmuContent = ""
    schemasFolder = ""
    schemasFolderExist = False
    

    def __init__(self, kind=None, name=None, manifest=None, checksum=None, manifestRefId=None):
        self.kind = kind
        self.name = name
        self.manifest = manifest
        self.checksum = checksum
        self.manifestRefId = manifestRefId
        self.rep_schema_file = None
        self.repDirFound = False
        self.repManifestFound = False
        self.manifestReferences = []

    def setKind(self, kind):
        self.kind = kind
    
    def getKind (self):
        return self.kind

    def setName(self, name):
        self.name = name
    
    def getName(self):
        return self.name
    
    def setManifest(self, manifest):
        self.manifest = manifest
    
    def getManifest(self):
        return self.manifest

    def setChecksum(self, checksum):
        self.checksum = checksum
    
    def getChecksum(self):
        return self.checksum
    
    def setManifestRefId(self, manifestRefId):
        self.manifestRefId = manifestRefId
    
    def getManifestRefId(self):
        return self.manifestRefId
    
    def getManifestReferences (self):
        return self.manifestReferences
    
    def addManifestReferences(self):
        with open(os.path.join(Representation.workingDir, Representation.efmuContent, self.name, self.manifest), mode="rU", encoding='utf-8-sig') as FILE:
            xml_file_lines = FILE.readlines()
        
        manifestTree = ET.fromstringlist(xml_file_lines, parser=LineNumberingParser())

        manifest_references = manifestTree.findall('ManifestReferences')
        if len(manifest_references) > 0:
            for file in manifest_references[0].findall('ManifestReference'):
                id = file.get('id')
                manifestRefId = file.get('manifestRefId')
                checksum = file.get('checksum')
                manifestReference = ManifetReference(id, manifestRefId, checksum)
                self.manifestReferences.append(manifestReference)

    def setSechmaFile (self):
        schema_fileName = None
        
        if Representation.schemasFolderExist == True:
            patheTo_schemas_folder = os.listdir(os.path.join(Representation.workingDir, Representation.efmuContent, Representation.schemasFolder))
            #print(os.path.join(Representation.workingDir, Representation.efmuContent, Representation.schemasFolder))
            for file in patheTo_schemas_folder:
                if file == self.kind:
                    #print('\033[92m' + '         The %s folder correctly exists in the %s' % (self.kind, os.path.join(Representation.workingDir, Representation.efmuContent, Representation.schemasFolder)))
                    rep_in_schemas = file
                    path_to_rep_in_schemas = os.listdir(os.path.join(Representation.workingDir, Representation.efmuContent, Representation.schemasFolder, rep_in_schemas))
                    schema_fileName = repSchemaFile(path_to_rep_in_schemas)
        
        if schema_fileName != None:
            self.rep_schema_file = schema_fileName
            return True
        else:
            return False
    
    def getSchaFile(self):
        return self.rep_schema_file

    def setRepDirFound(self):
        dirFound = False
        if self.name is not None and self.kind is not None:
            pathTo_eFMU_dir = os.listdir(os.path.join(Representation.workingDir, Representation.efmuContent))
            dirFound = findDoc(pathTo_eFMU_dir, self.name)
        self.repDirFound = dirFound
    
    def setRepManifestFound(self):
        manifestFound = False
        if self.repDirFound == True:
            fullPathDir = os.listdir(os.path.join(Representation.workingDir, Representation.efmuContent, self.name))
            manifestFound = findDoc(fullPathDir, self.manifest)
        self.repManifestFound = manifestFound

        
    def compareID_in_manifest(self):
        with open(os.path.join(Representation.workingDir, Representation.efmuContent, self.name, self.manifest), mode="rU", encoding='utf-8-sig') as FILE:
            xml_file_lines = FILE.readlines()
    
        manifestTree = ET.fromstringlist(xml_file_lines, parser=LineNumberingParser()) 

        #modelManifest = manifestTree.findall('Manifest')
        id = manifestTree.get('id')
        #if len(modelManifest) > 0:
        #    id = modelManifest[0].get('id')
        
        if id != "":
            if id == self.manifestRefId:
                return True
        return False
    
    def compareChecksum(self):
        calculatedChecksum = sha_hash(os.path.join(Representation.workingDir, Representation.efmuContent, self.name, self.manifest))
        if self.checksum == calculatedChecksum:
            return True
        else:
            return False
            

    
    def validateManifest(self):
        if self.repManifestFound == True:
            if self.rep_schema_file != None:
                with open(os.path.join(Representation.workingDir, Representation.efmuContent, self.name, self.manifest), mode="rU", encoding='utf-8-sig') as FILE:
                    xml_file_lines = FILE.readlines()
                repManifestTree = ET.fromstringlist(xml_file_lines, parser=LineNumberingParser()) 
                repManifestSchema = ET.XMLSchema(file=os.path.join(Representation.workingDir, Representation.efmuContent, Representation.schemasFolder, self.kind, self.rep_schema_file))
                xmlManifestValidator = repManifestSchema.validate(repManifestTree)
                return xmlManifestValidator
        return False

