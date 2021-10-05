# Repository overview

This repository provides the source code of the _eFMI Compliance Checker_, a tool for checking eFMUs for conformance with the [eFMI Standard](https://efmi-standard.org).

The supported checks are:

- Verifying the eFMU container architecture (e.g., are all containers listed in the eFMU manifest)
- Consistency checking of all model representation manifests, which includes:
1- Checking if the representation id matches the id in the manifest file
2- Comparing the representation checksum with the calculated checksum of the manifest file
3- Validating the representation manifest against the relevant schema file
4- Validating inter and intra manifest references (referenced id exists and its checksum) 
- Validating the GALEC code against the specification, which includes:
1- parsing the GALEC code and extracting all variables and functions
2- Checking if the declared variables match the manifest variables of its Algorithm Code container
3- Validating all expressions by checking if all variables are declared and their types are correct

A full list of supported checks is given in the [AsciiDoc](https://asciidoc-py.github.io/) file
[documentation/validation_list.adoc](documentation/validation_list.adoc).

## Dependencies

The _eFMI Compliance Checker_ is a [Python](https://www.python.org/) library; to use it, an installed [Python 3.10.0](https://www.python.org/) or higher runtime environment is required.

The _eFMI Compliance Checker_ uses the following Python libraries besides the [Python Standard Library](https://docs.python.org/3/library/index.html):
 * [Lark](https://lark-parser.readthedocs.io/en/latest/) for parsing
 * [lxml](https://lxml.de/) for processing XML and HTML
 * [colorama](https://pypi.org/project/colorama/) for colored terminal text and cursor positioning
 * [NumPy](https://numpy.org/) for large, multi-dimensional arrays and matrices and operations on such

## User interface

The following example shows how to run the _eFMI Compliance Checker_ to validate an eFMU called `M14_A.fmu`:

```
py <<path-to-main>>\main.py <<path-to-eFMU>>\M14_A.fmu
```

The `<<path-to-main>>` is the path to the `complianceChecker/main.py`.

The check results will be printed on the terminal. For a correct eFMU, you will have results like:

![eFMU VALIDATING](docs/validate_efmu.png)

## Structure

This chapter describes the main structure of the compliance checker. So it can help other partners to use the compliance checker and, more specifically, provides a full guidance for partners who would like to contribute.

### The "ComplianceChecker" module

It represents the main module and the main access point to all other modules, it contains the "read_model_container" which is the primary function that invokes and runs all the necessary tasks.
This function has the following format:


**def read_model_container(filename)**  
:param filename: The name of the eFMU archive file

This function severs the following tasks:

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

### The "larkTransformer" module

The Compliance Checker uses the Lark parsing library (https://lark-parser.readthedocs.io/en/latest/) to parse and validate the algorithm code files against the defined rules. So The "larkTransformer" module contains the main class that can read and store all data from the algorithm code files, this class can extract the data by visiting each node of the parsed tree and invoke the relevant member methods. For example, The function_declaration method in this class is invoked automatically when the function_declaration node (rule) is encountered in the tree.
The mentioned class has the following structure:

<details>
<summary>click to check the detailed structure of the ReadTree class</summary>
<p>

```python
class ReadTree(Transformer):
    """
        Class ReadTree inherited from the Lark.Transformer class so it is able to visit each node of the tree.
        
        This class uses methods that have the same names of visited rules, for example: The function_declaration method in this class is invoked
        automatically when the node (rule) function_declaration is encountered in the tree.

        Methods which start by __ in the name are called locally only, for example: the __single_assignment method below is not called automatically,
        it is instead called by other methods of the ReadTree class only.

    """
    
    # Contains all non local variables which are declared in the alg file
    vars = {}

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
    
    def __function_call (self, node):
    
        """
        It is called when the function_call node is encountered

        :param ode: The function_call tree node
        :return: The created FunctionCall tuple

        """
    
    def __number(self, node):

        """
        It is called when the number node is encountered (for reading real or integer numbers)

        :param ode: The number tree node
        :return: The real or integer number which is contained in the number node

        """
        
    def __integer(self, node):

        """
        It is called to read the integer part of a number

        :param ode: The integer tree node
        :return: The integer number (as a string) which is contained in the integer node

        """

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

    def __multi_dimension_constructor(self, node, in_for_loop=False, ref_value=[]):

        """
        It reads all the expressions which are stored in the multi_dimension_constructor node


        :param node: The tree node of the multi_dimension_constructor
        :param in_for_loop: It specifies if the method is called from a for_loop, when it is true the method reads the next param 
        :param ref_value: Stores the name of the for_loop index and its current iterating value (for example ["i", 0])
        :return: the list of all expressions stored in the multi_dimension_constructor tree node

        """

    def __if_expression(self, node, ifExpression):

        """
        It adds all expressions and conditions to the if_expression


        :param node: The tree node of the if_expression
        :param ifExpression: the if_expression object where expressions and conditions are added 

        """

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

    def __reference(self, node, in_for_loop=False, ref_value=[]):

        """
        It reads and returns the name of a reference which is contained in an expression 

        :param node: The tree node of the reference
        :param in_for_loop: It specifies if the method is called from a for_loop, when it is true the method reads the next param 
        :param ref_value: Stores the name of the for_loop index and its current iterating value (for example ["i", 0])
        :return: The reference name (reference might be scalar or an element of array)

        """

    def __name(self, node):

        
        """
        It reads and returns the name of when the name node is encountered, the name rule is a part of several rules (see the grammar file)

        :param node: The tree node of the name
        :return: The name element (examples include reference, method name and varaivle declaration)

        """
    
    def __fixed_dimensions(self, node):

        """
        It specifies the dimensions of a name currently is not used

        :param node: The tree node of the fixed_dimensions
        :return: the specified dimensions 
        
        """

    def state_entity_declaration (self, node):

        """
        This method is invoked automatically when the state_entity_declaration node is encountered, it adds the declared variables
        to the local vars property which contains all declared public variables in the alg file

        :param node: The tree node of the state_entity_declaration
        
        """


    def protected_declaration(self, node):

        """
        This method is invoked automatically when the protected_declaration node is encountered, it adds the declared protected 
        variables to the local vars property which contains all declared public variables in the alg file

        please note that only the ([DATA_FLOW_DIRECTION] variable_declaration) of the protected_declaration is implemented here 
        (see the grammar file)

        :param node: The tree node of the protected_declaration
        
        """
        
    def __variable_declaration(self, node):

        """
        This method is invoked when the variable_declaration node is encountered, it can read names of types of variables
        It can differentiate between scalar and vectors/arrays variables by reading the constant_dimensions when it is
        provided 

        :param node: The tree node of the variable_declaration
        
        """
    
    def __constant_dimensions(self, node):

        """
        This method is invoked when the constant_dimensions of a variable_declaration is provided (none scalar variables)
        (currently I use it also for the min and max values which are provided after the variable declaration)

        :param node: The tree node of the constant_dimensions 
        
        """

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

    @staticmethod
    def variables():
        return ReadTree.vars
    
    @staticmethod
    def getFunctions():
        return ReadTree.functions
```

</p>
</details> 

### The "AlgorithmCodeData" module

This module contains the definition of all data structures that are used to store variables and expressions contained in the algorithm code files. The data structures defined in this module are listed below.
#### Expressions tuples
The following tuples are defined to help store all types of expressions. For example, the Reference_constant tuple is defined to address the single_assignment of type (reference := constant). So it
contains three elements: reference, constant and the line number in the alg file. More examples are listed below:

- Reference_if_expression: contains reference, if_expression which is of type If_Expression and finally the line number
- FunctionCall: includes a name of the function, expression which contains all parameter expressions (see the function_call rule)
  and finally the line number
- ElseIf: contains a condition (which is an expression rule), expression to be visited when the condition is true and 
  finally the line number

<details>
<summary>click to check the definition of all used tuples</summary>
<p>

```python
Reference_constant = namedtuple('Reference_constant', ['reference', 'constant', 'line'])
Reference_Reference = namedtuple('Reference_Reference', ['reference1', 'reference2', 'line'])
Reference_if_expression = namedtuple('Reference_if_expression', ['reference', 'if_expression', 'line'])
BinaryOperation = namedtuple('BinaryOperation', ['expression1', 'operation', 'expression2', 'line'])
Reference_binary_operation = namedtuple('Reference_binary_operation', ['reference', 'binaryOperation', 'line'])
VarTypeCausality = namedtuple('VarTypeCausality', ['type', 'causality', 'line'])
ExpressionVariable = namedtuple('ExpressionVariable', ['name', 'line'])
ElseIf = namedtuple ('ElseIf', ['condition', 'expression', 'line'])
FunctionCall = namedtuple('FunctionCall', ['name', 'expression', 'line'])
UnaryOperation = namedtuple('UnaryOperation', ['operation', 'expression', 'line'])
Reference_function_call = namedtuple('Reference_function_call', ['reference', 'functionCall', 'line'])
```

</p>
</details>

#### If_Expression class
This class represents the if_expression rule, it contains a number of properties to store all elements of the if_expression. These properties include:
- conditions: stores the expression which act as a condition after the "if" keyword (see the if_expression rule)
- elseIf: contains all the elseif_expression expressions
- expression: includes the expression which is visited when the condition is true
- elseExpr: contains the expression which is visited when the condition is false

<details>
<summary>click to check the detailed structure of the If_Expression class</summary>
<p>

```python
class If_Expression:

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
    
    def addElseIF(self, condition, expression):
    
    def addExpression (self, expression):
    
    def addElseExpression (self, expression):
    
    def getConditions (self):
    
    def getElseIfs (self):

    def getExpressions (self):
    
    def getElseExpr (self):
    
    def toString (self):
```

</p>
</details>

#### Function class
This class represents the function_declaration rule, it contains a number of properties to store all local variables and expressions of the function_declaration. These properties include:
- declaredLocalVars: stores the local declared variables
- expressionsVariables: a list of all references contained in expressions of the function
- reference_to_constant: includes all Reference_constant expressions which are contained in the function
- reference_to_if_expression: contains all Reference_if_expression expressions
- binaryOperations: stores all Reference_binary_operation expressions
- and others, all hold proper names that explain the purpose

<details>
<summary>click to check the detailed structure of the If_Expression class</summary>
<p>

```python
class Function:
    def __init__(self):
        self.declaredLocalVars = {}
        self.expressionsVariables = []
        self.reference_to_constant = {}
        self.reference_to_if_expression = {}
        self.reference_to_reference = {}
        self.reference_to_functionCall = {}
        self.binaryOperations = {}
        self.method = False
        self.function = False
        self.refToConstCounter = 0
        self.refToBinaryOperCounter = 0
        self.refToRefCounter = 0
        self.refToIfExprCounter = 0
        self.refToFunctionCallCounter = 0
    
    def setName (self, name):
    
    def setFunctionMethod(self, methodFunction):
    
    def addDeclaredLocalVars (self, varCausality, nameAndType, line):

    def addReference_to_constant (self, refConstant):

    def addReference_to_binaryOperation(self, refToBinaryOperation):

    def addReference_to_reference(self, refToRef):
    
    def addReference_to_ifExpression (self, refToIfExpression):
    
    def addReference_to_functionCall (self, refToFunctionCall):
        
    
    def addExpressionVar (self, exprvar):


    def __retrieveIfExprVars (self, ifExpression):

    
    def __retrieveVars_expression(self, expression):
    
    def __retrieveVars_functionCall(self, functionCall):

    def __retrieveVars_binaryOperation (self, binaryOperation):

    def getExpressionsVariables (self):

    def getLocalVariables (self):

    def getReference_to_constant (self):
    
    def getReference_to_if_expression (self):
    
    def getReference_to_reference (self):
    
    def getBinary_operations (self):

    def getReference_to_functionCall (self):
    
    def display (self):
```
</p>
</details>

### The "validate_variables" module

It contains the "validate_variables" function which is the main function for validating all variables.
The "validate_variables" function validates all variables which are listed in the manifest xml file and the variables declared in the algorithm code file. So this function first checks if all variables listed in the xml manifest file are also declared in the alg file. It also checks if declared variables in the alg file are listed in the xml file. Moreover, it checks if variables types and causalities in the xml file match types and causalities in the alg file. 
It has the following format:

**def validate_variables (manifest_vars, algorithm_code_vars)**  
:param manifest_vars: Dictionary for all variables listed in the xml manifest file  
:param algorithm_code_vars: Dictionary for all variables declared in the alg file  
:return: a list of faced errors when running the mentioned validation

### The "validate_functions" module

This module contains the "validate_function" function, this function validates any algorithm code function in terms of contained variables and expressions:
- It starts by checking if all variables contained in expressions are declared either locally in the function or globally in the alg file  
- Checks if types of variables in an expressions match. For example:  
1- Checks if the data type of the reference in a Reference_constant matches the data type of the constant  
2- Checks if data types of both references in Reference_Reference match  
3- Checks if the data type of the reference in a Reference_binary_operation matches the data types of all references included in the BinaryOperation  
4- It also checks all Reference_if_expression, it checks if the conditions are valid (boolean) conditions and it also checks any included expressions  
It has the following format:

**def validate_function(function, varList)**   
:param function: The function object (of type Function)  
:param varList: List of global and local declared variables  
:return: a list of faced errors when running the mentioned validations

## Contributing

More work needs to be done in the following areas:

- Validating conditions of an if_expression needs to be extended
- Also the validation of a binary_operation in case of the left side of the operation is of type boolean (for example, x := (y > z) and (a=b))
- For_loop is implemented only for the (loop-iterator-declaration "in" start-bound ":" termination-bound), more specifically, it is implemented only for the format (for i in 1:50 loop) 
- The following statements needs to be added:  
1- multi_assignment  
2- limit statement  
3- function_call (implemented just to be added to the statement rule)  
4- if_statement (implemented just to be added to the statement rule)  
5- Exception handling

## Contributing, security and repository policies

Please consult the [contributing guidelines](CONTRIBUTING.md) for details on how to report issues and contribute to the repository.

For security issues, please consult the [security guidelines](SECURITY.md).

General MAP eFMI repository setup and configuration policies are summarized in the [MAP eFMI repository policies](https://github.com/modelica/efmi-organization/wiki/Repositories#public-repository-policies) (only relevant for repository administrators and therefor private webpage).
