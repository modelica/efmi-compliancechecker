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

def validate_variables (manifest_vars, algorithm_code_PublicVars, algorithm_code_ProtectedVars):

    """
    This function validates all variables which are listed in the manifest xml file and the variables declared in the
    algorithm code file. So this function first checks if all variables listed in the xml manifest file are also declared
    in the alg file. It also checks if declared variables in the alg file are listed in the xml file. Moreover, it
    checks if variables types and causalities in the xml file match types and causalities in the alg file. 
    

    :param manifest_vars: Dictionary for all variables listed in the xml manifest file
    :param algorithm_code_vars: Dictionary for all variables declared in the alg file
    :return: a list of faced errors when running the mentioned validation 

    """

    
    problems =[]
    
    
    print ("\nValidating all variables:\n" )

    #check if all model variables in the manifest file are declared in the Algorithm code file
    allAlgorithm_code_vars = {**algorithm_code_PublicVars, **algorithm_code_ProtectedVars}
    problemsSize = len(problems)
    for key in manifest_vars.keys():
        if key not in allAlgorithm_code_vars.keys():
            # the variable (key) exists in the manifest file but it is not declared in the Algoirthm code file
            problems.append('  There is no declaration for the %s model variable in the Algorithm Code, although it exists under the ModelVariables in the manifest file' % key)

    #check if all variables which are declared in the Algorithm code file exist in the manifest file 
    for key in algorithm_code_PublicVars.keys():
        if key not in manifest_vars.keys():
            # the variable (key) is declared in the Algoirthm code file but it does not exists in the manifest file
            problems.append('  The variable %s is declared in the Algorithm Code but it does not exist under the ModelVariables in the manifest file' % key)
    
    if len(problems) == problemsSize:
        print("  All model variables in the manifest file are declared in the Algorithm Code file and vice versa")
    else:
        return problems

    #check if the type/causality of the model vraibles (in manifest) match the variables type/causality declared in the Algorithm code file
    problemsSize = len(problems)
    for key in manifest_vars.keys():
        manifest_type_caus = manifest_vars[key]
        algoirthm_type_caus = allAlgorithm_code_vars[key]
        #checking if the types match
        if manifest_type_caus.type != algoirthm_type_caus.type:
            problems.append('    The %s variable in the manifest is of type %s and the same variable is of type %s in the algorithm code: variable types must match' % (key, manifest_type_caus.type, algoirthm_type_caus.type))

        manifest_caus = manifest_type_caus.causality
        algorithm_caus = algoirthm_type_caus.causality

        if manifest_caus == 'tunableParameter' or manifest_caus == 'dependentParameter':
            if algorithm_caus != 'parameter':
                problems.append('    The blockCausality of the %s variable is %s and the causality of the same variable in the algorithm code is %s in the algorithm code: causalities must match (line %s in the Algorithm code)' % (key, manifest_caus, algorithm_caus, algoirthm_type_caus.line))
        else:
            if manifest_caus != algorithm_caus:
                problems.append('    The blockCausality of the %s variable is %s and the causality of the same variable in the algorithm code is %s: causalities must match (line %s in the Algorithm code)' % (key, manifest_caus, algorithm_caus, algoirthm_type_caus.line))
    
    if len(problems) == problemsSize:
        print("  All model variables types and blockCausalities in the manifest file match the types and causalities in the Algorithm Code file")

    
    return problems

