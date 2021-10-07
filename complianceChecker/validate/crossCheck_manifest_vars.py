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
    