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

"""
The ``ComplianceChecker`` module
======================

>>> from ComplianceChecker import read_model_container

read_model_container
-------------------

- Extracts the eFMU archive and validate the extracted eFMU architecture against the specified eFMU architecure  
- Reads and parse the __content.xml file and locate the specified model representations in the file, then the
file is validated against the provided schema
- Reads the manifest xml file and validate it against the relevant schema, it also parse the file and reads all
files, variables and methods etrirs
- Retrieves the algorithm code files, validates them against the specified rules and reads all variables and
expressions included in the  functions
- Calls the validating functions on variables which compares the variables retrieved from xml file with
variables declared in algorithm code files
- Uses the validation functions that reads all expressions of the functions contained in the algorithm code
files then validate the expressions

"""

from collections import namedtuple
import shutil
from parse.grammars import grammar
from lark import Lark, Transformer, v_args, tree
from lark import exceptions
from parse.larkTransformer import ReadTree, VarTypeCausality
from parse.xmlParsing import retrieveVariables
from validate.validate_variables import validate_variables
from validate.validate_functions import validate_function
from validate.validate_manifest_references import validateReferences
from data.AlgorithmCodeData import Function
from data.Representations import Representation
from validate.crossCheck_manifest_vars import crossCheck_manifest_vars
from colorama import init, Fore, Back, Style
from lxml import etree as ET
import hashlib

BLOCKSIZE = 65536
ALGORITH_CODE_SCHEMA = 'efmiAlgorithmCodeManifest.xsd'
BEHAVIOR_MODEL_SCHEMA = 'efmiBehavioralModelManifest.xsd'
EQUATION_CODE_SCHEMA = 'efmiEquationCodeManifest.xsd'
BINARY_CODE_SCHEMA = 'efmiBinaryCodeManifest.xsd'
PRODUCTION_CODE_SCHEMA = 'efmiProductionCodeManifest.xsd'

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

init()


import logging
logging.basicConfig(level=logging.DEBUG)
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))

def sha_hash(fileName):
    hasher = hashlib.sha1()
    with open(fileName, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()

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


#variables = {}


def read_model_container(filename):
    import zipfile
    import os
    
    error = False
    modelRepresentations = []

    #The provided fmu name which should have fmu extension
    fmuName = os.path.basename(filename)
    
    print("\nChecking if the file name is an fmu archive")

    # Check if the provided file name is a valid archive with fmu extension, and it is not a folder
    if len(os.path.splitext(fmuName)) > 1:
        if os.path.splitext(fmuName)[1] != ".fmu":
            print('\033[91m' + "         The provided archive name is not valid 'fmu' archive, archive file extension should be fmu")
            print(Style.RESET_ALL)
            return 1
    else:
        print('\033[91m' + "         The provided archive name is not valid, you cannot provide a folder name as parameter. It has to be fmu archive")
        print(Style.RESET_ALL)
        return 1
    
    print('\033[92m' + "         The provided file is a valid 'fmu' archive")
    print(Style.RESET_ALL)
    
    # The name of the content directory of eFMUs is fixed to:
    efmuContentDir = "eFMU"

    # The full path of the provided fmu archive
    workingDir = os.getcwd()

    print("\nChecking if the fmu archive exist")
    if os.path.isfile(filename):
        print('\033[92m' + "         The fmu archive exists in the specified path")
    else:
        print('\033[91m' + "         The provided archive does not exist")
        return 1

    print(Style.RESET_ALL)

    pathTo_algorithmCode_dir = ""
    pathTo_equationCode_dir = ""

    # Unzip the fmu file, extracting will create a folder called eFMU
    print("Extracting the fmu archive  " + fmuName)
    def isDirInZip(zip, name):
        return any(x.startswith("%s/" % name.rstrip("/")) for x in zip.namelist())
    with zipfile.ZipFile(filename) as zip:
        if isDirInZip(zip, efmuContentDir):
            print('\033[92m' + "         The [" + efmuContentDir + "] folder is correctly contained in the fmu archive")
            for file in zip.namelist():
                    if file.startswith(efmuContentDir + "/"):
                        zip.extract(file, path=workingDir)
        else:
            print('\033[91m' + "         The [" + efmuContentDir + "] folder does not exist in the provided fmu archive")
            return 1
        
        if os.path.isdir(os.path.join(workingDir, efmuContentDir)):
            print('\033[92m' + "         [" + efmuContentDir + "] folder extracted correctly")
            print(Style.RESET_ALL)
        else:
            print('\033[91m' + "         Error during extracting the [" + efmuContentDir + "] folder")
            print(Style.RESET_ALL)
            return 1
    
    print("Checking the eFMU container architecture")

    pathTo_eFMU_dir = os.listdir(os.path.join(workingDir, efmuContentDir))
    contentFileExist = False
    manifestFileExist = False
    schemasFolderExist = False
    containerManifestExist = False
    algorithmCodeSchemasExist = False
    algorithmCodeManifestSchemaExist = False
    eqManifestFileExist = False
    manifestFileName = ""
    eqCodeManifestFile = ""

    # Check if the __content.xml file and schemas folder exist in the eFMU folder
    for file in pathTo_eFMU_dir: 
        if file == "__content.xml":
            print('\033[92m' + "         The __content.xml is correctly located in the", os.path.join(workingDir, efmuContentDir))
            contentFileExist = True
            contentFile = file
        if file == 'schemas':
            print('\033[92m' + "         The schemas folder is correctly contained in the ", os.path.join(workingDir, efmuContentDir))
            schemasFolderExist = True
            schemasFolder = file
        
    print(Style.RESET_ALL)
    
    algorithmCode_dirName = ""
    equationCode_dirName = ""
    # The __content.xml exists in the eFMU folder, then retrieve the manifest file name and the folder name of algorithm code 
    if contentFileExist == True:
        print("Parsing the __content.xml file")
        tree = ET.parse(os.path.join(workingDir, efmuContentDir, contentFile))
        root = tree.getroot()
        print('\033[92m' + "         __content.xml was parsed correctly")
        Representation.workingDir = workingDir
        Representation.efmuContent = efmuContentDir
        Representation.schemasFolderExist = schemasFolderExist
        if schemasFolderExist == True:
            Representation.schemasFolder = schemasFolder 
        for modelRepresentation in root.iter('ModelRepresentation'):
            repKind = modelRepresentation.get('kind')
            repName = modelRepresentation.get('name')
            repManifest = modelRepresentation.get('manifest').replace("./", "")
            repChecksum = modelRepresentation.get('checksum')
            repManifestRefId = modelRepresentation.get('manifestRefId')
            rep = Representation(repKind, repName, repManifest, repChecksum, repManifestRefId)
            rep.setRepDirFound()
            rep.setRepManifestFound()
            repSchemaFileExist = rep.setSechmaFile()
            rep.addManifestReferences()
            modelRepresentations.append(rep)

            if repKind == "AlgorithmCode":
                if algorithmCode_dirName != "":
                    error = True
                    print('\033[91m' + "         The eFMU has several Algorithm Code containers")
                    print(Style.RESET_ALL)
                algorithmCode_dirName = repName
                manifestFileName = repManifest
                #print('\033[92m' + "         The AlgorithmCode entity was found in the __content.xml file")
                if manifestFileName != "" and os.path.splitext(manifestFileName)[1] == ".xml":
                    pass
                    #print('\033[92m' + "         The manifest entity was found in the __content.xml file and the manifest file name is %s " % manifestFileName )
                else:
                    manifestFileName = ""
            elif repKind == "EquationCode":
                eqCodeManifestFile = repManifest
                equationCode_dirName = repName
                #print('\033[92m' + "         The AlgorithmCode entity was found in the __content.xml file")
                if eqCodeManifestFile != "" and os.path.splitext(eqCodeManifestFile)[1] == ".xml":
                    pass
                    #print('\033[92m' + "         The manifest entity was found in the __content.xml file and the manifest file name is %s " % manifestFileName )
                else:
                    eqCodeManifestFile = ""

        print(Style.RESET_ALL)    
    else:
        print('\033[91m' + "         The __content.xml file does not exist in the eFMU folder, this file is required")
        print(Style.RESET_ALL)
        return 1

    if (algorithmCode_dirName != ""):
        for file in pathTo_eFMU_dir: 
            if file == algorithmCode_dirName:
                #algorithmCodeFolderExist = True
                #print("The AlgorithmCode entity was found in the __content.xml file")
                pathTo_algorithmCode_dir = os.listdir(os.path.join(workingDir, efmuContentDir, algorithmCode_dirName))
                #print('\033[92m' + "         The AlgorithmCode folder exists in the", os.path.join(workingDir, efmuContentDir))           
    else:
        print ('\033[91m' + "         The AlgorithmCode folder does not exist, execution cannot be completed!")
        print(Style.RESET_ALL)
        return 1

    if (equationCode_dirName != ""):
        for file in pathTo_eFMU_dir: 
            if file == equationCode_dirName:
                #algorithmCodeFolderExist = True
                #print("The AlgorithmCode entity was found in the __content.xml file")
                pathTo_equationCode_dir = os.listdir(os.path.join(workingDir, efmuContentDir, equationCode_dirName))
                #print('\033[92m' + "         The AlgorithmCode folder exists in the", os.path.join(workingDir, efmuContentDir))

    # We read the content of the AlgorithmCode folder to find the manifest xml file
    if pathTo_algorithmCode_dir != "":
        #print("Reading the content of the AlgorithmCode folder")
        for file in pathTo_algorithmCode_dir:
            if file == manifestFileName:
                #print('\033[92m' + "         %s was found in the AlgorithmCode folder" % manifestFileName)
                manifestFileExist = True
        if manifestFileExist == False:
            error = True
            print ('\033[91m' + "         The Algorithm Code container's manifest is missing!")
            print(Style.RESET_ALL)
    else:
        print ('\033[91m' + "         The AlgorithmCode folder does not exist, execution cannot be completed!")
        print(Style.RESET_ALL)
        return 1
    
    if pathTo_equationCode_dir != "":
        #print("Reading the content of the AlgorithmCode folder")
        for file in pathTo_equationCode_dir:
            if file == eqCodeManifestFile:
                #print('\033[92m' + "         %s was found in the AlgorithmCode folder" % manifestFileName)
                eqManifestFileExist = True
    
    equationCodeVariablesData = {}
    algorithmCodeVariablesData = {}
    
    if eqManifestFileExist == True and manifestFileExist == True:
        with open(os.path.join(workingDir, efmuContentDir, equationCode_dirName, eqCodeManifestFile), mode="rU", encoding='utf-8-sig') as eq_FILE:
            eq_xml_file_lines = eq_FILE.readlines()
        
        eq_manifestTree = ET.fromstringlist(eq_xml_file_lines, parser=LineNumberingParser())

        equationCodeModelVariables = eq_manifestTree.findall('Variables')

        retrieveVariables(equationCodeVariablesData, equationCodeModelVariables[0], "", False)

        with open(os.path.join(workingDir, efmuContentDir, algorithmCode_dirName, manifestFileName), mode="rU", encoding='utf-8-sig') as FILE:
            xml_file_lines = FILE.readlines()
        
        manifestTree = ET.fromstringlist(xml_file_lines, parser=LineNumberingParser())

        modelVariables = manifestTree.findall('Variables')

        retrieveVariables(algorithmCodeVariablesData, modelVariables[0], 'RealVariable', False)
                
        retrieveVariables(algorithmCodeVariablesData, modelVariables[0], 'BooleanVariable', False)
       
        retrieveVariables(algorithmCodeVariablesData, modelVariables[0], 'IntegerVariable', False)

    # Running the consistency checks
    ManifestRefs_validate = validateReferences (modelRepresentations)
    print("Running the consistency check for all model representations in the __content.xml file")
    for rep in modelRepresentations:
        print("   - The %s model representation" % rep.getKind())
        
        if rep.compareID_in_manifest() == True:
            print('\033[92m' + "         The representation id matches the id in the manifest")
        else:
            error = True
            print('\033[91m' + "         The representation id does not match the id in the manifest")
        
        if rep.compareChecksum() == True:
            print('\033[92m' + "         The representation checksum matches the calculated checksum of the manifest")
        else:
            error = True
            print('\033[91m' + "         The representation checksum does not match the calculated checksum of the manifest")
        
        if rep.validateManifest() == True:
            print('\033[92m' + "         The %s manifest file was correctly validated against the relevant schema file" % rep.getManifest())
        else:
            error = True
            print('\033[91m' + "         The %s manifest file can not be validated against the relevant schema file" % rep.getManifest())
        
        if len(rep.getManifestReferences()) == 0:
            print('\033[92m' + "         The %s manifest file does not contain any manifest references" % rep.getManifest())
        elif rep.getName() not in ManifestRefs_validate.keys():
            print('\033[92m' + "         All manifest references in the %s manifest file are valid" % rep.getManifest())
        else:
            error = True
            errorMessages = ManifestRefs_validate[rep.getName()]
            for key in errorMessages.keys():
                s = errorMessages[key]
                print('\033[91m' + "         " + s)
    
        print(Style.RESET_ALL)
    
    print("Other consistency checks")
    eqRep = ""
    algRep = ""
    for rep in modelRepresentations:
        if rep.getName() == equationCode_dirName:
            eqRep = rep.getKind()
        elif rep.getName() == algorithmCode_dirName:
            algRep = rep.getKind()
    
    varsCrossCheckMsgs = {}
    crossCheck_manifest_vars(algorithmCodeVariablesData, equationCodeVariablesData, algRep, eqRep, varsCrossCheckMsgs)
    crossCheck_manifest_vars(equationCodeVariablesData, algorithmCodeVariablesData, eqRep, algRep, varsCrossCheckMsgs)

    if not varsCrossCheckMsgs:
        print('\033[92m' + "         All variables in the %s manifest are consistent with the variables in the %s manifest" % (algRep, eqRep))
    else:
        error = True
        for key in varsCrossCheckMsgs.keys():
            for key1 in varsCrossCheckMsgs[key].keys():
                print('\033[91m' + "         " + varsCrossCheckMsgs[key][key1])
    print(Style.RESET_ALL)
    
    # Trying to locate the efmiContainerManifest.xsd file in the schemas folder
    if schemasFolderExist == True:
        patheTo_schemas_folder = os.listdir(os.path.join(workingDir, efmuContentDir, schemasFolder))
        for file in patheTo_schemas_folder:
            if file == 'efmiContainerManifest.xsd':
                #print('\033[92m' + "         The efmiContainerManifest.xsd was found in the ", os.path.join(workingDir, efmuContentDir, schemasFolder))
                containerManifestExist = True
                efmuContainerManifest = file
            if file == 'AlgorithmCode':
                #print('\033[92m' + '         The AlgorithmCode folder correctly exists in the ', os.path.join(workingDir, efmuContentDir, schemasFolder))
                algorithmCodeSchemasExist = True
                algorithmCode_in_schemas = file
        #print(Style.RESET_ALL)
    else:
        print('\033[91m' + "         The schemas folder does not exist in the %s folder ", os.path.join(workingDir, efmuContentDir, schemasFolder, efmuContainerManifest))
        print(Style.RESET_ALL)
        return 1
    
    if containerManifestExist == True:
        print("Validating the __content.xml file against the efmiContainerManifest.xsd schema file")
        efmiContainerSchema = ET.XMLSchema(file=os.path.join(workingDir, efmuContentDir, schemasFolder, efmuContainerManifest))
        xmlContainerValidator = efmiContainerSchema.validate(root)
        if xmlContainerValidator == True:
            print('\033[92m' + "         The __content.xml file was validated correctly against the efmiContainerManifest.xsd schema file")
            print(Style.RESET_ALL)
        else:
            print('\033[91m' + "         The __content.xml file was not validated correctly against the efmiContainerManifest.xsd schema file")
            print(Style.RESET_ALL)
            return 1
    else:
        print('\033[91m' + "         Missing efmiContainerManifest.xsd XML Scheme file")
        print(Style.RESET_ALL)
        return 1
    
    modelVariablesData = {}
    # We parse the manifest.xml if it exists
    if manifestFileExist == True:
        #print("Parsing the %s file" % manifestFileName)

        with open(os.path.join(workingDir, efmuContentDir, algorithmCode_dirName, manifestFileName), mode="rU", encoding='utf-8-sig') as FILE:
            xml_file_lines = FILE.readlines()
        
        manifestTree = ET.fromstringlist(xml_file_lines, parser=LineNumberingParser()) 
        
        #print('\033[92m' + "         %s was parsed correctly" % manifestFileName)

        # search for efmiAlgorithmCodeManifest.xsd in the algorithmCode folder which is located in the schemas folder
        if algorithmCodeSchemasExist == True:
            path_to_algorithmCode_in_schemas = os.listdir(os.path.join(workingDir, efmuContentDir, schemasFolder, algorithmCode_in_schemas))
            for file in path_to_algorithmCode_in_schemas:
                if file == 'efmiAlgorithmCodeManifest.xsd':
                    algorithmCodeManifestSchemaExist = True
                    algorithmCode_manifest_schema = file
            if algorithmCodeManifestSchemaExist == True:
                #print('\033[92m' + "         The efmiAlgorithmCodeManifest.xsd schema file correctly located in the %s folder" % os.path.join(workingDir, efmuContentDir, schemasFolder, algorithmCode_in_schemas))
                algorithmCodeManifestSchema = ET.XMLSchema(file=os.path.join(workingDir, efmuContentDir, schemasFolder, algorithmCode_in_schemas, algorithmCode_manifest_schema))
                xmlManifestValidator = algorithmCodeManifestSchema.validate(manifestTree)
                #if xmlManifestValidator == True:
                    #print('\033[92m' + "         The %s file was validated correctly against the %s schema file" % (manifestFileName, algorithmCode_manifest_schema))
            else:
                print('\033[91m' + "         Missing efmiAlgorithmCodeManifest.xsd XML Scheme file")
                print(Style.RESET_ALL)
                return 1
        else:
            print('\033[91m' + "         Missing AlgorithmCode XML Scheme files directory")
            print(Style.RESET_ALL)
            return 1
        
        with open(os.path.join(workingDir, efmuContentDir, algorithmCode_dirName, manifestFileName), mode="rU", encoding='utf-8-sig') as FILE:
            xml_file_lines = FILE.readlines()

        # read the variables from the manifest xml file
        modelVariables = manifestTree.findall('Variables')

        if (len(modelVariables) == 0):
            print('\033[91m' + "         The %s manifest file does not contain any listed variables, cannot run any further checks" % manifestFileName)
            return 1

        retrieveVariables(modelVariablesData, modelVariables[0], 'RealVariable')
        retrieveVariables(modelVariablesData, modelVariables[0], 'BooleanVariable')
        retrieveVariables(modelVariablesData, modelVariables[0], 'IntegerVariable')    
        
        # extract the names of all alg file names listed in the manifest xml file and checking if these files exist in the AlgorithmCode folder
        # then the alg files are parsed and validated against the specified rules (in the grammr file) using the Lark parsing module which return 
        # a complete parse tree for algorithm code file
        # The ReadTree Transformer class is used which visits each node of the tree and run defined methods 
        # The latter utilization of the ReadTree can help to read and store all relevant data (variables and functions) from the alg file
        # The validate_variables function is used to check if all listed variables, in the manifest xml file, are also defined in the alg file
        # The latter also check if variable types and causalities match
        # validate_function can validate all expressions in each funtion by checking all variables in each expression are declared 
        # It also checks if tpyes of variables in each expression match
          
        print("Reading all 'alg' files from the %s file and checking if these files exist in the AlgorithmCode folder" % manifestFileName)
        
        files = manifestTree.findall('Files')
        
        for file in files[0].findall('File'):
            algorithmFileExist = False
            if os.path.splitext(file.get('name'))[1] == '.alg' and file.get('role') == 'Code':
                print('\033[92m' + "         The %s file is listed in the manifest.xml file" % file.get('name'))
                for f in pathTo_algorithmCode_dir:
                    if f == file.get('name'):
                        algorithmFileExist = True
                if algorithmFileExist == True:
                    print('\033[92m' + "         " + file.get('name'), "exists in the", os.path.join(workingDir, efmuContentDir, algorithmCode_dirName), "directory")
                    print(Style.RESET_ALL)
                    with open(os.path.join(workingDir, efmuContentDir, algorithmCode_dirName, file.get('name')), 'r') as f:
                        s = f.read()
                        algorithmCode_parser = Lark(grammar, start='start', lexer="dynamic_complete", propagate_positions=True)
                        try:
                            
                            print("Parsing the %s file " % file.get('name'))
                            tree = algorithmCode_parser.parse(s)
                            tree = ReadTree().transform(tree)
                            varList = ReadTree.variables()

                            protectedVarList = ReadTree.protectedVariables()
                   
                            problems = []
                            #allLocalVarList = {}
                            funcList = ReadTree.getFunctions()
                            #for x in funcList.keys():
                                #allLocalVarList = {**allLocalVarList, **funcList[x].getLocalVariables()}
                            problems += validate_variables(modelVariablesData, varList, protectedVarList)
                    
                            print ("\nfunctions\n")
                        
                            for x in funcList.keys():
                                localVarList = funcList[x].getLocalVariables()
                                problems += validate_function(funcList[x], {**varList, **localVarList, **protectedVarList} )
                            if problems:
                                error = True
                                print ('\033[91m' + "Errors:")
                                for k in range(len(problems)):
                                    print ('\033[91m' + problems[k]) 
                            print(Style.RESET_ALL)
                        except exceptions.UnexpectedCharacters as e:
                            error = True
                            print('\033[91m' + "         The %s file cannot be parsed, the message below contains the line number which does not comply with the required rules " % file.get('name'))
                            print('\033[91m' + "         " + str(e))
                else:
                    error = True
                    print (file.get('name'), "does not exist in the", os.path.join(workingDir, efmuContentDir, algorithmCode_dirName), "directory")

    # deleting the unzipped eFMU
    shutil.rmtree(os.path.join(workingDir, efmuContentDir))
    
    if error == True:
        return 1
    else:
        return 0
