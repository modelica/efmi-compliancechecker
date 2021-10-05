#This file is a part of the eFMI Compliance Checker which is a python open-source 
# library intended for checking the compliance of an eFMU with the standard specification

#Copyright © ESI ITI GmbH, 2021
               
#This program is a free software distributed WITHOUT ANY WARRANTY and the use is 
#completely at your own risk; it can be redistributed and/or modified under the 
#terms of the BSD 3-Clause license. For license conditions (including the 
#disclaimer of warranty) visit: https://opensource.org/licenses/BSD-3-Clause.

#ESI ITI GmbH, Zwinger-Forum, Schweriner Straße 1, 01067 Dresden, Germany


from lark import Lark, Transformer, v_args, tree
from collections import namedtuple
from data.AlgorithmCodeData import Function, If_Expression, BinaryOperation, Reference_constant, Reference_Reference, Reference_if_expression, UnaryOperation, \
                    Reference_binary_operation, VarTypeCausality, FunctionCall, Reference_function_call, ExpressionVariable
import collections
import numpy as np

class ReadTree(Transformer):
    """
        Class ReadTree inherited from the Lark.Transformer class so it is able to visit each node of the tree.
        
        This class uses methods that have the same names of visited rules, for example: The function_declaration method in this class is invoked
        automatically when the node (rule) function_declaration is encountered in the tree.

        Methods which start by __ in the name are called locally only, for example: the __single_assignment method below is not called automatically,
        it is instead called by other methods of the ReadTree class only.

    """
    
    # Contains all none local and none protected variables which are declared in the alg file
    vars = {}

    # Contains all none local protected variables which are declared in the alg file
    protectedVars = {}

    # Includes all functions in the alg file, stored as objects instantiated from the Function class
    functions = {}

    def __init__(self):
        pass

    def __single_assignment(self, ref_node, expr, function, in_for_loop=False, ref_value=[], multi_dimension_constructor_indexs=[]):
        
        """
        It adds the single_assignment element to the function object, it checks the type of the passed expression first then adds
        the single_assignment element accordingly.

        The only parts of the rules which are not implemented yet are:
        - reference := dimension_query
        - The reference := multi_dimension_comstructor is limited to one and two dimensions of multi_dimension_comstructor 
            (three and above are not implemented)


        :param ref_node: The tree node of the reference element
        :param expr: The expression to be assigned to the single_assignment (see __expression() method)
        :param function: the function object where the single_assignment to be added to
        :param in_for_loop: It specifies if the method is called from a for_loop, when it is true the method reads the next param 
        :param ref_value: Stores the name of the for_loop index and its current iterating value (for example ["i", 0])
        :param multi_dimension_constructor_indexs: List of indexes for the multi_dimension_constructor, if the passes expression is 
            a multi_dimension_constructor

        """

        ref = self.__reference(ref_node, in_for_loop, ref_value)
        if (len(multi_dimension_constructor_indexs) > 1):
            ref += "[" + multi_dimension_constructor_indexs[0] + "," + multi_dimension_constructor_indexs[1] + "]"
        elif (len(multi_dimension_constructor_indexs) > 0):
            ref += "[" + multi_dimension_constructor_indexs[0] + "]"
        
        if expr[0] == 'constant':
            refConstant = Reference_constant (ref, expr[1], ref_node.line)
            function.addReference_to_constant(refConstant)
        elif expr[0] == 'reference':
            refToRef = Reference_Reference (ref, expr[1], ref_node.line)
            function.addReference_to_reference(refToRef)
        elif expr[0] == 'if_expression':
            refToIfExpr = Reference_if_expression(ref, expr[1], ref_node.line)
            function.addReference_to_ifExpression(refToIfExpr)
        elif expr[0] == 'binary_operation':
            
            refToBinaryOperation = Reference_binary_operation(ref, expr[1], ref_node.line)
            function.addReference_to_binaryOperation(refToBinaryOperation)
        elif expr[0] == 'function_call':
            
            refToFunctionCall = Reference_function_call(ref, expr[1], ref_node.line)
            function.addReference_to_functionCall(refToFunctionCall)
        elif expr[0] == 'unary_operation':
            if expr[1] == 'function_call':
                
                refToFunctionCall = Reference_function_call(ref, expr[2], ref_node.line)
                function.addReference_to_functionCall(refToFunctionCall)
            elif expr[1] == 'reference':
                refToRef = Reference_Reference (ref, expr[2], ref_node.line)
                function.addReference_to_reference(refToRef)
            elif expr[1] == 'if_expression':
                refToIfExpr = Reference_if_expression(ref, expr[2], ref_node.line)
                function.addReference_to_ifExpression(refToIfExpr)
        elif expr[0] == 'multi_dimension_constructor':
            all_espressions = expr[1]
            for i in range(len(all_espressions)):
                
                if all_espressions[i][0] == 'multi_dimension_constructor':
                    embedded_expressions = all_espressions[i][1]
                    for j in range(len(all_espressions[i])):
                        
                        self.__single_assignment(ref_node, embedded_expressions[j], function, in_for_loop, ref_value, [str(i+1), str(j+1)])
                else:
                    self.__single_assignment(ref_node, all_espressions[i], function, in_for_loop, ref_value, [str(i+1)])
    
    def __function_call (self, node):
    
        """
        It is called when the function_call node is encountered

        :param ode: The function_call tree node
        :return: The created FunctionCall tuple

        """

        funcName = ""
        expressions = []
        for i in range(len(node.children)):
            if isinstance(node.children[i], tree.Tree):
                if node.children[i].data == 'name':
                    funcName = self.__name(node.children[i].children[0])
                else:
                    expressions.append(self.__expression(node.children[i]))
        functionCall = FunctionCall(funcName, expressions, node.line)
        return functionCall
    
    def __number(self, node):

        """
        It is called when the number node is encountered (for reading real or integer numbers)

        :param ode: The number tree node
        :return: The real or integer number which is contained in the number node

        """

        
        strInt = self.__integer(node.children[0])
        if len(node.children) == 1:
            if (strInt[0] == "-"):
                if (strInt[1] != "0"):
                    return (0 - int(strInt))
                return 0
            else:
                return int(strInt)
        else:
            for i in range(len(node.children)):
                if (i > 0):
                    for j in range(len(node.children[i].children)):
                        strInt += node.children[i].children[j]
                    
        return float(strInt)
            

    def __integer(self, node):

        """
        It is called to read the integer part of a number

        :param ode: The integer tree node
        :return: The integer number (as a string) which is contained in the integer node

        """

        
        if (isinstance(node.children[0], tree.Tree)):    
            if (node.children[0].data == "positive_integer"):
                number = ""
                for i in range(len(node.children[0].children)):
                    number += node.children[0].children[i]
            '''    
            else:
                number = "-"
                for i in range(len(node.children[0].children[0].children)):
                    number += node.children[0].children[0].children[i]'''
                
            return number
        elif node.children[0] == "0":
            return "0"
        #else:
            #return "-0"

    def __expression(self, node, in_for_loop=False, ref_value=[]):

        
        """
        It can read the expression when the expression tree node is encountered, it specifies the type of the expression and creates the
        relevant expression tuple

        The only parts of the rules which are not implemented yet are:
        - dimension_query
        - multi_dimension_comstructor is limited to one and two dimensions (three and above are not implemented)


        :param node: The tree node of the expression
        :param in_for_loop: It specifies if the method is called from a for_loop, when it is true the method reads the next param 
        :param ref_value: Stores the name of the for_loop index and its current iterating value (for example ["i", 0])
        :return: the expression as a tuple, type (constant, reference, binary_operation, ...) and line number in the alg file

        """

        for j in range(len(node.children)):
            if node.children[j].data == "constant":
                number = 0
                
                if node.children[j].children[0].data == 'boolean':
                    typ = node.children[j].children[0].data
                else:
                    if len(node.children[j].children[0].children) > 1:
                        typ = "real"
                    else:
                        typ = "integer"
                    
                    number = self.__number(node.children[j].children[0])
                return ['constant', typ.title(), number, node.children[j].line]
            elif node.children[j].data == "reference":
                return ['reference', self.__reference(node.children[j], in_for_loop, ref_value), node.children[j].line]
            elif node.children[j].data == "if_expression":
                ifExpression = If_Expression()
                self.__if_expression(node.children[j], ifExpression)
                return ['if_expression', ifExpression, node.children[j].line]
            elif node.children[j].data == "binary_operation":

                return self.__read_binaryOperation(node.children[j])
                
                #operation = node.children[j].children[1].children[0].children[0].children[0].value
                #exp1 = self.__expression(node.children[j].children[0])
                
                #exp2 = self.__expression(node.children[j].children[2])
                
                #binaryOperation = BinaryOperation (exp1, operation, exp2, node.children[j].line)
                #return ['binary_operation', binaryOperation, node.children[j].line]
            elif node.children[j].data == 'parenthesized_expression':   
                return  self.__expression (node.children[j].children[1])
            elif node.children[j].data == 'function_call':
                return ['function_call', self.__function_call(node.children[j]), node.children[j].line]
            elif node.children[j].data == 'unary_operation':
                u_operation = node.children[j].children[0].value
                if node.children[j].children[1].data == 'function_call':
                    funcCall = self.__function_call(node.children[j].children[1])
                    return ['unary_operation', 'function_call', funcCall, u_operation, node.children[j].children[1].line]
                elif node.children[j].children[1].data == 'reference':
                    ref = self.__reference(node.children[j].children[1])
                    
                    return ['unary_operation', 'reference', ref, u_operation, node.children[j].children[1].line]
                elif node.children[j].children[1].data == 'parenthesized_expression':
                    exp = self.__expression(node.children[j].children[1].children[1])
                    return ['unary_operation', exp[0], exp[1], u_operation, node.children[j].children[1].line]
                elif node.children[j].children[1].data == 'binary_operation':
                    #operation = node.children[j].children[1].children[1].children[0].children[0].children[0].value
                    #exp1 = self.__expression(node.children[j].children[1].children[0])
                    #exp2 = self.__expression(node.children[j].children[1].children[2])
                    #binaryOperation = BinaryOperation (exp1, operation, exp2, node.children[j].line)
                    binaryOperationExpr =  self.__read_binaryOperation(node.children[j].children[1])
                    
                    return ['unary_operation', 'binary_operation', binaryOperationExpr[1], u_operation, node.children[j].children[1].line]
                elif  node.children[j].children[1].data == "if_expression":
                    ifExpression = If_Expression()
                    self.__if_expression(node.children[j].children[1], ifExpression)
                    return ['unary_operation', 'if_expression', ifExpression, u_operation, node.children[j].children[1].line]
                elif node.children[j].children[1].data == "constant":
                    if node.children[j].children[1].children[0].data == 'boolean':
                        typ = node.children[j].children[1].children[0].data
                    else:
                        if len(node.children[j].children[1].children[0].children) > 1:
                            typ = "real"
                        else:
                            typ = "integer"
                    number = self.__number(node.children[j].children[1].children[0])
                    const = ['constant', typ.title(), number, node.children[j].children[1].line]
                    return ['unary_operation', 'constant', const, u_operation, node.children[j].children[1].line]

            elif node.children[j].data == 'multi_dimension_constructor':
                return ['multi_dimension_constructor', self.__multi_dimension_constructor(node.children[j], in_for_loop, ref_value)]
    
    def __read_binaryOperation (self, node):
        return self.__or(node.children[0])
        
            
    def __or(self, node):
        if (len(node.children) > 1):
            exp1 = self.__or(node.children[0])
            operation = node.children[1]
            exp2 = self.__and(node.children[2])
            binaryOperation = BinaryOperation (exp1, operation, exp2, node.children[0].line)
            return ['binary_operation', binaryOperation, node.children[0].line]
        else:
            return self.__and(node.children[0])

    
    def __and(self, node):
        if (len(node.children) > 1):
            exp1 = self.__and(node.children[0])
            operation = node.children[1]
            exp2 = self.__equal(node.children[2])
            binaryOperation = BinaryOperation (exp1, operation, exp2, node.children[0].line)
            return ['binary_operation', binaryOperation, node.children[0].line]
        else:
            return self.__equal(node.children[0])
    
    def __equal(self, node):
        if (len(node.children) > 1):
            exp1 = self.__equal(node.children[0])
            operation = node.children[1]
            exp2 = self.__relational(node.children[2])
            binaryOperation = BinaryOperation (exp1, operation, exp2, node.children[0].line)
            return ['binary_operation', binaryOperation, node.children[0].line]
        else:
            return self.__relational(node.children[0])
    
    def __relational(self, node):
        if (len(node.children) > 1):
            exp1 = self.__relational(node.children[0])
            operation = node.children[1]
            exp2 = self.__sum(node.children[2])
            binaryOperation = BinaryOperation (exp1, operation, exp2, node.children[0].line)
            return ['binary_operation', binaryOperation, node.children[0].line]
        else:
            return self.__sum(node.children[0])
        
    def __sum(self, node):
        if (len(node.children) > 1):
            exp1 = self.__sum(node.children[0])
            operation = node.children[1]
            exp2 = self.__mul(node.children[2])
            binaryOperation = BinaryOperation (exp1, operation, exp2, node.children[0].line)
            return ['binary_operation', binaryOperation, node.children[0].line]
        else:
            return self.__mul(node.children[0])

    def __mul(self, node):
        if (len(node.children) > 1):
            exp1 = self.__mul(node.children[0])
            operation = node.children[1]
            exp2 = self.__power(node.children[2])
            binaryOperation = BinaryOperation (exp1, operation, exp2, node.children[0].line)
            return ['binary_operation', binaryOperation, node.children[0].line]
        else:
            return self.__power(node.children[0])
    
    def __power(self, node):
        if (len(node.children) > 1):
            exp1 = self.__power(node.children[0])
            operation = node.children[1]
            exp2 = self.__expression(node.children[2])
            binaryOperation = BinaryOperation (exp1, operation, exp2, node.children[0].line)
            return ['binary_operation', binaryOperation, node.children[0].line]
        else:
            return self.__expression(node.children[0])

 
    def __multi_dimension_constructor(self, node, in_for_loop=False, ref_value=[]):

        """
        It reads all the expressions which are stored in the multi_dimension_constructor node


        :param node: The tree node of the multi_dimension_constructor
        :param in_for_loop: It specifies if the method is called from a for_loop, when it is true the method reads the next param 
        :param ref_value: Stores the name of the for_loop index and its current iterating value (for example ["i", 0])
        :return: the list of all expressions stored in the multi_dimension_constructor tree node

        """

        all_expressions = []
        for i in range(len(node.children)):
            if (isinstance(node.children[i], tree.Tree)):
                if node.children[i].data == "multi_dimension_constructor_element":
                    if node.children[i].children[0].data == "expression":
                        all_expressions.append(self.__expression(node.children[i].children[0], in_for_loop, ref_value))
                    else:
                        all_expressions.append(self.__multi_dimension_constructor(node.children[i].children[0], in_for_loop, ref_value))
                        
        return all_expressions

    def __if_expression(self, node, ifExpression):

        """
        It adds all expressions and conditions to the if_expression


        :param node: The tree node of the if_expression
        :param ifExpression: the if_expression object where expressions and conditions are added 

        """

        k = 1
        while k in range(len(node.children)):
            
            if node.children[k] == 'if':
                k += 1
                exp = self.__expression(node.children[k])
                ifExpression.addCondition(exp)
                k += 1
            elif node.children[k] == 'then':
                k += 1
                exp = self.__expression(node.children[k])
                ifExpression.addExpression(exp)
                k += 1
                
            elif node.children[k] == 'else':
                k += 1
                exp = self.__expression(node.children[k])
                ifExpression.addElseExpression(exp)
                k += 1

            elif isinstance(node.children[k], tree.Tree):
                
                if node.children[k].data == 'elseif_expression':
                    exp1 = self.__expression(node.children[k].children[1])
                    exp2 = self.__expression(node.children[k].children[3])
                    ifExpression.addElseIF (exp1, exp2)
                    k += 1
            else:
                k += 1
        

    def function_declaration(self,node):

        """
        This method is invoked automatically when the function_declaration node is encountered, it instantiates a function object and then adds
        the declared variables and the expressions to the object. The latter object is stored in the functions property which contains all function
        declarations (examples of function declarations are: Startup and DoStep)

        The following statements need to be added:
        - multi_assignment
        - limit statement
        - function_call (implemented just to be added)
        - if_statement (implemented just to be added)


        :param node: The tree node of the function_declaration

        """

        functionName = ''
        function = Function()
        for i in range(len(node)):
            
            if not isinstance(node[i], tree.Tree):
                if i == 0:
                    methodOrFunction = node[i].value    
            #funaction name
            if i == 1:
                #for j in range(len(node[i].children[0].children)):
                    #functionName += node[i].children[0].children[j]
                functionName = self.__name(node[i].children[0])
                function.setName(functionName)
                function.setFunctionMethod(methodOrFunction)
                
            #reading statement
            if isinstance(node[i], tree.Tree):
                if node[i].data == "statement":
                    
                    if node[i].children[0].data == "single_assignment":
                        
                        expr = self.__expression(node[i].children[0].children[2])
                        
                        self.__single_assignment(node[i].children[0].children[0], expr, function)
                    elif node[i].children[0].data == "for_loop":
                        self.__for_loop(node[i].children[0], function)
                    
                elif node[i].data == "parameter_var_delaration":
                    
                    for j in range(len(node[i].children)):
                        if isinstance(node[i].children[j], tree.Tree):
                            if node[i].children[j].data == "parameter_declaration":
                                # To do KAH
                                varCausality = node[i].children[j].children[0].value
                                
                                nameAndType = self.__variable_declaration(node[i].children[j].children[1].children)
                                #varTypeCaus = VarTypeCausality(nameAndType[1], varCausality)
                                function.addDeclaredLocalVars(varCausality, nameAndType, node[i].line)
                                #ReadTree.vars[nameAndType[0]] = varTypeCaus
                            elif node[i].children[j].data == "local_variable_declaration":
                                varCausality = node[i].children[j].children[0].children[0].children[0].value
                            
                                nameAndType = self.__variable_declaration(node[i].children[j].children[0].children)
                                function.addDeclaredLocalVars(varCausality, nameAndType, node[i].line)
                                
                                '''if len(nameAndType[0]) == 1:
                                    function.addDeclaredLocalVars(varCausality, nameAndType[0][0], node[i].line)
                                else:
                                    for k in range(len(nameAndType[0])):
                                        function.addDeclaredLocalVars(varCausality, nameAndType[0][k], node[i].line)'''
                                    
                            
                
                '''elif node[i].data == 'local_variable_declaration':
                    varCausality = node[i].children[0].value
                    nameAndType = self.__variable_declaration(node[i].children[1].children)
                    function.addDeclaredLocalVars(varCausality, nameAndType)'''
                
        ReadTree.functions[function.name] = function
        return node

    def __reference(self, node, in_for_loop=False, ref_value=[]):

        """
        It reads and returns the name of a reference which is contained in an expression 

        :param node: The tree node of the reference
        :param in_for_loop: It specifies if the method is called from a for_loop, when it is true the method reads the next param 
        :param ref_value: Stores the name of the for_loop index and its current iterating value (for example ["i", 0])
        :return: The reference name (reference might be scalar or an element of array)

        """

        ref = ""
        varName = ""
        # state_reference
        if node.children[0].data == "state_reference":
            for j in range(len(node.children[0].children)):
                if isinstance(node.children[0].children[j], tree.Tree):
                    if node.children[0].children[j].data == "name":
                        varName = self.__name(node.children[0].children[j].children[0])
                        ref += varName
                    elif node.children[0].children[j].data == "computed_dimensions":
                        node1 = node.children[0].children[j]
                        for i in range(len(node1.children)):
                            
                            if isinstance(node1.children[i], tree.Tree):
                                if (node1.children[i].data == "constant_scalar_integer_expression"):
                                    
                                    if node1.children[i].children[0].children[0].data == "constant":
                                        
                                        if len(node1.children[i].children[0].children[0].children[0].children) == 1:
                                            index = self.__number(node1.children[i].children[0].children[0].children[0])
                                            ref += "[" + str(index) + "]"
                                            
                                    elif node1.children[i].children[0].children[0].data == "reference":
                                        index_ref = self.__reference(node1.children[i].children[0].children[0])
                                        if (in_for_loop):
                                            if index_ref == ref_value[0]:
                                                ref += "[" + ref_value[1] + "]"
                                    elif node1.children[i].children[0].children[0].data == "binary_operation":

                                        binaryOperationExpr =  self.__read_binaryOperation(node1.children[i].children[0].children[0])
                    
                                        #BinaryOperationExpr[1], u_operation, node.children[j].children[1].line]
                                        #node2 = node1.children[i].children[0].children[0]
                                        operation = binaryOperationExpr[1]
                                        
                                        exp1 = binaryOperationExpr[0]
                                        exp2 = binaryOperationExpr[2]
                                        
                                        if exp1[0] == "reference":
                                            if (in_for_loop):
                                                if exp1[1] == ref_value[0]:
                                                    if exp2[0] == "constant":
                                                        if operation=="+":
                                                            index = int(ref_value[1]) + int (exp2[2])
                                                        elif operation=="-":
                                                            index = int(ref_value[1]) - int (exp2[2])
                                                        ref += "[" + str(index) + "]"
                                                        
                                        
        elif node.children[0].data == "local_reference":
            if node.children[0].children[0].data == "name":
                varName = self.__name(node.children[0].children[0].children[0])
                ref += varName


                #else:
                    #ref += node.children[0].children[j]
        
        return ref

    def __scalarized_reference(self, node):
        varName = ""
        for j in range(len(node.children)):
            #print(node.children[j])    
            if (node.children[j] == "."):
                varName += node.children[j]
            elif node.children[j].data == "fixed_dimensions":
                for i in range(len(node.children[j].children)):
                    if not isinstance(node.children[j].children[i], tree.Tree):
                        varName += node.children[j].children[i]
                    else:
                        if (node.children[j].children[i].data == "positive_integer"):
                            number = ""
                            for k in range(len(node.children[j].children[i].children)):
                                number += node.children[j].children[i].children[k]
                            varName += number
            elif (node.children[j].data == "identifier"):
                for k in range(len(node.children[j].children)):
                    varName += node.children[j].children[k]
        return varName
    
    def __quoted_identifier_higher_order_derivative(self, node):
        varName = ""
        if isinstance(node.children[0], tree.Tree):
            return self.__scalarized_reference(node.children[0])
        else:
            varName += node.children[0]
            varName += node.children[1]
            varName += self.__quoted_identifier_higher_order_derivative(node.children[2])
            varName += ")"
            return varName

    def __name(self, node):

        
        """
        It reads and returns the name of when the name node is encountered, the name rule is a part of several rules (see the grammar file)

        :param node: The tree node of the name
        :return: The name element (examples include reference, method name and varaivle declaration)

        """


        varName = ""
        containBracket = False
        containQuotes = False
        
        #if (node.data == "identifier"):
            #for l in range(len(node.children)):
                #varName += node.children[l].value
        if not isinstance(node, tree.Tree):
            varName = node.value
                
        else:                   
            varName = ""
            varName += "'"
            containQuotes = True

            # quoted_identifier
            if (len(node.children) > 1):
                varName += node.children[0]
                temp = node.children[0]
                varName += node.children[1]
                node = node.children[2]
                containBracket = True
                if temp == "previous":
                    varName += self.__scalarized_reference(node)
                else:
                    varName += self.__quoted_identifier_higher_order_derivative(node)
            else:
                node = node.children[0]
                varName += self.__scalarized_reference(node)
                #print(varName)

                    
            #scalarized_reference
            
            """
            if node.children[0].data == "scalarized_reference":
                #self.__scalarized_reference(node.children[0], varName)
                
                
                for j in range(len(node.children)):
                
                    if (node.children[j] == "."):
                        varName += node.children[j]
                    elif node.children[j].data == "fixed_dimensions":
                        for i in range(len(node.children[j].children)):
                            if not isinstance(node.children[j].children[i], tree.Tree):
                                varName += node.children[j].children[i]
                            else:
                                if (node.children[j].children[i].data == "positive_integer"):
                                    number = ""
                                    for k in range(len(node.children[j].children[i].children)):
                                        number += node.children[j].children[i].children[k]
                                    varName += number
                    
                    elif (node.children[j].data == "identifier"):
                        for k in range(len(node.children[j].children)):
                            varName += node.children[j].children[k]
            """
            

    

        if containBracket:
            varName += ")"
        
        if containQuotes :
            varName += "'"
        #varNames.append(varName)
        return varName
    
    def __fixed_dimensions(self, node):

        """
        It specifies the dimensions of a name currently is not used

        :param node: The tree node of the fixed_dimensions
        :return: the specified dimensions 
        
        """


        dimensions = []
        for i in range(len(node.children)):
            if isinstance(node.children[i], tree.Tree):
                if (node.children[i].data == "positive_integer"):
                    number = ""
                    for j in range(len(node.children[i].children)):
                        number += node.children[i].children[j]
                    dimensions.append(number)
        return dimensions


    def state_entity_declaration (self, node):

        """
        This method is invoked automatically when the state_entity_declaration node is encountered, it adds the declared variables
        to the local vars property which contains all declared public variables in the alg file

        :param node: The tree node of the state_entity_declaration
        
        """


        varCausality = node[0].value

        #print ("from state_entity_declaration")
        #print(node[0])
        #print(node[1])
        #print ("finished state_entity_declaration")
        nameAndType = self.__variable_declaration(node[1].children)
        varTypeCaus = VarTypeCausality(nameAndType[1], varCausality, node[1].line)
        if len(nameAndType[0]) == 1:
            ReadTree.vars[nameAndType[0][0]] = varTypeCaus
        else:
            for i in range(len(nameAndType[0])):
                ReadTree.vars[nameAndType[0][i]] = varTypeCaus

    def protected_declaration(self, node):

        """
        This method is invoked automatically when the protected_declaration node is encountered, it adds the declared protected 
        variables to the local vars property which contains all declared public variables in the alg file

        please note that only the ([DATA_FLOW_DIRECTION] variable_declaration) of the protected_declaration is implemented here 
        (see the grammar file)

        :param node: The tree node of the protected_declaration
        
        """
         
        i = 0
        while i < len(node):
            if isinstance(node[i], tree.Tree):
                if (node[i].data == "variable_declaration"):
                    #print(node[i])
                    varCausality = "state"
                    nameAndType = self.__variable_declaration(node[i].children)
                    #MinMax_Expressions = MinMax_Expressions', ['references', 'types', 'vals'])
                    varTypeCaus = VarTypeCausality(nameAndType[1], varCausality, node[i].line)
                    if len(nameAndType[0]) == 1:
                        ReadTree.protectedVars[nameAndType[0][0]] = varTypeCaus
                    else:
                        for j in range(len(nameAndType[0])):
                            ReadTree.protectedVars[nameAndType[0][j]] = varTypeCaus
                i += 1
            else:
                if not isinstance(node[i], list):
                    #print(node[i])
                    varCausality = node[i].value
                    nameAndType = self.__variable_declaration(node[i+1].children)
                    varTypeCaus = VarTypeCausality(nameAndType[1], varCausality, node[i].line)
                    if len(nameAndType[0]) == 1:
                        ReadTree.protectedVars[nameAndType[0][0]] = varTypeCaus
                    else:
                        for j in range(len(nameAndType[0])):
                            ReadTree.protectedVars[nameAndType[0][j]] = varTypeCaus
                    
                    i += 2
                else:
                    i += 1
    def __type_compartment_reference(self, node):
        return node.children[0]
        
    def __variable_declaration(self, node):

        """
        This method is invoked when the variable_declaration node is encountered, it can read names of types of variables
        It can differentiate between scalar and vectors/arrays variables by reading the constant_dimensions when it is
        provided 

        :param node: The tree node of the variable_declaration
        
        """
       
        name = ""
        constatDimensExist = False
        varNames = []
    
        for i in range(len(node)):
            if (node[i].data == "type"):
                varType = node[i].children[0].value
            elif node[i].data == "variable_name":
                name = self.__name(node[i].children[0].children[0])
            elif node[i].data == "constant_dimensions":
                constatDimensExist = True
                constant_dimensions = self.__constant_dimensions(node[i])
        
        if (constatDimensExist):
            if constant_dimensions[0] == "dimensions":
                if len(constant_dimensions[1]) == 1:
                    for i in range(constant_dimensions[1][0]):
                        varNames.append(name + "[" + str(i+1) + "]")
                    
                    varNames.append(name)
                elif len(constant_dimensions[1]) == 2:
                    for i in range(constant_dimensions[1][0]):
                        for j in range(constant_dimensions[1][1]):
                            varNames.append(name + "[" + str(i+1) + "," + str(j+1) + "]")
                    
                    varNames.append(name)
            else:
                varNames.append(name)
        else:
            varNames.append(name)

        return [varNames, varType]
    
    def __constant_dimensions(self, node):

        """
        This method is invoked when the constant_dimensions of a variable_declaration is provided (none scalar variables)
        (currently I use it also for the min and max values which are provided after the variable declaration)

        :param node: The tree node of the constant_dimensions 
        
        """
  
        names = []
        values = []
        dimensions = []
        varDimension = False
        for i in range(len(node.children)):
            if isinstance(node.children[i], tree.Tree):
                
                if isinstance(node.children[i].children[0], tree.Tree):
                    for j in range(len(node.children[i].children[0].children)):
                        node1 = node.children[i].children[0].children[j].children[0]
                        
                        if isinstance(node1, tree.Tree):
                            if node1.data == "constant":
                                varDimension = True
                                if node1.children[0].data == "boolean":
                                    print("error")
                                elif len(node1.children[0].children) == 1:
                                    dimension = self.__number(node1.children[0])
                                    dimensions.append(dimension)
                                    
                                else:
                                    print("error")
                            elif node1.data == "minmax_expression":
                                varName = self.__name(node1.children[0].children[0])
                                if isinstance(node1.children[2], tree.Tree):
                                    value = self.__number(node1.children[2].children[0])
                                else:
                                    value = self.__number(node1.children[3].children[0])
                                    value = "-" + value
                                names.append(varName)
                                values.append(value)
        if (varDimension == True):
            return ["dimensions", dimensions]
        else:
            return ["minmax", names, values]

    def __for_loop(self, node, function):
        
        """
        It is called when a for_loop node is encountered, so it can iterate through and store the statements

        The following statements need to be added:
        - multi_assignment
        - limit statement
        - function_call
        - if_statement


        :param node: The tree node of the for_loop
        :param function: the function object where the for_loop to be added to
        """

        start_bound = 0
        termination_bound = 0
        index_name = ""
        for i in range(len(node.children)):
            
            if isinstance(node.children[i], tree.Tree):
                if node.children[i].data == "bounded_iteration":
                    for j in range(len(node.children[i].children)):
                        node1 = node.children[i].children[j]
                        if isinstance(node1, tree.Tree):
                            if node1.data == "loop_iterator_declaration":
                                index_name = self.__name(node1.children[0].children[0])
                                
                            elif node1.data == "start_bound":
                                expr = self.__expression(node1.children[0].children[0])
                                if expr[0] == "constant":
                                    start_bound = int(expr[2])
                                    
                            elif node1.data == "termination_bound":
                                expr = self.__expression(node1.children[0].children[0])
                                if expr[0] == "constant":
                                    termination_bound = int(expr[2])
                                    

                elif node.children[i].data == "statement":
                    if node.children[i].children[0].data == "single_assignment":
                        for k in range(start_bound,termination_bound+1):
                            index_val = [index_name, str(k)]
                            
                            expr = self.__expression(node.children[i].children[0].children[2], True, index_val)
                            self.__single_assignment(node.children[i].children[0].children[0], expr, function, True, index_val)
                    elif node.children[i].children[0].data == "for_loop":
                        self.__for_loop(node.children[i].children[0], function)



    @staticmethod
    def variables():
        return ReadTree.vars
    
    @staticmethod
    def protectedVariables():
        return ReadTree.protectedVars
    
    @staticmethod
    def getFunctions():
        return ReadTree.functions
