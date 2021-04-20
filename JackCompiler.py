import sys
import os
from pathlib import Path
import shutil

if_number = 0
while_number = 0
unary_op = {'-':'neg', '~':'not'}
op = {'+':'add', '*':'mult', '&':'and', '<':'lt', '>':'gt', '/':'div', '|':'or', '-':'sub', '=':'eq'}
class_var_dec = ['field', 'static']
types = ['int', 'char', 'boolean']
statements = ['let', 'while', 'if', 'do', 'return']
subDec = ['constructor', 'method', 'function']
keywordConstants = ['true', 'false', 'null', 'this']
keywords = ['class', 'function', 'constructor', 'method', 'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'field', 'static', 'let', 'if', 'while', 'do', 'else', 'return']
symbols = ['=','.', '-', '+', '/', '*', '{', '}', '(', ')', '<', '>', '|', '&', ';', '[', ']', ',', '~']
tokenIndex = 0
analysed_tokens = list()
currentToken = tuple()
output_file = None

def compileClass():
    class_symbol_table = {"field":-1, "static":-1}
    # ignore keyword class because it is the first token
    advanceToken()
    # class Name
    class_symbol_table["className"] = currentToken[1]
    advanceToken()
    eat('{')
    while currentToken[1] != '}':
        if currentToken[1] in class_var_dec:
            class_symbol_table = compileClassVarDec(class_symbol_table)
            print(class_symbol_table)
        elif currentToken[1] in subDec:
            compileSubRoutineDec(class_symbol_table)
    eat('}')

def compileClassVarDec(class_sym_tab):
    static_number = None
    field_number = None
    var_kind = None
    # field/static
    if currentToken[1] == "field":
        class_sym_tab["field"] = class_sym_tab["field"] + 1
        field_number = class_sym_tab["field"]
        var_kind = "this"
    elif currentToken[1] == "static":
        class_sym_tab["static"] = class_sym_tab["static"] + 1
        static_number = class_sym_tab["static"]
        var_kind = "static"
    advanceToken()
    # int, boolean, char
    var_type = currentToken[1]
    advanceToken()
    # varname
    var_name = currentToken[1]
    #add classvar to class symbol table
    if field_number is None:
        number_to_use = static_number
    else:
        number_to_use = field_number
    class_sym_tab[var_name] = (var_kind, var_type, number_to_use)
    advanceToken()
    while currentToken[1] == ',':
        eat(',')
        var_name = currentToken[1]
        number_to_use += 1
        class_sym_tab[var_name] = (var_kind, var_type, number_to_use)
        advanceToken()
    if field_number is None:
        class_sym_tab["static"] = number_to_use
    else:
        class_sym_tab["field"] = number_to_use
    eat(';')
    return class_sym_tab

def compileSubRoutineDec(class_sym_tab):
    # function prologue
    function_prologue = None
    subrtine_sym_tab = {"argument":-1, "local":-1}
    className = class_sym_tab["className"]
    # constructor/method/function
    subroutine_type = currentToken[1]
    if subroutine_type == "method":
        # anchor this on the right object
        code = 'push argument 0\n'
        code = code + 'pop pointer 0\n'
        function_prologue = code
        subrtine_sym_tab = {"argument":0, "local": -1,"this":("argument", className, 0)}
    elif subroutine_type == "constructor":
        #number of fields in class sym tab
        number_of_field_variables = class_sym_tab["field"] + 1
        # call OS memory alloc to set aside location for object data
        code = 'push constant ' + str(number_of_field_variables) + '\n'
        code = code + 'call Memory.alloc 1\n'
        code = code + 'pop pointer 0\n'
        function_prologue = code
        subrtine_sym_tab = subrtine_sym_tab
    elif subroutine_type == "function":
        subrtine_sym_tab = subrtine_sym_tab
    advanceToken()
    # void/types
    if currentToken[1] == 'void' or currentToken[1] in types:
        eat(currentToken[1])
    # className type
    else:
        advanceToken()
    # subroutineName for function declaration
    subroutine_name = className + '.' + currentToken[1]
    advanceToken()
    eat('(')
    subrtine_sym_tab = compileParameterList(subrtine_sym_tab)
    eat(')')
    local_nu, subroutine_vm_codes = compileSubRoutineBody(class_sym_tab, subrtine_sym_tab)
    local_nu += 1
    if subroutine_type == "constructor":
        writeVMcode('function ' + subroutine_name + ' ' + str(local_nu) + '\n')
        writeVMcode(function_prologue)
    elif subroutine_type == "method":
        writeVMcode('function ' + subroutine_name + ' ' + str(local_nu) + '\n')
        writeVMcode(function_prologue)
    else:
        writeVMcode('function ' + subroutine_name + ' ' + str(local_nu) + '\n')
    for line in subroutine_vm_codes:
        writeVMcode(line)
    
        
def compileParameterList(subroutine_symbol_table):
    argument_number = subroutine_symbol_table["argument"]
    var_kind = "argument"
    while currentToken[1] != ')':
        # var type
        var_type = currentToken[1]
        advanceToken()
        # variable name
        var_name = currentToken[1]
        argument_number = argument_number + 1
        subroutine_symbol_table[var_name] = (var_kind, var_type, argument_number)
        advanceToken()
        if currentToken[1] == ',':
            eat(',')
    subroutine_symbol_table["argument"] = argument_number
    return subroutine_symbol_table
        
def compileSubRoutineBody(class_sym_tab, subroutine_symbol_table):
    subroutine_vm_codes = list()
    eat('{')
    while currentToken[1] != '}':
        if currentToken[1] == 'var':
            local_number = subroutine_symbol_table["local"]
            local_number = local_number + 1
            eat('var')
            # variable type
            var_type = currentToken[1]
            advanceToken()
            # varName
            var_name = currentToken[1]
            subroutine_symbol_table[var_name] = ("local", var_type, local_number)
            advanceToken()
            while currentToken[1] == ',':
                eat(',')
                local_number = local_number + 1
                # varName
                var_name = currentToken[1]
                subroutine_symbol_table[var_name] = ("local", var_type, local_number)
                advanceToken()
            eat(';')
            subroutine_symbol_table["local"] = local_number
        # compile statements
        elif currentToken[1] in statements:
            subroutine_vm_codes = compileStatements(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
    eat('}')
    return subroutine_symbol_table["local"], subroutine_vm_codes


def compileStatements(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes):
    while currentToken[1] in statements:
        if currentToken[1] == 'if':
            return compileIfStatement(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
        elif currentToken[1] == 'while':
            return compileWhileStatement(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
        elif currentToken[1] == 'let':
            return compileLetStatement(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
        elif currentToken[1] == 'do':
            return compileDoStatement(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
        elif currentToken[1] == 'return':
            return compileReturnStatement(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)


def compileIfStatement(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes):
    global if_number
    eat('if')
    eat('(')
    # compile the expression
    subroutine_vm_codes = compileExpression(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
    code = 'not\n'
    subroutine_vm_codes.append(code)
    eat(')')
    label_false = 'if_false' + str(if_number)
    label_end = 'if_end' + str(if_number)
    if_number = if_number + 1
    # if the not(condition) is true, go to else
    code = 'if-goto ' + label_false + '\n'
    subroutine_vm_codes.append(code)
    eat('{')
    # compile condition is true statements
    subroutine_vm_codes = compileStatements(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
    eat('}')
    code = 'goto ' + label_end + '\n'
    subroutine_vm_codes.append(code)
    if currentToken[1] == 'else':
        # setup else statement block
        code = 'label ' + label_false + '\n'
        subroutine_vm_codes.append(code)
        eat('else')
        eat('{')
        # compile not(condition) is true statements
        subroutine_vm_codes = compileStatements(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
        eat('}')
        code = 'label ' + label_end + '\n'
        subroutine_vm_codes.append(code)
    else:
        # when the if has no else block, just set a jump location for when the condition is false
        code = 'label ' + label_false + '\n'
        subroutine_vm_codes.append(code)
    return subroutine_vm_codes

def compileWhileStatement(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes):
    global while_number
    label_start = 'while_begin' + str(while_number)
    label_true = 'while_true' + str(while_number)
    label_end = 'while_end' + str(while_number)
    code = 'label ' + label_start + '\n'
    subroutine_vm_codes.append(code)
    eat('while')
    eat('(')
    subroutine_vm_codes = compileExpression(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
    eat(')')
    eat('{')
    # if condition is true
    code = 'if-goto ' + label_true + '\n'
    # if condition is false
    code = code + ('goto ' + label_end +'\n')
    subroutine_vm_codes.append(code)
    code = 'label ' + label_true + '\n'
    subroutine_vm_codes.append(code)
    while currentToken[1] != '}':
        # compile the while block statements
        subroutine_vm_codes = compileStatements(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
    eat('}')

    # go back to while loop condition and evaluate
    code = 'goto ' + label_start + '\n'
    subroutine_vm_codes.append(code)

    # end of while block - outside while block
    code = 'label ' + label_end + '\n'
    subroutine_vm_codes.append(code)
    while_number = while_number + 1
    return subroutine_vm_codes

def compileLetStatement(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes):
    eat('let')
    segment_map = None
    if currentToken[0] =='identifier':
        first = currentToken
        advanceToken()
        # Array reference
        if currentToken[1] == '[':
            # push array name on stack
            var_name = first[1]
            if var_name in subroutine_symbol_table.keys():
                props = subroutine_symbol_table[var_name]
                var_kind = props[0]
                var_number = props[2]
                segment_map = var_kind + ' ' + str(var_number)
            elif var_name in class_sym_tab.keys():
                props = class_sym_tab[var_name]
                var_kind = props[0]
                var_number = props[2]
                segment_map = var_kind + ' ' + str(var_number)
            code = 'push ' + segment_map + '\n'
            subroutine_vm_codes.append(code)
            eat('[')
            subroutine_vm_codes = compileExpression(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
            eat(']')
            # add array base + value of expression
            code = 'add\n'
            subroutine_vm_codes.append(code)
            eat('=')
            subroutine_vm_codes = compileExpression(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
            eat(';')
            code = 'pop temp 0\n'
            code = code + 'pop pointer 1\n'
            code = code + 'push temp 0\n'
            code = code + 'pop that 0\n'
            subroutine_vm_codes.append(code)
        # usual variable name
        else:
            var_name = first[1]
            if var_name in subroutine_symbol_table.keys():
                props = subroutine_symbol_table[var_name]
                var_kind = props[0]
                var_number = props[2]
                segment_map = var_kind + ' ' + str(var_number)
            elif var_name in class_sym_tab.keys():
                props = class_sym_tab[var_name]
                var_kind = props[0]
                var_number = props[2]
                segment_map = var_kind + ' ' + str(var_number)
            else:
                exitCompilation()
            eat('=')  
            subroutine_vm_codes = compileExpression(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
            eat(';')
            code = 'pop ' + segment_map +'\n'
            subroutine_vm_codes.append(code)
    else:
        exitCompilation()
    return subroutine_vm_codes
    

def compileDoStatement(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes):
    eat('do')
    if currentToken[0] == 'identifier':
        first = currentToken
        advanceToken()

        # identifier()
        if currentToken[1] == '(':
            function_name = first[1]
            eat('(')
            subroutine_vm_codes = compileExpressionList(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
            eat(')')
            number_of_arguments = subroutine_vm_codes.pop()
            # call function
            code = 'call ' + function_name + ' ' + str(number_of_arguments) + '\n'
            subroutine_vm_codes.append(code)
        
        # className.method() or object.method
        elif currentToken[1] == '.':
            # if first character is lowercase, it is an obj.method call
            if first[1].islower():
                class_name = class_sym_tab["className"]
                obj_name = first[1]

                if obj_name in subroutine_symbol_table.keys():
                    props = subroutine_symbol_table[obj_name]
                    var_kind = props[0]
                    var_number = props[2]
                    segment_map = var_kind + ' ' + str(var_number)
                    # push segment map
                    code = 'push ' + segment_map + '\n'
                    subroutine_vm_codes.append(code)
                
                elif obj_name in class_sym_tab.keys():
                    props = class_sym_tab[obj_name]
                    var_kind = props[0]
                    var_number = props[2]
                    segment_map = var_kind + ' ' + str(var_number)
                    # push segment map
                    code = 'push ' + segment_map + '\n'
                    subroutine_vm_codes.append(code)

                eat('.')
                subroutine_name = currentToken[1]
                function_name = class_name + '.' + subroutine_name
                advanceToken()
                eat('(')
                subroutine_vm_codes = compileExpressionList(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
                eat(')')
                # call function here
                number_of_arguments = subroutine_vm_codes.pop()
                code = 'call ' + function_name + ' ' + str(number_of_arguments+1) + '\n'
                subroutine_vm_codes.append(code)

            else:
                class_name = first[1]
                eat('.')
                subroutine_name = currentToken[1]
                function_name = class_name + '.' + subroutine_name
                advanceToken()
                eat('(')
                subroutine_vm_codes = compileExpressionList(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
                eat(')')
                # call function here
                number_of_arguments = subroutine_vm_codes.pop()
                code = 'call ' + function_name + ' ' + str(number_of_arguments) + '\n'
                subroutine_vm_codes.append(code)
        else:
            exitCompilation()
    else:
        exitCompilation()
    eat(';')
    # pop the void return value into temp 0 because it is not needed
    code  = 'pop temp 0\n'
    subroutine_vm_codes.append(code)
    return subroutine_vm_codes

def compileReturnStatement(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes):
    eat('return')
    if currentToken[1] != ';':
        if currentToken[1] == "this":
            advanceToken()
            eat(';')
            code = 'push pointer 0\n'
            code = code + 'return\n'
            subroutine_vm_codes.append(code)
        else:
            subroutine_vm_codes = compileExpression(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
            eat(';')
            # return
            code = 'return\n'
            subroutine_vm_codes.append(code)
    else:    
        eat(';')
        # push constant 0
        code = 'push constant 0\n'
        subroutine_vm_codes.append(code)
        # return
        code = 'return\n'
        subroutine_vm_codes.append(code)
    return subroutine_vm_codes

def compileExpression(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes):
    subroutine_vm_codes = compileTerm(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
    while currentToken[1] in op.keys():
        operator = op[currentToken[1]]
        advanceToken()
        subroutine_vm_codes = compileTerm(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
        #we push operator here
        if operator == "mult":
            code = 'call Math.multiply 2\n'
        elif operator == "div":
            code = 'call Math.divide 2\n'
        else:
            code = operator + '\n'
        subroutine_vm_codes.append(code)
    return subroutine_vm_codes

def compileExpressionList(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes):
    number_of_args = 0
    while currentToken[1] != ')':
        subroutine_vm_codes = compileExpression(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
        number_of_args = number_of_args + 1
        if currentToken[1] == ',':
            eat(',')
            continue
    subroutine_vm_codes.append(number_of_args)
    return subroutine_vm_codes

def compileTerm(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes):
    # if it is an int or str constant, we ouptut and advance token
    if currentToken[0] == 'integerConstant':
        integer = currentToken[1]
        # push integer constant
        code = 'push constant '+integer+'\n'
        subroutine_vm_codes.append(code)
        advanceToken()

    elif currentToken[0] == 'stringConstant':
        string = currentToken[1]
        len_of_string = len(currentToken[1])
        code = 'push constant ' + str(len_of_string) + '\n'
        code = code + 'call String.new 1\n'
        subroutine_vm_codes.append(code)
        for character in string:
            ascii_code = ord(character)
            code = 'push constant ' + str(ascii_code) + '\n'
            code = code + 'call String.appendChar 2\n'
            subroutine_vm_codes.append(code)
        advanceToken()

    # if it is a keyword constant, we ouptut and advance token
    elif currentToken[1] in keywordConstants:
        if currentToken[1] == "null" or currentToken[1] == "false":
            code = 'push constant 0\n'
            subroutine_vm_codes.append(code)
        elif currentToken[1] == "true":
            code = 'push constant 0\n'
            code = code + 'not\n'
            subroutine_vm_codes.append(code)
        advanceToken()

    # expression in parantheses eg sum = (2+3)
    elif currentToken[1] == '(':
        eat('(')
        subroutine_vm_codes = compileExpression(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
        eat(')')
        

    # but if it is an identifier, the we need to check next token
    elif currentToken[0] == 'identifier':
        first = currentToken
        # get the next token, current token refers to it
        advanceToken()

        # array reference
        if currentToken[1] == '[':
            segment_map = None
            # push array name on stack
            var_name = first[1]
            if var_name in subroutine_symbol_table.keys():
                props = subroutine_symbol_table[var_name]
                var_kind = props[0]
                var_number = props[2]
                segment_map = var_kind + ' ' + str(var_number)
            elif var_name in class_sym_tab.keys():
                props = class_sym_tab[var_name]
                var_kind = props[0]
                var_number = props[2]
                segment_map = var_kind + ' ' + str(var_number)
            code = 'push ' + segment_map + '\n'
            subroutine_vm_codes.append(code)
            eat('[')
            subroutine_vm_codes = compileExpression(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
            eat(']')
            code = 'add\n'
            code = code + 'pop pointer 1\n'
            code = code + 'push that 0\n'
            subroutine_vm_codes.append(code)
        # subroutine call eg Main.output()
        elif currentToken[1] == '.':
            # if first character is lowercase, it is an obj.method call
            if first[1].islower():
                class_name = class_sym_tab["className"]
                obj_name = first[1]

                if obj_name in subroutine_symbol_table.keys():
                    props = subroutine_symbol_table[obj_name]
                    var_kind = props[0]
                    var_number = props[2]
                    segment_map = var_kind + ' ' + str(var_number)
                    # push segment map
                    code = 'push ' + segment_map + '\n'
                    subroutine_vm_codes.append(code)
                
                elif obj_name in class_sym_tab.keys():
                    props = class_sym_tab[obj_name]
                    var_kind = props[0]
                    var_number = props[2]
                    segment_map = var_kind + ' ' + str(var_number)
                    # push segment map
                    code = 'push ' + segment_map + '\n'
                    subroutine_vm_codes.append(code)

                eat('.')
                subroutine_name = currentToken[1]
                function_name = class_name + '.' + subroutine_name
                advanceToken()
                eat('(')
                subroutine_vm_codes = compileExpressionList(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
                eat(')')
                # call function here
                number_of_arguments = subroutine_vm_codes.pop()
                code = 'call ' + function_name + ' ' + str(number_of_arguments+1) + '\n'
                subroutine_vm_codes.append(code)

            else:
                class_name = first[1]
                eat('.')
                subroutine_name = currentToken[1]
                function_name = class_name + '.' + subroutine_name
                advanceToken()
                eat('(')
                subroutine_vm_codes = compileExpressionList(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
                eat(')')
                # call function here
                number_of_arguments = subroutine_vm_codes.pop()
                code = 'call ' + function_name + ' ' + str(number_of_arguments) + '\n'
                subroutine_vm_codes.append(code)

        # subroutine call eg cry()
        elif currentToken[1] == '(':
            class_name = class_sym_tab["className"]
            function_name = class_name + first[1]
            eat('(')
            subroutine_vm_codes = compileExpressionList(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
            eat(')')
            # call function here
            number_of_arguments = subroutine_vm_codes.pop()
            code = 'call ' + function_name + ' ' + str(number_of_arguments) + '\n'
            subroutine_vm_codes.append(code)

        # else a usual varname
        else:
            var_name = first[1]
            if var_name in subroutine_symbol_table.keys():
                props = subroutine_symbol_table[var_name]
                var_kind = props[0]
                var_number = props[2]
                segment_map = var_kind + ' ' + str(var_number)
                # push segment map
                code = 'push ' + segment_map + '\n'
                subroutine_vm_codes.append(code)
                
            elif var_name in class_sym_tab.keys():
                props = class_sym_tab[var_name]
                var_kind = props[0]
                var_number = props[2]
                segment_map = var_kind + ' ' + str(var_number)
                # push segment map
                code = 'push ' + segment_map + '\n'
                subroutine_vm_codes.append(code)

    # if -7 or ~term
    elif currentToken[1] in unary_op.keys():
        operator = unary_op[currentToken[1]]
        advanceToken()
        subroutine_vm_codes = compileTerm(class_sym_tab, subroutine_symbol_table, subroutine_vm_codes)
        # do operator action
        code = operator + '\n'
        subroutine_vm_codes.append(code)
        

    else:
        exitCompilation()
    return subroutine_vm_codes

def eat(currentTokenCompare):
    
    if currentToken[1] == currentTokenCompare:
        if currentToken[1] == '>':
            advanceToken()
        elif currentToken[1] == '<':  
            advanceToken()
        elif currentToken[1] == '&':
            advanceToken()
        else:
            advanceToken()
    else:
        print(currentTokenCompare)
        exitCompilation()

def advanceToken():
    global tokenIndex
    global currentToken
    tokenIndex += 1
    if tokenIndex < len(analysed_tokens):
        currentToken = analysed_tokens[tokenIndex]

def exitCompilation():
    print(currentToken)
    print(tokenIndex)
    print(analysed_tokens[tokenIndex-1])
    print(analysed_tokens[tokenIndex+1])
    print('Syntax error')
    exit()


def tokenizer(jackFile):
    tokensList = list()
    with open(jackFile, 'r') as TokenizerInput:
        line = TokenizerInput.readline()
        while line != '':
            if line.strip().startswith('/') or line.startswith('\n') or line.strip().startswith('*'):
                line = TokenizerInput.readline()
                continue
            else:
                tokenLine = line.strip().split('//')[0]

                if tokenLine != '':
                    for letter in tokenLine:
                        tokensList.append(letter)
                line = TokenizerInput.readline()
    # print(tokensList)
    len_of_tokensList = len(tokensList)

    tokensListIndex = 0
    tokenString = ""
    
    while tokensListIndex < len_of_tokensList:
        # check if we reached a space
        if tokensList[tokensListIndex] == ' ':
            # do we have integer constant
            if tokenString != "":
                if tokenString.isnumeric():
                    token = ("integerConstant",tokenString)
                    analysed_tokens.append(token)
                    tokenString = ""
                    tokensListIndex += 1
                elif tokenString in keywords:
                    token = ("keyword", tokenString)
                    analysed_tokens.append(token)
                    tokenString = ""
                    tokensListIndex += 1
                else:
                    token = ("identifier", tokenString)
                    analysed_tokens.append(token)
                    tokenString = ""
                    tokensListIndex += 1
            else:
                tokensListIndex += 1


        # check if we reached a symbol
        elif tokensList[tokensListIndex] in symbols:
            # if we have a symbol, check to see if token string is empty
            if tokenString != "":
                if tokenString.isnumeric():
                    token = ("integerConstant",tokenString)
                    analysed_tokens.append(token)
                    token = ("symbol", tokensList[tokensListIndex])
                    analysed_tokens.append(token)
                    tokenString = ""
                    tokensListIndex += 1
                elif tokenString in keywords:
                    token = ("keyword", tokenString)
                    analysed_tokens.append(token)
                    token = ("symbol", tokensList[tokensListIndex])
                    analysed_tokens.append(token)
                    tokenString = ""
                    tokensListIndex += 1
                else:
                    token = ("identifier", tokenString)
                    analysed_tokens.append(token)
                    token = ("symbol", tokensList[tokensListIndex])
                    analysed_tokens.append(token)
                    tokenString = ""
                    tokensListIndex += 1

            else:
                token = ("symbol", tokensList[tokensListIndex])
                analysed_tokens.append(token)
                tokensListIndex += 1
        
        # else append to token string
        else:
            # check if we dont have string constant
            if tokensList[tokensListIndex] != '"':
                tokenString += tokensList[tokensListIndex]
                tokensListIndex += 1
            
            # if we have string constant, form it and continue the loop
            else:
                stringConst = ''
                tokensListIndex += 1
                while tokensListIndex < len_of_tokensList and tokensList[tokensListIndex] != '"':
                    stringConst += tokensList[tokensListIndex]
                    tokensListIndex += 1
                analysed_tokens.append(("stringConstant", stringConst))
                tokensListIndex += 1
    # print(analysed_tokens)

def writeVMcode(string):
    with open(output_file, 'a') as vmfile:
        vmfile.write(string)


def openDirForAnalysis(directory):
    directory = Path(directory)
    for jackFile in os.listdir(directory):
        if jackFile.endswith('.jack'):
            global output_file
            output_file = jackFile.split('.')[0]+'.vm'

            file_to_analyze = directory/jackFile
            tokenizer(file_to_analyze)

            global currentToken
            currentToken = analysed_tokens[tokenIndex]
            compileClass()

            shutil.move(output_file, directory)
            output_file = None


def openFileForAnalysis(jackFile):
    tokenizer(jackFile)
    global output_file
    output_file = jackFile.split('.')[0]+'.vm'
    global currentToken
    currentToken = analysed_tokens[tokenIndex]
    compileClass()

def main():

    fileOrDir = sys.argv[1]
    if os.path.isdir(fileOrDir):
        directory = fileOrDir
        openDirForAnalysis(directory)
    else:
        jackFile = fileOrDir
        openFileForAnalysis(jackFile)
        

if __name__ == "__main__":
    main()