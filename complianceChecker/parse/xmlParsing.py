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

from lxml import etree as ET
from parse.larkTransformer import VarTypeCausality

def retrieveVariables(modelVariablesData, variablesElement, elementType="", retrieveArrays=True):

    if elementType == 'RealVariable':
        varType = 'Real'
    elif elementType == 'BooleanVariable':
        varType = 'Boolean'
    elif elementType == 'IntegerVariable':
        varType = 'Integer'
    else: 
        varType = ""
    
    if elementType == "":
        varTag = "Variable"
    else:
        varTag = elementType    
   
    for var in variablesElement.findall(varTag):
        
        dimensions = []
        varsCausalities = ["input", "output"]
        if elementType == "":
            varType = var.get('type')
            itemCausality = ""
        else:
            itemCausality = var.get('blockCausality')

        varTypeCaus = VarTypeCausality(varType, itemCausality, str(var.sourceline))
        dimensionsTags = var.findall("Dimensions")
        if (len(dimensionsTags) > 0):
            for a_dimension in dimensionsTags:
                allDimensions = a_dimension.findall("Dimension")
                if len(allDimensions) == 1:
                    dimensionSize = allDimensions[0].get('size')
                    if retrieveArrays == True:
                        for index in range(int(dimensionSize)):
                            varName = var.get('name') + "[" + str(index + 1) + "]"
                            modelVariablesData[varName] = varTypeCaus
                    elif itemCausality == "" or itemCausality in varsCausalities:
                        dimensions.append(dimensionSize)
                        
                elif len(allDimensions) == 2:
                    dimensionSize_1 = allDimensions[0].get('size')
                    dimensionSize_2 = allDimensions[1].get('size')
                    if retrieveArrays == True:
                        for index1 in range(int(dimensionSize_1)):
                            for index2 in range(int(dimensionSize_2)):
                                varName = var.get('name') + "[" + str(index1 + 1) + "," + str(index2 + 1) + "]"
                                modelVariablesData[varName] = varTypeCaus
                    elif itemCausality == "" or itemCausality in varsCausalities:
                        dimensions.append(dimensionSize_1)
                        dimensions.append(dimensionSize_2)
                elif len(allDimensions) == 3:
                    dimensionSize_1 = allDimensions[0].get('size')
                    dimensionSize_2 = allDimensions[1].get('size')
                    dimensionSize_3 = allDimensions[2].get('size')
                    if retrieveArrays == True:
                        for index1 in range(int(dimensionSize_1)):
                            for index2 in range(int(dimensionSize_2)):
                                for index3 in range(int(dimensionSize_3)):
                                    varName = var.get('name') + "[" + str(index1 + 1) + "," + str(index2 + 1) + "," + str(index3 + 1) + "]"
                                    modelVariablesData[varName] = varTypeCaus
                    elif itemCausality == "" or itemCausality in varsCausalities:
                        dimensions.append(dimensionSize_1)
                        dimensions.append(dimensionSize_2)
                        dimensions.append(dimensionSize_3)

        if retrieveArrays == True:
            modelVariablesData[var.get('name')] = varTypeCaus
        elif itemCausality == "" or itemCausality in varsCausalities:
            modelVariablesData[var.get('name')] = [varTypeCaus, dimensions]