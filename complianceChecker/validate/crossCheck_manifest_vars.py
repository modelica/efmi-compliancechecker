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

def addEntry(key1, key2, msg, dic):
    if key1 in dic.keys():
        if key2 in dic[key1].keys():
            pass
        else:
            dic[key1].updat({key2 : msg})
    else:
        dic[key1] = {key2 : msg}


def crossCheck_manifest_vars(rep1_vars, rep2_vars, rep1, rep2, messages):
    #messages = {}
    for key in rep1_vars.keys():
        if key in rep2_vars.keys():
            varTypeCausDimen_rep1 = rep1_vars[key]
            varTypeCausDimen_rep2 = rep2_vars[key]
            if varTypeCausDimen_rep1[0].type != varTypeCausDimen_rep2[0].type:
                s = "The type of the " + key + " variable from the "  + rep1 + " manifest does not match the type of the same variable in the " + rep2 + " manifest"
                addEntry(key, "type", s, messages)

                #essages[key] = s
            if len(varTypeCausDimen_rep1[1]) != len(varTypeCausDimen_rep2[1]):
                s = "The Dimensions of the " + key + " variable from the "  + rep1 + " manifest does not match the dimensions of the same variable in the " + rep2 + " manifest"
                addEntry(key, "dimension", s, messages)
            elif len(varTypeCausDimen_rep1[1]) > 0:
                if len(varTypeCausDimen_rep2[1]) > 0:
                    for i in range(len(varTypeCausDimen_rep1[1])):
                        if varTypeCausDimen_rep1[1][i] != varTypeCausDimen_rep2[1][i]:
                            s = "The Dimensions of the " + key + " variable from the "  + rep1 + " manifest does not match the dimensions of the same variable in the " + rep2 + " manifest"
                            addEntry(key, "dimension", s, messages)
                            break
        else:
            s = "The " + key + " variable from the "  + rep1 + " manifest is not listed in the " + rep2 + " manifest"
            addEntry(key, "missing", s, messages)
    