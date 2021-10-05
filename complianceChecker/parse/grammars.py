#This file is a part of the eFMI Compliance Checker which is a python open-source 
# library intended for checking the compliance of an eFMU with the standard specification

#Copyright © ESI ITI GmbH, 2021
               
#This program is a free software distributed WITHOUT ANY WARRANTY and the use is 
#completely at your own risk; it can be redistributed and/or modified under the 
#terms of the BSD 3-Clause license. For license conditions (including the 
#disclaimer of warranty) visit: https://opensource.org/licenses/BSD-3-Clause.

#ESI ITI GmbH, Zwinger-Forum, Schweriner Straße 1, 01067 Dresden, Germany

grammar = r'''
    start: block

    block: ("block" name (state_entity_declaration)* "protected" protected_declaration "public" public_declaration END name ";")
    
    protected_declaration: (state_compartment_declaration)* ([DATA_FLOW_DIRECTION] variable_declaration)* (error_signal_declaration)* (function_declaration)*

    public_declaration: (function_declaration)*
 
    state_compartment_declaration: "record" name (state_entity_declaration)* END name ";"

    error_signal_declaration: "signal" identifier ";"
 
    function_declaration: FUNCTION_METHOD name [signal_interface] (parameter_var_delaration)* "algorithm" (statement)* END name ";"

    FUNCTION_METHOD: "function" | "method"

    END: "end"
    
    signal_interface: "signals" identifier ("," identifier)* ";" 

    parameter_var_delaration: (parameter_declaration)* ["protected" (local_variable_declaration)*]
    
    state_entity_declaration: ( DATA_FLOW_DIRECTION variable_declaration)
    
    DATA_FLOW_DIRECTION: ("input" | "output" | "parameter" | CONSTANT)
 
    parameter_declaration: LOCAL_DATA_FLOW_DIRECTION variable_declaration
 
    local_variable_declaration: variable_declaration
 
    LOCAL_DATA_FLOW_DIRECTION: "input" | "output"
 
    variable_declaration: (type | state_compartment_reference) variable_name [constant_dimensions] [range_specification] ";"

    range_specification: "(" (lower_bound | upper_bound | (lower_bound "," upper_bound)) ")"
    lower_bound: "min" "=" ["-"] (integer | number)
    upper_bound: "max" "=" ["-"] (integer | number)

    //type_compartment_reference: type //| state_compartment_reference

    type: PRIMITIVE_TYPE

    //type: ("Boolean" | "Integer" | "Real")

    state_compartment_reference: name

    variable_name: name                

    PRIMITIVE_TYPE: "Boolean" | "Integer" | "Real"
 
    record_reference: name
 
    constant_dimensions: OPEN_BRACKET derived_or_constat_dimension (COMMA derived_or_constat_dimension)* CLOSE_BRACKET
    
    derived_or_constat_dimension: (DERIVED_DIMENSION | constant_scalar_integer_expression)

    DERIVED_DIMENSION: ":"    
    
    expression: constant
        | reference
        | dimension_query
        | function_call
        | if_expression
        | unary_operation
        | parenthesized_expression
        | multi_dimension_constructor
        | binary_operation
        | minmax_expression
    
    new_expression: constant
        | reference
        | dimension_query
        | function_call
        | if_expression
        | unary_operation
        | parenthesized_expression
        | multi_dimension_constructor
        | minmax_expression

    
 
    parenthesized_expression: OPEN_PARENTHESES expression CLOSE_PARENTHESES
 
    dimension_query: "size" "(" reference COMMA constant_scalar_integer_expression ")"

    constant_scalar_integer_expression: expression
 
    unary_operation: UNARY_OPERATOR ( constant | reference | dimension_query | function_call | parenthesized_expression | if_expression)
 
    UNARY_OPERATOR: MINUS | "not"
 
    //binary_operation: expression binary_operator expression

    binary_operation: or_operation

    or_operation: and_operation         
        | or_operation OR and_operation         -> or
    
    and_operation: equal_operation      
        | and_operation AND equal_operation     -> and

    equal_operation: relational_operation   -> relational
        | equal_operation EQUAL_EQUAL relational_operation      -> equal
        | equal_operation NOT_EQUAL relational_operation        -> not_equal

    relational_operation: sum_operation    
        | relational_operation SMALLER sum_operation            -> smaller
        | relational_operation GREATER sum_operation            -> greater
        | relational_operation SMALLER_EQUAL sum_operation      -> smaller_equal
        | relational_operation GREATER_EQUAL sum_operation      -> greater_equal
    
    sum_operation: mul_operation
        | sum_operation PLUS mul_operation  -> add
        | sum_operation MINUS mul_operation -> minus
    
    mul_operation: power_operation      
        | mul_operation MULTIPLICATION power_operation  -> mul
        | mul_operation DIVISION power_operation        -> div
    
    power_operation: new_expression
        | power_operation POWER expression  -> power
 
    //binary_operator: ARITHMETIC_OPERATOR | RELATIONAL_OPERATOR | LOGICAL_OPERATOR
    binary_operator: arithmetic_operator | relational_operator | logical_operator

    minmax_expression: name EQUAL (constant | ("-" constant))

    plus: PLUS //.6
    PLUS: "+"

    minus: MINUS //.6
    MINUS: "-"
 
    arithmetic_operator: plus | minus | multiplication | division | power

    relational_operator: smaller_equal | greater_equal | not_equal | smaller | greater | equal_equal
 
    //LOGICAL_OPERATOR: AND | OR
    logical_operator : and | or
    

    POWER : "^"
    power: POWER //.8

    OR: "or"
    or: OR //.2

    AND: "and"
    and: AND //.3

    EQUAL_EQUAL: "=="
    equal_equal: EQUAL_EQUAL //.4

    NOT_EQUAL: "<>"
    not_equal: NOT_EQUAL //.4

    SMALLER: "<"
    smaller: SMALLER //.5

    GREATER: ">"
    greater: GREATER //.5

    SMALLER_EQUAL: "<="
    smaller_equal: SMALLER_EQUAL //.5

    GREATER_EQUAL: ">="
    greater_equal: GREATER_EQUAL //.5

    DIVISION: "/"
    division: DIVISION //.7

    MULTIPLICATION: "*"
    multiplication: MULTIPLICATION //.7

    multi_dimension_constructor: "{" multi_dimension_constructor_element (COMMA multi_dimension_constructor_element)* "}"
 
    multi_dimension_constructor_element: expression | multi_dimension_constructor
 
    function_call: name "(" [ expression (COMMA expression)* ] ")"
 
    if_expression: OPEN_PARENTHESES IF expression THEN expression elseif_expression* ELSE expression CLOSE_PARENTHESES
    
    elseif_expression: ELSEIF expression THEN expression

    //references
    reference: local_reference | state_reference
 
    local_reference: name [computed_dimensions]
 
    state_reference: SELF DOT name [computed_dimensions] (DOT name [computed_dimensions])*
 
    computed_dimensions: OPEN_BRACKET constant_scalar_integer_expression (COMMA constant_scalar_integer_expression)* CLOSE_BRACKET
 
    //statements
    statement: (limit_statement | function_call | single_assignment | multi_assignment | if_statement | for_loop | error_signal_statement) ";"

    limit_statement: "limit" ("self" | reference) ("," ("self" | reference))*
 
    single_assignment: reference ASSIGNMENT expression
 
    multi_assignment: "(" [reference (COMMA reference)*] ")" ASSIGNMENT function_call
 
    if_statement: "if" (expression | error_signal_check) "then" (statement)* elseif_statement* ["else" (statement)*] END "if"

    error_signal_check:"signal" [identifier] [["not"] "in" identifier ("," identifier)*] ["or" expression]
    
    elseif_statement: "elseif" (expression | error_signal_check) "then" (statement)*   
    
    for_loop: "for" bounded_iteration "loop" (statement)* END "for"
 
    bounded_iteration: [loop_iterator_declaration "in"] start_bound [":" iteration_step_size] ":" termination_bound
 
    loop_iterator_declaration: name
 
    start_bound: constant_scalar_integer_expression
 
    iteration_step_size: constant_scalar_integer_expression
 
    termination_bound: constant_scalar_integer_expression

    error_signal_statement: "signal" identifier ("," identifier)*

    constant: boolean | number

    integer: ZERO | positive_integer

    MINUS_ZERO: "-0"

    positive_integer: NON_ZERO_DIGIT (NON_ZERO_DIGIT | ZERO)*

    negative_integer: "-" positive_integer

    number: (integer [decimal_places] [exponent]) //- (integer)

    //integer_places: integer

    decimal_places: DOT (NON_ZERO_DIGIT | ZERO)*

    exponent: ( EXP_LOWER | EXP ) (PLUS | MINUS) (NON_ZERO_DIGIT | ZERO)*

    boolean: BOOLEAN

    BOOLEAN: "false" | "true"

    keyword: "block" | "protected" | "public"
        | "record" | "end"
        | "function" | "method" | "algorithm"
        | "input" | "output"
        | "Boolean" | "Integer" | "Real"
        | "if" | "then" | "elseif" | "else" |
        | "for" | "in" | "loop"
        | "and" | "or" | "not" |
        | "size"
        | "self"
        // reserved for future extensions: 
        | "while" | "do" | "until"
        | "break" | "return"
        | "enumeration"
        | "__" identifier
  
    name: ID | quoted_identifier
    
    identifier: (ALPHABETIC_CHARACTER (ALPHABETIC_CHARACTER | UNDERSCORE | NON_ZERO_DIGIT | ZERO)*) //- (keyword)

    ID: /[A-Za-z][A-Za-z0-9\d_]*/
 
    quoted_identifier: "'" (PREV OPEN_PARENTHESES scalarized_reference CLOSE_PARENTHESES
                  | DERIV OPEN_PARENTHESES quoted_identifier_higher_order_derivative CLOSE_PARENTHESES
                  | scalarized_reference)"'"
    
    quoted_identifier_higher_order_derivative: scalarized_reference
                  | DERIV OPEN_PARENTHESES quoted_identifier_higher_order_derivative CLOSE_PARENTHESES 

    PREV: "previous"

    DERIV: "derivative"

    OPEN_PARENTHESES: "("

    CLOSE_PARENTHESES: ")"

    OPEN_BRACKET: "["

    CLOSE_BRACKET: "]"

    COMMA: ","

    IF: "if"

    ELSEIF: "elseif"

    ELSE: "else"

    THEN: "then"

    scalarized_reference: identifier [fixed_dimensions] (DOT identifier [fixed_dimensions])*
 
    fixed_dimensions: OPEN_BRACKET positive_integer (COMMA positive_integer)* CLOSE_BRACKET

    white_space: (_SPACE | NEW_LINE_CHARACTER | comment)* //- ( )
 
    NEW_LINE_CHARACTER: ( "\r" | "\n" ) | ( "\r" "\n" )
        //? carriage return, line feed or carriage return followed by line feed
        //(ISO/IEC 10646:2017 code point 13 or 10 or 13 followed by 10) ?
 
    comment: single_line_comment //| multi_line_comment
 
    single_line_comment: "//" (character_or_space)* "\n" //- (new_line_character)
 
    //multi_line_comment: "/*" (character)* "*/"  // - ( (character)* "*/" (character)* )

    character_or_space: character | _SPACE

    //MULTILINE_COMMENT: /\/\/[^\n]*/

    MULTILINE_COMMENT: /\/\*.*?\*\//s
    COMMENT: "//" /(.)+/ NEWLINE 

    character: LOWER | UPPER | (NON_ZERO_DIGIT | ZERO) | SPECIAL //? any valid ISO/IEC 10646:2017 code point ?

    EXP_LOWER: "e"
    
    EXP: "E"

    ALPHABETIC_CHARACTER: "a" | "b" | "c" | "d" | EXP_LOWER | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m"
        | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z"
        | "A" | "B" | "C" | "D" | EXP | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M"
        | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z"


    LOWER: "a" | "b" | "c" | "d" | EXP_LOWER | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" 
     | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z"

    UPPER: "A" | "B" | "C" | "D" | EXP | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M"
        | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z"

    NON_ZERO_DIGIT: "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"

    ZERO: "0"

    //NON_ZERO_DIGIT: "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"

    DOT: "."

    EQUAL: "="
    
    SPECIAL: "-" | UNDERSCORE | "'" | "&" | "\"" | OPEN_PARENTHESES | CLOSE_PARENTHESES | MULTIPLICATION | PLUS | COMMA | DOT | DIVISION 
       | ":" | ";" | SMALLER | EQUAL | GREATER | "#"
    
    

    SELF: "self"

    ASSIGNMENT: ":="

    UNDERSCORE: "_"

    CONSTANT: "constant"
    PARAMETER: "parameter"
    
    _SPACE: " " | "\t"
    %import common.NEWLINE
    
       
        
    //COMMENT: "/*" /(.|\n|\r)+/ "*/"                
    //        |  "//" /(.)+/ NEWLINE

    %ignore MULTILINE_COMMENT
    %ignore COMMENT
    %ignore /\s/s
    %ignore _SPACE
    %ignore "\n"
    %ignore /[\t \f]+/  // WS
    %ignore /\\[\t \f]*\r?\n/   // LINE_CONT

'''
