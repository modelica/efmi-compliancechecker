
#This file is a part of the eFMI Compliance Checker which is a python open-source 
# library intended for checking the compliance of an eFMU with the standard specification

#Copyright © ESI ITI GmbH, 2021
               
#This program is a free software distributed WITHOUT ANY WARRANTY and the use is 
#completely at your own risk; it can be redistributed and/or modified under the 
#terms of the BSD 3-Clause license. For license conditions (including the 
#disclaimer of warranty) visit: https://opensource.org/licenses/BSD-3-Clause.

#ESI ITI GmbH, Zwinger-Forum, Schweriner Straße 1, 01067 Dresden, Germany


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