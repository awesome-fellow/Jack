import sys
import os
from pathlib import Path
import shutil

unary_op = ['-', '~']
op = ['+', '*', '&', '<', '>', '/', '|', '-', '=']
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
    output = '<class>\n'
    writeXML(output)
    # keyword class
    output = '<'+currentToken[0]+'> '+currentToken[1]+' </'+currentToken[0]+'>\n'
    writeXML(output)
    advanceToken()
    # class Name
    output = '<'+currentToken[0]+'> '+currentToken[1]+' </'+currentToken[0]+'>\n'
    writeXML(output)
    advanceToken()
    eat('{')
    while currentToken[1] != '}':
        if currentToken[1] in class_var_dec:
            compileClassVarDec()
        elif currentToken[1] in subDec:
            compileSubRoutineDec()
    eat('}')
    writeXML('</class>\n')

def compileClassVarDec():
    writeXML('<classVarDec>\n')
    # field/static
    eat(currentToken[1])
    # int, boolean, char
    eat(currentToken[1])
    # varname
    output = '<'+currentToken[0]+'> '+currentToken[1]+' </'+currentToken[0]+'>\n'
    writeXML(output)
    advanceToken()
    while currentToken[1] == ',':
        eat(',')
        output = '<'+currentToken[0]+'> '+currentToken[1]+' </'+currentToken[0]+'>\n'
        writeXML(output)
        advanceToken()
    eat(';')
    writeXML('</classVarDec>\n')

def compileSubRoutineDec():
    writeXML('<subroutineDec>\n')
    # constructor/method/function
    eat(currentToken[1])
    # void/types
    if currentToken[1] == 'void' or currentToken[1] in types:
        eat(currentToken[1])
    # className type
    else:
        output = '<'+currentToken[0]+'> '+currentToken[1]+' </'+currentToken[0]+'>\n'
        writeXML(output)
        advanceToken()
    # subroutineName
    output = '<'+currentToken[0]+'> '+currentToken[1]+' </'+currentToken[0]+'>\n'
    writeXML(output)
    advanceToken()
    eat('(')
    compileParameterList()
    eat(')')
    compileSubRoutineBody()
    writeXML('</subroutineDec>\n')
    
        
def compileParameterList():
    writeXML('<parameterList>\n')
    while currentToken[1] != ')':
        # var type
        output = '<'+currentToken[0]+'> '+currentToken[1]+' </'+currentToken[0]+'>\n'
        writeXML(output)
        advanceToken()
        # variable name
        output = '<'+currentToken[0]+'> '+currentToken[1]+' </'+currentToken[0]+'>\n'
        writeXML(output)
        advanceToken()
        if currentToken[1] == ',':
            eat(',')
    writeXML('</parameterList>\n')
        
def compileSubRoutineBody():
    writeXML('<subroutineBody>\n')
    eat('{')
    while currentToken[1] != '}':
        if currentToken[1] == 'var':
            writeXML('<varDec>\n')
            eat('var')
            # variable type
            output = '<'+currentToken[0]+'> '+currentToken[1]+' </'+currentToken[0]+'>\n'
            writeXML(output)
            advanceToken()
            # varName
            output = '<'+currentToken[0]+'> '+currentToken[1]+' </'+currentToken[0]+'>\n'
            writeXML(output)
            advanceToken()
            if currentToken[1] == ',':
                eat(',')
                # varName
                output = '<'+currentToken[0]+'> '+currentToken[1]+' </'+currentToken[0]+'>\n'
                writeXML(output)
                advanceToken()
            eat(';')
            writeXML('</varDec>\n')
        # compile statements
        elif currentToken[1] in statements:
            compileStatements()
    eat('}')
    writeXML('</subroutineBody>\n')


def compileStatements():
    writeXML('<statements>\n')
    while currentToken[1] in statements:
        if currentToken[1] == 'if':
            compileIfStatement()
        elif currentToken[1] == 'while':
            compileWhileStatement()
        elif currentToken[1] == 'let':
            compileLetStatement()
        elif currentToken[1] == 'do':
            compileDoStatement()
        elif currentToken[1] == 'return':
            compileReturnStatement()
    writeXML('</statements>\n')


def compileIfStatement():
    writeXML('<ifStatement>\n')
    eat('if')
    eat('(')
    compileExpression()
    eat(')')
    eat('{')
    compileStatements()
    eat('}')
    if currentToken[1] == 'else':
        eat('else')
        eat('{')
        compileStatements()
        eat('}')
    writeXML('</ifStatement>\n')

def compileWhileStatement():
    writeXML('<whileStatement>\n')
    eat('while')
    eat('(')
    compileExpression()
    eat(')')
    eat('{')
    if currentToken[1] != '}':
        compileStatements()
    eat('}')
    writeXML('</whileStatement>\n')

def compileLetStatement():
    writeXML('<letStatement>\n')
    eat('let')
    if currentToken[0] =='identifier':
        first = currentToken
        advanceToken()
        # Array reference
        if currentToken[1] == '[':
            output = '<'+first[0]+'> '+first[1]+' </'+first[0]+'>\n'
            writeXML(output)
            eat('[')
            compileExpression()
            eat(']')
        # usual variable name
        else:
            output = '<'+first[0]+'> '+first[1]+' </'+first[0]+'>\n'
            writeXML(output)
    else:
        exitCompilation()
    eat('=')
    compileExpression()
    eat(';')
    writeXML('</letStatement>\n')
    

def compileDoStatement():
    writeXML('<doStatement>\n')
    eat('do')
    if currentToken[0] == 'identifier':
        first = currentToken
        advanceToken()

        # identifier()
        if currentToken[1] == '(':
            output = '<'+first[0]+'> '+first[1]+' </'+first[0]+'>\n'
            writeXML(output)
            eat('(')
            compileExpressionList()
            eat(')')
        
        # className.method()
        elif currentToken[1] == '.':
            output = '<'+first[0]+'> '+first[1]+' </'+first[0]+'>\n'
            writeXML(output)
            eat('.')
            output = '<'+currentToken[0]+'> '+currentToken[1]+' </'+currentToken[0]+'>\n'
            writeXML(output)
            advanceToken()
            eat('(')
            compileExpressionList()
            eat(')')
        else:
            exitCompilation()
    else:
        exitCompilation()
    eat(';')
    writeXML('</doStatement>\n')

def compileReturnStatement():
    writeXML('<returnStatement>\n')
    eat('return')
    if currentToken[1] != ';':
        compileExpression()
        eat(';')
    else:    
        eat(';')
    writeXML('</returnStatement>\n')

def compileExpression():
    writeXML('<expression>\n')
    compileTerm()
    while currentToken[1] in op:
        eat(currentToken[1])
        compileTerm()    
    writeXML('</expression>\n')

def compileExpressionList():
    writeXML('<expressionList>\n')
    while currentToken[1] != ')':
        compileExpression()
        if currentToken[1] == ',':
            eat(',')
            continue
    writeXML('</expressionList>\n')

def compileTerm():
    writeXML('<term>\n')
    # if it is an int or str constant, we ouptut and advance token
    if currentToken[0] == 'integerConstant' or currentToken[0] == 'stringConstant':
        output = '<'+currentToken[0]+'> '+currentToken[1]+' </'+currentToken[0]+'>\n'
        writeXML(output)
        writeXML('</term>\n')
        advanceToken()

    # if it is a keyword constant, we ouptut and advance token
    elif currentToken[1] in keywordConstants:
        output = '<'+currentToken[0]+'> '+currentToken[1]+' </'+currentToken[0]+'>\n'
        writeXML(output)
        writeXML('</term>\n')
        advanceToken()

    # expression in parantheses eg sum = (2+3)
    elif currentToken[1] == '(':
        eat('(')
        compileExpression()
        eat(')')
        writeXML('</term>\n')

    # but if it is an identifier, the we need to check next token
    elif currentToken[0] == 'identifier':
        first = currentToken
        # get the next token, current token refers to it
        advanceToken()

        # array reference
        if currentToken[1] == '[':
            output = '<'+first[0]+'> '+first[1]+' </'+first[0]+'>\n'
            writeXML(output)
            eat('[')
            compileExpression()
            eat(']')
            writeXML('</term>\n')
        
        # subroutine call eg Main.output()
        elif currentToken[1] == '.':
            output = '<'+first[0]+'> '+first[1]+' </'+first[0]+'>\n'
            writeXML(output)
            eat('.')
            output = '<'+currentToken[0]+'> '+currentToken[1]+' </'+currentToken[0]+'>\n'
            writeXML(output)
            advanceToken()
            eat('(')
            compileExpressionList()
            eat(')')
            writeXML('</term>\n')

        # subroutine call eg cry()
        elif currentToken[1] == '(':
            output = '<'+first[0]+'> '+first[1]+' </'+first[0]+'>\n'
            writeXML(output)
            eat('(')
            compileExpressionList()
            eat(')')
            writeXML('</term>\n')

        # else a usual varname
        else:
            output = '<'+first[0]+'> '+first[1]+' </'+first[0]+'>\n'
            writeXML(output)
            writeXML('</term>\n')

    # if -7 or ~term
    elif currentToken[1] in unary_op:
        eat(currentToken[1])
        compileTerm()
        writeXML('</term>\n')

    else:
        exitCompilation()

def eat(currentTokenCompare):
    
    if currentToken[1] == currentTokenCompare:
        if currentToken[1] == '>':
            output = '<'+currentToken[0]+'> '+'&gt;'+' </'+currentToken[0]+'>\n'
            writeXML(output)
            advanceToken()
        elif currentToken[1] == '<':
            output = '<'+currentToken[0]+'> '+'&lt;'+' </'+currentToken[0]+'>\n'
            writeXML(output)
            advanceToken()
        elif currentToken[1] == '&':
            output = '<'+currentToken[0]+'>' + '&amp;' +'</'+currentToken[0]+'>\n'
            writeXML(output)
            advanceToken()
        else:
            output = '<'+currentToken[0]+'> '+currentToken[1]+' </'+currentToken[0]+'>\n'
            writeXML(output)
            advanceToken()
        
    else:
        exitCompilation()

def advanceToken():
    global tokenIndex
    global currentToken
    tokenIndex += 1
    if tokenIndex < len(analysed_tokens):
        currentToken = analysed_tokens[tokenIndex]

def exitCompilation():
    print(currentToken)
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

def writeXML(string):
    with open(output_file, 'a') as xmlfile:
        xmlfile.write(string)


def openDirForAnalysis(directory):
    directory = Path(directory)
    for jackFile in os.listdir(directory):
        if jackFile.endswith('.jack'):
            global output_file
            output_file = jackFile.split('.')[0]+'.xml'

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
    output_file = jackFile.split('.')[0]+'.xml'
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