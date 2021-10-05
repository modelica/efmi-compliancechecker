#This file is a part of the eFMI Compliance Checker which is a python open-source 
# library intended for checking the compliance of an eFMU with the standard specification

#Copyright © ESI ITI GmbH, 2021
               
#This program is a free software distributed WITHOUT ANY WARRANTY and the use is 
#completely at your own risk; it can be redistributed and/or modified under the 
#terms of the BSD 3-Clause license. For license conditions (including the 
#disclaimer of warranty) visit: https://opensource.org/licenses/BSD-3-Clause.

#ESI ITI GmbH, Zwinger-Forum, Schweriner Straße 1, 01067 Dresden, Germany


from data.AlgorithmCodeData import Reference_constant, Reference_Reference, Reference_binary_operation, Reference_function_call        

def validate_function(function, varList):

    """
    This function validates a function in terms of contained variables and expressions:
    - It starts by checking if all variables contained in expressions are declared either locally in the function or
      globally in the alg file
    - Checks if types of variables in an expressions match. For example: 
        1- checks if the data type of the reference in a Reference_constant matches the data type of the constant
        2- Checks if data types of both references in Reference_Reference match
        3- Checks if the data type of the reference in a Reference_binary_operation matches the data types of all 
        references included in the BinaryOperation
        4- It also checks all Reference_if_expression, it checks if the conditions are valid (boolean) conditions and
        it also checks any included expressions

    :param function: The function object (of type Function)
    :param varList: List of global and local declared variables
    :return: a list of faced errors when running the mentioned validations 

    """


    problems = []
    
    print("The %s function\n" % function.name)
    #print ("  Validating all the expressions of the function:\n" )

    problemsSize = len (problems)
    problems += checkExprVarsDelaration(function.getExpressionsVariables(), varList, function.getLocalVariables())
    
    
    refToConstantList = function.getReference_to_constant()
    for key in refToConstantList.keys():
        refToCons = refToConstantList[key]
        problems += validate_refToConstants (refToCons, varList, function.getLocalVariables())

    #  list of all reference_to_reference
    refToReferenceList = function.getReference_to_reference()
    for key in refToReferenceList.keys():
        refToRef = refToReferenceList[key]
        problems += validate_refToReference(refToRef, varList, function.getLocalVariables())

    #  list of all reference_to_binaryOperation
    refToBinaryOperationsList = function.getBinary_operations ()
    for key in refToBinaryOperationsList.keys():
        refToBinaryOperation = refToBinaryOperationsList[key]
        problems += validate_refToBinaryOperation (refToBinaryOperation, varList, function.getLocalVariables())
    
    refToIfExpressionList = function.getReference_to_if_expression ()
    for key in refToIfExpressionList.keys():
        refToIfExpression = refToIfExpressionList[key]
        problems += validateRefToIfExpression(refToIfExpression, varList, function.getLocalVariables())
            #allEpressionsVars_list += retrieveIfExprVars(refToIfExpression.if_expression)
    if problemsSize == len (problems):
        print('   All variables of expressions are declared in the Algorithm code block')
        print('   Function expressions do not contain any errors\n')

    return problems


def validate_refToConstants (refToCons, varList, localVarList):
    problems = []
       
    varName = refToCons.reference
        
    varDeclared = varName in varList.keys()
    varDeclared_locally = varName in localVarList.keys()

    if varDeclared == True:
        varTypeCausality = varList[varName]
    elif varDeclared_locally == True:
        varTypeCausality = localVarList[varName]
    else:
        return problems
        
    if varTypeCausality.type != refToCons.constant:
        problems.append('  The value of the %s variable in the expression (line %s) does not match the declared variable type of %s ' % (varName, refToCons.line, varTypeCausality.type))
        return problems
    
        #print("  The validation of the (reference := constatn) statements passed without any errors\n")
    
    return problems


def checkExprVarsDelaration (expressionsVarsList, varList, localVarList):
    
    problems = []
    
    for exprVar in expressionsVarsList:
        #print (exprVar.name)
        varDeclared = exprVar.name in varList.keys()
        varDeclared_locally = exprVar.name in localVarList
        
        if not varDeclared and not varDeclared_locally:
            # variable exprVar.name which is contained in the expression is not declread globally or locally
            problems.append('  The variable %s which is contained in the expressions (line %s) is not declared anywhere in the Algorithm code block' % (exprVar.name, exprVar.line))
        
    return problems


def validate_refToReference (refToRef, varList, localVarList):
    
    problems = []
    '''
    print("      - Checking if all variables are declared in the Algorithm code block")
    print("      - Checking if all relevant variables types in both references match ")

    for key in refToReferenceList.keys():
        refToRef = refToReferenceList[key]'''

    varName_ref1 = refToRef.reference1
    varName_ref2 = refToRef.reference2

    varDeclared_ref1 = varName_ref1 in varList.keys()
    varDeclared_ref2 = varName_ref2 in varList.keys()

    varDeclared_locally_ref1 = varName_ref1 in localVarList.keys()
    varDeclared_locally_ref2 = varName_ref2 in localVarList.keys()


    if varDeclared_ref1 == True:
        varTypeCausality_ref1 = varList[varName_ref1]
    elif varDeclared_locally_ref1 == True:
        varTypeCausality_ref1 = localVarList[varName_ref1]
    else:
        return problems
            
    if varDeclared_ref2 == True:
        varTypeCausality_ref2 = varList[varName_ref2]
    elif varDeclared_locally_ref2 == True:
        varTypeCausality_ref2 = localVarList[varName_ref2]
    else:
        return problems
            
    if varTypeCausality_ref1.type != varTypeCausality_ref2.type:
        problems.append('  Expression in line %s contains variables type mismatch: The %s variable is of type %s and the variable %s is of type %s, types must match ' % (refToRef.line, varName_ref1, varTypeCausality_ref1.type, varName_ref2, varTypeCausality_ref2.type))
        return problems
            
    #print("  The validation of the (reference := reference) statements passed without any errors\n")

    return problems

def validate_refToBinaryOperation (refToBinaryOperation, varList, localVarList):

    problems = []
    varName_ref = refToBinaryOperation.reference

    varDeclared_ref = varName_ref in varList.keys()
        
    varDeclared_locally_ref = varName_ref in localVarList.keys()

    if varDeclared_ref == True:
        varTypeCausality_ref = varList[varName_ref]
    elif varDeclared_locally_ref == True:
        varTypeCausality_ref = localVarList[varName_ref]
    else:
        return problems

    #TODO I have to check if we can know the return type of a function call
    if (refToBinaryOperation.binaryOperation.expression1[0] == "function_call" \
            and refToBinaryOperation.binaryOperation.expression2[0] == "function_call"):
         return problems
    elif (refToBinaryOperation.binaryOperation.expression1[0] == "function_call"):
        if varTypeCausality_ref.type == "Boolean":
            isLogical_expr2 = isLogical_expression (refToBinaryOperation.binaryOperation.expression2, varList, localVarList)
            if (isLogical_expr2[0]):
                if refToBinaryOperation.binaryOperation.operation in ["and", "or"]:
                    return problems
                else:
                    problems.append('  Expression in line %s contains variables type mismatch: The %s variable is of type %s while the expression in the right is not of type %s, types must match ' % (refToBinaryOperation.line, varName_ref, varTypeCausality_ref.type, varTypeCausality_ref.type))
                    return problems
            else:
                if refToBinaryOperation.binaryOperation.operation in ["<=", ">=", "<>", "<", ">", "=="]:
                    return problems
                else:
                    problems.append('  Expression in line %s contains variables type mismatch: The %s variable is of type %s while the expression in the right is not of type %s, types must match ' % (refToBinaryOperation.line, varName_ref, varTypeCausality_ref.type, varTypeCausality_ref.type))
                    return problems
                    

        

    #elif (refToBinaryOperation.binaryOperation.expression2[0] == "function_call"):

    
    #print(varTypeCausality_ref)
    if varTypeCausality_ref.type == "Boolean":
        if isLogical_BinaryOperation(refToBinaryOperation.binaryOperation, varList, localVarList):
            return problems
        else:
            problems.append('  Expression in line %s contains variables type mismatch: The %s variable is of type %s while the expression in the right is not of type %s, types must match ' % (refToBinaryOperation.line, varName_ref, varTypeCausality_ref.type, varTypeCausality_ref.type))
            return problems

            
    #Adding all variables in the right hand binary operation to a list
    allVars_binaryOperation = retrieveVars_binaryOperation (refToBinaryOperation.binaryOperation)
    vars_binaryOperation = allVars_binaryOperation[0]
    realVars_realFunc_call = allVars_binaryOperation[1]
    integerVars_realFunc_call = allVars_binaryOperation[2]

    #print(vars_binaryOperation)
    for i in range(len(vars_binaryOperation)):
        #print(vars_binaryOperation[i])
        #Is the variable retireved from the binary operation declared?
        varDeclared_bin = vars_binaryOperation[i] in varList.keys()
                
        varDeclared_locally_bin = vars_binaryOperation[i] in localVarList.keys()
         
        if varDeclared_bin == True:
            varTypeCausality_bin = varList[vars_binaryOperation[i]]
        elif varDeclared_locally_bin == True:
            varTypeCausality_bin = localVarList[vars_binaryOperation[i]]
        else:
            return problems
                
        if varTypeCausality_ref.type != varTypeCausality_bin.type:
            if varTypeCausality_bin.type == "Real" and (vars_binaryOperation[i] in realVars_realFunc_call):
                pass
            #print ("The types of variables in the binary operation must match the types of variables in the LHS reference")
            else:
                problems.append('  Expression in line %s contains variables type mismatch: The %s variable is of type %s and the variable %s is of type %s, types must match ' % (refToBinaryOperation.line, varName_ref, varTypeCausality_ref.type, vars_binaryOperation[i], varTypeCausality_bin.type))
            #return problems
        
    return problems

def isLogical_BinaryOperation(binaryOperation, varList, localVarList):

    exp1 = binaryOperation.expression1
    exp2 = binaryOperation.expression2
    isLogicalEpre1 = isLogical_expression (exp1, varList, localVarList)
    isLogicalEpre2 = isLogical_expression (exp2, varList, localVarList)
    if isLogicalEpre1[0] and isLogicalEpre2[0]:
        return binaryOperation.operation in ["and", "or"]
    elif not isLogicalEpre1[0] and not isLogicalEpre2[0]:
        return binaryOperation.operation in ["<=", ">=", "<>", "<", ">", "=="]
    else:
        return False

    '''
    if binaryOperation.expression1[0] == "reference" and binaryOperation.expression2[0] == "reference":
        ref1 = binaryOperation.expression1[1]
        ref2 = binaryOperation.expression2[1]

        varDeclared_ref1 = ref1 in varList.keys()
        varDeclared_locally_ref1 = ref1 in localVarList.keys()

        varDeclared_ref2 = ref2 in varList.keys()
        varDeclared_locally_ref2 = ref2 in localVarList.keys()

        if varDeclared_ref1 == True:
            varTypeCausality_ref1 = varList[ref1]
        elif varDeclared_locally_ref1 == True:
            varTypeCausality_ref1 = localVarList[ref1]
        
        if varDeclared_ref2 == True:
            varTypeCausality_ref2 = varList[ref2]
        elif varDeclared_locally_ref2 == True:
            varTypeCausality_ref2 = localVarList[ref2]

        if varTypeCausality_ref1.type == "Boolean" and varTypeCausality_ref2.type == "Boolean":
            if binaryOperation.operation in ["and", "or"]:
                return True
        elif (varTypeCausality_ref1.type == "Real" and varTypeCausality_ref2.type == "Real") or \
                (varTypeCausality_ref1.type == "Integer" and varTypeCausality_ref2.type == "Integer"):
            return (binaryOperation.operation in ["<=", ">=", "<>", "<", ">", "=="])
        return False
    elif binaryOperation.expression1[0] == "binary_operation" and binaryOperation.expression2[0] == "binary_operation":
        if binaryOperation.operation in ["and", "or"]:
            return relational_logical_operation(binaryOperation.expression1[1], varList, localVarList) and relational_logical_operation(binaryOperation.expression2[1], varList, localVarList)
    elif binaryOperation.expression1[0] == "binary_operation" and binaryOperation.expression2[0] == "reference":
        ref = binaryOperation.expression2[1]
        varDeclared_ref = ref in varList.keys()
        varDeclared_locally_ref = ref in localVarList.keys()

        if varDeclared_ref == True:
            varTypeCausality_ref = varList[ref]
        elif varDeclared_locally_ref == True:
            varTypeCausality_ref = localVarList[ref]

        if relational_logical_operation(binaryOperation.expression1[1], varList, localVarList):
            if varTypeCausality_ref.type == "Boolean":
                return binaryOperation.operation in ["and", "or"]
        else:
            if varTypeCausality_ref.type != "Boolean":
                binaryOperation.operation in ["<=", ">=", "<>", "<", ">", "=="]

    elif binaryOperation.expression1[0] == "reference" and binaryOperation.expression2[0] == "constant":
        ref = binaryOperation.expression1[1]
        varDeclared_ref = ref in varList.keys()
        varDeclared_locally_ref = ref in localVarList.keys()

        if varDeclared_ref == True:
            varTypeCausality_ref = varList[ref]
        elif varDeclared_locally_ref == True:
            varTypeCausality_ref = localVarList[ref]
        
        if varTypeCausality_ref.type == "Boolean":
            if binaryOperation.expression2[1] == "boolean":
                return binaryOperation.operation in ["and", "or"]
        else:
            if binaryOperation.expression2[1] != "boolean":
                return binaryOperation.operation in ["<=", ">=", "<>", "<", ">", "=="]
    elif binaryOperation.expression1 == "reference" and binaryOperation.expression2[0] == "if_expression":
        ref = binaryOperation.expression1[1]
        varDeclared_ref = ref in varList.keys()
        varDeclared_locally_ref = ref in localVarList.keys()

        if varDeclared_ref == True:
            varTypeCausality_ref = varList[ref]
        elif varDeclared_locally_ref == True:
            varTypeCausality_ref = localVarList[ref]
        
        #if varTypeCausality_ref.type == "Boolean":
            #if 
        

    
    # TODO elif more cases to be added here

    return False
    '''




def validate_refToFunctionCall (refToFunctionCall, varList, localVarList):

    problems = []

    varName_ref = refToFunctionCall.reference

    varDeclared_ref = varName_ref in varList.keys()
        
    varDeclared_locally_ref = varName_ref in localVarList.keys()

    if varDeclared_ref == True:
        varTypeCausality_ref = varList[varName_ref]
    elif varDeclared_locally_ref == True:
        varTypeCausality_ref = localVarList[varName_ref]
    else:
        return problems

            
    #Adding all variables in the right hand binary operation to a list

     
    allVars_binaryOperation = (retrieveVars_functionCall (refToFunctionCall.functionCall))
    vars_FunctionCall = allVars_binaryOperation[0]
    realVars_realFunc_call = allVars_binaryOperation[1]
    integerVars_realFunc_call = allVars_binaryOperation[2]
    #print ("all variables  ", vars_binaryOperation)        
    for i in range(len(vars_FunctionCall)):
        #Is the variable retireved from the binary operation declared?
        #print(vars_FunctionCall[i])
        varDeclared_func = vars_FunctionCall[i] in varList.keys()
                
        varDeclared_locally_func = vars_FunctionCall[i] in localVarList.keys()
                                
        if varDeclared_func == True:
            varTypeCausality_func = varList[vars_FunctionCall[i]]
        elif varDeclared_locally_func == True:
            varTypeCausality_func = localVarList[vars_FunctionCall[i]]
        else:
            return problems
                
                    
        if varTypeCausality_ref.type != varTypeCausality_func.type:
            #print ("The types of variables in the binary operation must match the types of variables in the LHS reference")
            if varTypeCausality_ref.type == "Real" and (vars_FunctionCall[i] in realVars_realFunc_call):
                pass
            else:
                problems.append('Expression in line %s contains variables type mismatch: The %s variable is of type %s and the variable %s is of type %s, types must match ' % (refToFunctionCall.line, varName_ref, varTypeCausality_ref.type, vars_FunctionCall[i], varTypeCausality_func.type))
            #return problems
        
    return problems
                    

def validateRefToIfExpression (refToIfExpression, varList, localVarList):
    
    problems = []
    
    ifExpression = refToIfExpression.if_expression

    condtionsList = ifExpression.getConditions()

    problems += validateAllConditions_ifExpr(condtionsList, varList, localVarList)
    
    
    expressionsList = ifExpression.getExpressions()
    problems += validateAllExprs_ifExpr (expressionsList, refToIfExpression.reference, varList, localVarList)

    elseExpressionsList = ifExpression.getElseExpr()
    problems += validateAllExprs_ifExpr (elseExpressionsList, refToIfExpression.reference, varList, localVarList)

    elseIfExpressionsList = ifExpression.getElseIfs()
    elseIfConditions = {}
    elseIfExprs = {}

    for key in elseIfExpressionsList.keys():
        cond = 'cond' + key
        expre = 'expre' + key
        elseIfConditions[cond] = elseIfExpressionsList[key].condition
        elseIfExprs[expre] = elseIfExpressionsList[key].expression
    
    problems += validateAllConditions_ifExpr(elseIfConditions, varList, localVarList)
    problems += validateAllExprs_ifExpr (elseIfExprs, refToIfExpression.reference, varList, localVarList)
            
    return problems

def validateAllConditions_ifExpr(condtionsList, varList, localVarList):
    problems = []
    for key in condtionsList.keys():
        expre = condtionsList[key]
        isLogicalExpre = isLogical_expression (expre, varList, localVarList)
        if not isLogicalExpre[0]:
            returnedProblems = isLogicalExpre[1]
            for i in range(len(returnedProblems)):
                problems.append ("Evaluating the condition of the if_expression: " + returnedProblems[i])
        '''
        if expre[0] == 'reference':
            varName_ref = expre[1]

            varDeclared_ref = varName_ref in varList.keys()
        
            varDeclared_locally_ref = varName_ref in localVarList.keys()
                
            if varDeclared_ref == True:
                varTypeCausality_ref = varList[varName_ref]
            elif varDeclared_locally_ref:
                varTypeCausality_ref = localVarList[varName_ref]
            else:
                return problems
                
            if varTypeCausality_ref.type != "Boolean":
                problems.append('  The condition of the if_expression (in line %s) is not valid because the %s variable is not of type boolean' % (expre[2], varName_ref))

            
        elif expre[0] == 'binary_operation':

            problems += ValidateVars_binaryOperation (expre, varList, localVarList)
        
        # elif TODO'''

    
    return problems

def validateAllExprs_ifExpr (expressionsList, ref, varList, localVarList):
    problems = []
    for key in expressionsList.keys():
        expre = expressionsList[key]
        if expre[0] == 'constant':
            refToCons = Reference_constant (ref, expre[1], expre[2])
            problems += validate_refToConstants (refToCons, varList, localVarList)
        elif expre[0] == 'reference':
            refToRef = Reference_Reference(ref, expre[1], expre[2])
            problems += validate_refToReference(refToRef, varList, localVarList)
        elif expre[0] == 'binary_operation':
            refToBinary = Reference_binary_operation(ref, expre[1], expre[2])
            problems += validate_refToBinaryOperation(refToBinary, varList, localVarList)
        elif expre[0] == 'function_call':
            refToFunctionCall = Reference_function_call(ref, expre[1], expre[2])
            problems += validate_refToFunctionCall(refToFunctionCall, varList, localVarList)  
            
    return problems


'''
def ValidateVars_binaryOperation (binaryOperation, varList, localVarList):
    problems = []

    vars_binaryOperation = retrieveVars_binaryOperation (binaryOperation[1])

    i = 1
    if len(vars_binaryOperation) > 1:

        while i in range(len(vars_binaryOperation)):
            #Is the variable retireved from the binary operation declared?
            varDeclared_1 = vars_binaryOperation[i-1] in varList.keys()
                
            varDeclared_locally_1 = vars_binaryOperation[i-1] in localVarList.keys()

            varDeclared_2 = vars_binaryOperation[i] in varList.keys()
                
            varDeclared_locally_2 = vars_binaryOperation[i] in localVarList.keys()
                
            if varDeclared_1 == True:
                varTypeCausality_1 = varList[vars_binaryOperation[i-1]]
            elif varDeclared_locally_1 == True:
                varTypeCausality_1 = localVarList[vars_binaryOperation[i-1]]
            else:
                return problems
                    
            if varDeclared_2 == True:
                varTypeCausality_2 = varList[vars_binaryOperation[i]]
            elif varDeclared_locally_2 == True:
                varTypeCausality_2 = localVarList[vars_binaryOperation[i]]
            else:
                return problems

            if varTypeCausality_1.type != varTypeCausality_2.type:
                #print ("The types of variables in the binary operation must match the types of variables in the LHS reference")
                problems.append('Expression in line %s contains variables type mismatch: The %s variable is of type %s and the variable %s is of type %s, types must match ' % (binaryOperation[2], vars_binaryOperation[i-1], varTypeCausality_1.type, vars_binaryOperation[i], varTypeCausality_2.type))
                return problems
                    
            i += 1
    
    return problems 
'''


def retrieveIfExprVars (ifExpression):
    
    varList = []
    '''condtionsList = ifExpression.getConditions()

    if len(condtionsList) > 0:
        for key in condtionsList.keys():
            varList += retrieveVars_expression(condtionsList[key])
    '''

    expressionsList = ifExpression.getExpressions()

    for key in expressionsList.keys():
        expre = expressionsList[key]
        varList += retrieveVars_expression(expre)[0]
    

    elseExpressionsList = ifExpression.getElseExpr()
    for key in elseExpressionsList.keys():
        expre = elseExpressionsList[key]
        varList += retrieveVars_expression(expre)[0]

    elseIfExpressionsList = ifExpression.getElseIfs()
    for key in elseIfExpressionsList.keys():
        expre = elseIfExpressionsList[key]
        varList += retrieveVars_expression(expre)[0]
        
    return varList
            


def retrieveVars_functionCall(functionCall):
    varList= []
    realFunc = []
    integerFunc = []
    temp = []
    exprsList = functionCall.expression
    for i in range(len(exprsList)):
        temp += retrieveVars_expression(exprsList[i])
        varList += temp[0]
        if functionCall.name == "real" or functionCall.name == "sqrt":
            realFunc += temp[0]
        elif functionCall.name == "integer":
            integerFunc += temp[0]

    return [varList, realFunc, integerFunc]

def retrieveVars_expression(expression):
    allVarList = []
    varList = []
    realFunc = []
    integerFunc = []
    if expression[0] == 'reference':
        varList.append(expression[1])
    elif expression[0] == 'binary_operation':
        allVarList += retrieveVars_binaryOperation(expression[1])
        varList += allVarList[0]
        realFunc += allVarList[1]
        integerFunc += allVarList[2]
    elif expression[0] == 'if_expression':
        varList += retrieveIfExprVars(expression[1])
    elif expression[0] == 'function_call':
        allVarList += retrieveVars_functionCall(expression[1])
        varList += allVarList[0]
        realFunc += allVarList[1]
        integerFunc += allVarList[2]
    elif expression[0] == 'unary_operation':
        if expression[1] == 'function_call':
            allVarList += retrieveVars_functionCall(expression[2])
            varList += allVarList[0]
            realFunc += allVarList[1]
            integerFunc += allVarList[2]
        elif expression[1] == 'reference':
            varList.append(expression[2])
        elif expression[1] == 'binary_operation':
            allVarList += retrieveVars_binaryOperation(expression[2])
            varList += allVarList[0]
            realFunc += allVarList[1]
            integerFunc += allVarList[2]
        elif expression[1] == 'if_expression':
            varList += retrieveIfExprVars(expression[2])
            
    return [varList, realFunc, integerFunc]



def retrieveVars_binaryOperation (binaryOperation):
    varsList = []
    allVarList1 = []
    allVarList2 = []
    realFunc = []
    integerFunc = []
    expr1 = binaryOperation.expression1
    expr2 = binaryOperation.expression2
    allVarList1 += retrieveVars_expression(expr1)
    allVarList2 += retrieveVars_expression(expr2)
    varsList += allVarList1[0]
    varsList += allVarList2[0]

    realFunc += allVarList1[1]
    realFunc += allVarList2[1]

    integerFunc += allVarList1[2]
    integerFunc += allVarList2[2]
    '''
    if expr1[0] == "reference":
        varsList.append(expr1[1])
    elif expr1[0] == "binary_operation":
        varsList += retrieveVars_binaryOperation(expr1[1])
    
    if expr2[0] == "reference":
        varsList.append(expr2[1])
    elif expr2[0] == "binary_operation":
        varsList += retrieveVars_binaryOperation(expr2[1])
    '''
    
    return [varsList, realFunc, integerFunc]


def isLogical_expression (expression, varList, localVarList):
    
    problems = []
    isBooleanExpre = False
    isLogical = True


    if expression[0] == "constant":
        isBooleanExpre = (expression[1] == "Boolean")
        if not isBooleanExpre:
            isLogical = False
            problems.append('Expression in line %s cannot be evaluated as a logical expression: The constant %s is not of type boolean ' % (expression[3] , expression[2]))
    elif expression[0] == "reference":
        ref = expression[1]
        varDeclared_ref = ref in varList.keys()
        varDeclared_locally_ref = ref in localVarList.keys()
        if varDeclared_ref == True:
            varTypeCausality_ref = varList[ref]
        elif varDeclared_locally_ref == True:
            varTypeCausality_ref = localVarList[ref]
        
        isBooleanExpre = (varTypeCausality_ref.type == "Boolean")
        if not isBooleanExpre:
            isLogical = False
            problems.append('Expression in line %s cannot be evaluated as a logical expression: The reference %s is not of type boolean ' % (expression[2] , expression[1]))
    elif expression[0] == "if_expression":
        isBooleanExpre = True
        ifExpression = expression[1]
        majorExpressions = ifExpression.getExpressions()
        if majorExpressions:
            for x in majorExpressions.keys():
                isLogicalExpre = isLogical_expression (majorExpressions[x], varList, localVarList)
                isBooleanExpre = isLogicalExpre[0]
                if not isBooleanExpre:
                    isLogical = False
                    problems += isLogicalExpre[1]
        elseExpressions = ifExpression.getElseExpr()
        if elseExpressions:
            for x in elseExpressions.keys():
                isLogicalExpre = isLogical_expression (elseExpressions[x], varList, localVarList)
                isBooleanExpre = isLogicalExpre[0]
                if not isBooleanExpre:
                    isLogical = False
                    problems += isLogicalExpre[1]
        elseifStatements = ifExpression.getElseIfs()
        if elseifStatements:
            for x in elseifStatements.keys():
                isLogicalExpre = isLogical_expression (elseifStatements[x][1], varList, localVarList)
                isBooleanExpre = isLogicalExpre[0]
                if not isBooleanExpre:
                    isLogical = False
                    problems += isLogicalExpre[1]
    elif expression[0] == "binary_operation":
        binaryOperation = expression[1]
        isLogical_expre1 = isLogical_expression (binaryOperation[0], varList, localVarList)
        isLogical_expre2 = isLogical_expression (binaryOperation[2], varList, localVarList)
        if not isLogical_expre1[0]:
            if not isLogical_expre2[0]:
                isBooleanExpre = (binaryOperation[1] in ["<=", ">=", "<>", "<", ">", "=="])
                if not isBooleanExpre:
                    isLogical = False
                    problems.append('The binary operation in line %s cannot be evaluated as a logical expression ' % expression[2])
            else:
                isLogical = False
                problems.append('The binary operation in line %s cannot be evaluated as a logical expression ' % expression[2])
        else:

            if isLogical_expre2[0]:
                isBooleanExpre = (binaryOperation[1] in ["and", "or"])
                if not isBooleanExpre:
                    isLogical = False
                    problems.append('The binary operation in line %s cannot be evaluated as a logical expression ' % expression[2])
            else:
                isLogical = False
                problems.append('The binary operation in line %s cannot be evaluated as a logical expression ' % expression[2])
    elif expression[0] == "function_call":
        isBooleanExpre = True # TODO should try to find out if there is a way to check the return type of called functions
    else: #expression[0] == "unary_operation":
        if expression[3] == "not":
            isLogicalExpre = isLogical_expression (expression[2], varList, localVarList)
            isBooleanExpre = isLogicalExpre[0]
            if not isBooleanExpre:
                isLogical = False
                problems.append('The unary operation in line %s cannot be evaluated as a logical expression ' % expression[2])
        else:
            isLogical = False
            problems.append('The unary operation in line %s cannot be evaluated as a logical expression ' % expression[2])
    
    return[isLogical, problems]
    




