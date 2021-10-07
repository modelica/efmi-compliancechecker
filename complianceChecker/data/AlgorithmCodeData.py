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

from collections import namedtuple

"""
The following tuples are defined to help store all types of expressions.
For example, the Reference_constant tuple is defined to address the single_assignment of type (reference := constant). So it
contains three elements: reference, constant and the line number in the alg file. More examples are listed below:

- Reference_if_expression: contains reference, if_expression which is of type If_Expression and finally the line number
- FunctionCall: includes a name of the function, expression which contains all parameter expressions (see the function_call rule)
  and finally the line number
- ElseIf: contains a condition (which is an expression rule), expression to be visited when the condition is true and 
  finally the line number

"""

Reference_constant = namedtuple('Reference_constant', ['reference', 'constant', 'line'])
Reference_Reference = namedtuple('Reference_Reference', ['reference1', 'reference2', 'line'])
#MinMax_Expressions = namedtuple('MinMax_Expressions', ['references', 'types', 'vals'])
Reference_if_expression = namedtuple('Reference_if_expression', ['reference', 'if_expression', 'line'])
BinaryOperation = namedtuple('BinaryOperation', ['expression1', 'operation', 'expression2', 'line'])
Reference_binary_operation = namedtuple('Reference_binary_operation', ['reference', 'binaryOperation', 'line'])
VarTypeCausality = namedtuple('VarTypeCausality', ['type', 'causality', 'line'])
ExpressionVariable = namedtuple('ExpressionVariable', ['name', 'line'])
ElseIf = namedtuple ('ElseIf', ['condition', 'expression', 'line'])
FunctionCall = namedtuple('FunctionCall', ['name', 'expression', 'line'])
UnaryOperation = namedtuple('UnaryOperation', ['operation', 'expression', 'line'])
Reference_function_call = namedtuple('Reference_function_call', ['reference', 'functionCall', 'line'])

class If_Expression:

    """
    Class If_Expression represents the if_expression rule, it contains a number of properties to store all elements of the
    if_expression. These properties include:

    - conditions: stores the expression which act as a condition after the "if" keyword (see the if_expression rule)
    - elseIf: contains all the elseif_expression expressions
    - expression: includes the expression which is visited when the condition is true
    - elseExpr: contains the expression which is visited when the condition is false

    """

    def __init__(self):
        self.conditions = {}
        self.elseIf = {}
        self.expression = {}
        self.elseExpr = {}
        self.condCounter = 0
        self.elseIfCounter = 0
        self.expressionCounter = 0
        self.elseCounter = 0

    
    def addCondition (self, condition):
        self.condCounter += 1
        cond = 'condition' + str(self.condCounter)
        self.conditions[cond] = condition
    
    def addElseIF(self, condition, expression):
        self.elseIfCounter += 1
        elseIfKey = 'elseIf' + str(self.elseIfCounter)
        elseIfVal = ElseIf(condition, expression, condition[2])
        self.elseIf[elseIfKey] = elseIfVal
    
    def addExpression (self, expression):
        self.expressionCounter += 1
        expr = 'expression' + str(self.expressionCounter)
        self.expression[expr] = expression
    
    def addElseExpression (self, expression):
        self.elseCounter += 1
        expr = 'elseExpr' + str(self.elseCounter)
        self.elseExpr[expr] = expression
    
    def getConditions (self):
        return self.conditions
    
    def getElseIfs (self):
        return self.elseIf

    def getExpressions (self):
        return self.expression
    
    def getElseExpr (self):
        return self.elseExpr
    
    def toString (self):
        ifString = []
        str1 = 'if'
        ifString.append(str1)
        for x in self.conditions.keys():
            #ifString += ' ' + self.conditions[x][1]
            str1 = self.conditions[x][1]
            ifString.append(str1)
        str1 = 'then'
        ifString.append(str1)
        for x in self.expression.keys():
            str1 = self.expression[x][1]
            ifString.append(str1) 
        if len(self.elseIf) > 0:
            str1 = 'elseif'
            ifString.append(str1)
            for x in self.elseIf.keys():
                str1 = self.elseIf[x].condition
                ifString.append(str1)
            for x in self.elseIf.keys():
                str1 = self.elseIf[x].expression
                ifString.append(str1)
        if len(self.elseExpr) > 0:
            str1 = 'else'
            ifString.append(str1)
            for x in self.elseExpr.keys():
                #print (self.elseExpr[x][1].expression1[1])#, self.elseExpr[x][1].operation, self.elseExpr[x][1].expression2[1])
                str1 = "exp1 " + str(self.elseExpr[x][1].expression1[1]) + " operation " + str(self.elseExpr[x][1].operation) + " exp2 " + str(self.elseExpr[x][1].expression2[1])
                ifString.append(str1)
        return ifString


        


class Function:

    """
    Class Function represents the function_declaration rule, it contains a number of properties to store all local variables 
    and expressions of the function_declaration. These properties include:

    - declaredLocalVars: stores the local declared variables
    - expressionsVariables: a list of all references contained in expressions of the function
    - reference_to_constant: includes all Reference_constant expressions which are contained in the function
    - reference_to_if_expression: contains all Reference_if_expression expressions
    - binaryOperations: stores all Reference_binary_operation expressions
    - and others, all hold proper names that explain the purpose 

    """
    def __init__(self):
        self.declaredLocalVars = {}
        self.expressionsVariables = []
        self.reference_to_constant = {}
        self.reference_to_if_expression = {}
        self.reference_to_reference = {}
        self.reference_to_functionCall = {}
        #self.single_assignment = {}
        self.binaryOperations = {}
        self.method = False
        self.function = False
        self.refToConstCounter = 0
        self.refToBinaryOperCounter = 0
        self.refToRefCounter = 0
        self.refToIfExprCounter = 0
        self.refToFunctionCallCounter = 0
    
    def setName (self, name):
        self.name = name
    
    def setFunctionMethod(self, methodFunction):
        if methodFunction == 'function':
            self.function = True
        else:
            self.method = True
    
    def addDeclaredLocalVars (self, varCausality, nameAndType, line):
        #varCausality = node[i].children[j].children[0].value
        varTypeCaus = VarTypeCausality(nameAndType[1], varCausality, line)
        if len(nameAndType[0]) == 1:
            self.declaredLocalVars[nameAndType[0][0]] = varTypeCaus
        else:
            for i in range(len(nameAndType[0])):
                self.declaredLocalVars[nameAndType[0][i]] = varTypeCaus



    def addReference_to_constant (self, refConstant):
        self.refToConstCounter += 1
        statement = 'refToConst' + str(self.refToConstCounter)
        exprVar= ExpressionVariable (refConstant.reference, refConstant.line)
        #print (" adding from Reference_to_constant  " + exprVar.name)
        self.expressionsVariables.append(exprVar)
        self.reference_to_constant[statement] = refConstant

    def addReference_to_binaryOperation(self, refToBinaryOperation):
        self.refToBinaryOperCounter += 1
        statement = 'refToBinaryOperation' + str(self.refToBinaryOperCounter)
        #binaryOperation = BinaryOperation(expression1, operation, expression2)
        exprVar= ExpressionVariable (refToBinaryOperation.reference, refToBinaryOperation.line)
        
        self.expressionsVariables.append(exprVar)
        self.expressionsVariables += self.__retrieveVars_binaryOperation(refToBinaryOperation.binaryOperation)
        
        
        self.binaryOperations[statement] = refToBinaryOperation

    def addReference_to_reference(self, refToRef):
        self.refToRefCounter += 1
        statement = 'refToRef' + str(self.refToRefCounter)
        exprVar1= ExpressionVariable (refToRef.reference1, refToRef.line)
        self.expressionsVariables.append(exprVar1)
        exprVar2= ExpressionVariable (refToRef.reference2, refToRef.line)
        self.expressionsVariables.append(exprVar2)
        self.reference_to_reference[statement] = refToRef
    
    def addReference_to_ifExpression (self, refToIfExpression):
        self.refToIfExprCounter += 1
        statement = 'refToIfExpr' + str(self.refToIfExprCounter)
        exprVar= ExpressionVariable (refToIfExpression.reference, refToIfExpression.line)
        self.expressionsVariables.append(exprVar)
        self.expressionsVariables += self.__retrieveIfExprVars(refToIfExpression.if_expression)

        self.reference_to_if_expression[statement] = refToIfExpression
    
    def addReference_to_functionCall (self, refToFunctionCall):
        self.refToFunctionCallCounter += 1
        statement = 'refToIfExpr' + str(self.refToFunctionCallCounter)
        exprVar= ExpressionVariable (refToFunctionCall.reference, refToFunctionCall.line)
        self.expressionsVariables.append(exprVar)
        
        self.expressionsVariables += self.__retrieveVars_functionCall(refToFunctionCall.functionCall)
        self.reference_to_functionCall[statement] = refToFunctionCall
        
    
    def addExpressionVar (self, exprvar):
        self.expressionsVariables.append(exprvar)

    def __retrieveIfExprVars (self, ifExpression):
    
        varList = []
        condtionsList = ifExpression.getConditions() 
        for key in condtionsList.keys():
            varList += self.__retrieveVars_expression(condtionsList[key])
        
        expressionsList = ifExpression.getExpressions()
        for key in expressionsList.keys():
            varList += self.__retrieveVars_expression(expressionsList[key])
        
        elseifList = ifExpression.getElseIfs()
        for key in elseifList.keys():
            varList += self.__retrieveVars_expression(elseifList[key].condition)
            varList += self.__retrieveVars_expression(elseifList[key].expression)
        
        elseExpressions = ifExpression.getElseExpr()
        for key in elseExpressions.keys():
            varList += self.__retrieveVars_expression(elseExpressions[key])

        return varList
        

    
    def __retrieveVars_expression(self, expression):
        varList = []
        #print(expression)
        if expression[0] == 'reference':
            exprVar= ExpressionVariable (expression[1], expression[2])
            varList.append(exprVar)
        elif expression[0] == 'binary_operation':
            varList += self.__retrieveVars_binaryOperation(expression[1])
        elif expression[0] == 'if_expression':
            varList += self.__retrieveIfExprVars(expression[1])
        elif expression[0] == 'function_call':
            varList += self.__retrieveVars_functionCall(expression[1])
        elif expression[0] == 'unary_operation':
            if expression[1] == 'function_call':
                varList += self.__retrieveVars_functionCall(expression[2])
            elif expression[1] == 'reference':
                exprVar= ExpressionVariable (expression[2], expression[3])
                varList.append(exprVar)
            elif expression[1] == 'binary_operation':
                
                varList += self.__retrieveVars_binaryOperation(expression[2])
            elif expression[1] == 'if_expression':
                varList += self.__retrieveVars_functionCall(expression[2])
                  
        return varList
    
    def __retrieveVars_functionCall(self, functionCall):
        varList= []
        exprsList = functionCall.expression
        for i in range(len(exprsList)):
            varList += self.__retrieveVars_expression(exprsList[i])
    
        return varList

    def __retrieveVars_binaryOperation (self, binaryOperation):
        varsList = []
        
        expr1 = binaryOperation.expression1
        expr2 = binaryOperation.expression2

       
        if expr1[0] == "reference":
            exprVar= ExpressionVariable (expr1[1], binaryOperation.line)
            varsList.append(exprVar)
        elif expr1[0] == "binary_operation":
            varsList += self.__retrieveVars_binaryOperation(expr1[1])
    
        if expr2[0] == "reference":
            exprVar= ExpressionVariable (expr2[1], binaryOperation.line)
            varsList.append(exprVar)
        elif expr2[0] == "binary_operation":
            varsList += self.__retrieveVars_binaryOperation(expr2[1])
    
        return varsList

    def getExpressionsVariables (self):
        return self.expressionsVariables

    def getLocalVariables (self):
        return self.declaredLocalVars

    def getReference_to_constant (self):
        return self.reference_to_constant
    
    def getReference_to_if_expression (self):
        return self.reference_to_if_expression
    
    def getReference_to_reference (self):
        return self.reference_to_reference
    
    def getBinary_operations (self):
        return self.binaryOperations

    def getReference_to_functionCall (self):
        return self.reference_to_functionCall
    
    def display (self):
        print(self.name)
        for x in self.reference_to_constant.keys():
            print(x, " ref = ",  self.reference_to_constant[x].reference, " constant = ", self.reference_to_constant[x].constant)
        for x in self.reference_to_reference.keys():
            print(x, " ref1 = ", self.reference_to_reference[x].reference1, " ref2 = ", self.reference_to_reference[x].reference2)
        for x in self.binaryOperations.keys():
            print(x, " ref = ", self.binaryOperations[x].reference, " exp1 = ", self.binaryOperations[x].binaryOperation.expression1, " operation ", self.binaryOperations[x].binaryOperation.operation, " exp2 = ", self.binaryOperations[x].binaryOperation.expression2)
        for x in self.reference_to_if_expression.keys():
            print(x)
            print ("...", " ref = ", self.reference_to_if_expression[x].reference)
            #print ("......", self.reference_to_if_expression[x].if_expression.toString())
            for i in range(len(self.reference_to_if_expression[x].if_expression.toString())):
                print(self.reference_to_if_expression[x].if_expression.toString()[i])
            





    

