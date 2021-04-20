cAD_instructions = {'0':'0101010', '1':'0111111', '-1':'0111010', 'D':'0001100', 'A':'0110000', '!D':'0001101', '!A':'0110001', '-D':'0001111', '-A':'0110011', 'D+1':'0011111', 'A+1':'0110111', 'D-1':'0001110', 'A-1':'0110010', 'D+A':'0000010', 'D-A':'0010011', 'A-D':'0000111', 'D&A':'0000000', 'D|A':'0010101'}
cMD_instructions = {'M':'1110000', '!M':'1110001', '-M':'1110011', 'M+1':'1110111', 'M-1':'1110010', 'D+M':'1000010', 'D-M':'1010011', 'M-D':'1000111', 'D&M':'1000000', 'D|M':'1010101'}
jump_instructions = {'null':'000', 'JGT':'001', 'JEQ':'010', 'JGE':'011', 'JLT':'100', 'JNE':'101', 'JLE':'110', 'JMP':'111'}
dest_instructions = {'null':'000', 'M':'001', 'D':'010', 'MD':'011', 'A':'100', 'AM':'101', 'AD':'110', 'AMD':'111'}
symbol_table = {
    'R0':'0',
    'R1':'1',
    'R2':'2',
    'R3':'3',
    'R4':'4',
    'R5':'5',
    'R6':'6',
    'R7':'7',
    'R8':'8',
    'R9':'9',
    'R10':'10',
    'R11':'11',
    'R12':'12',
    'R13':'13',
    'R14':'14',
    'R15':'15',
    'SCREEN':'16384',
    'KBD':'24576',
    'SP':'0',
    'LCL':'1',
    'ARG':'2',
    'THIS':'3',
    'THAT':'4',
    'memory':'16'
}

# Function to parse instructions into components
def parser(instructionString):
    #instruction A
    if instructionString.startswith('@'):
        operand = instructionString[1:]
        decodeA(operand)
    # instruction C
    else:
        # Do this to ignore inline comments
        # Find space in line read
        space_index = instructionString.find(' ')
        # setup C instruction data structure
        c_instruction = {'dest':'null', 'comp':'', 'jump':'null'}
        # find index of '='
        index_of_equal_to = instructionString.find('=')
        if index_of_equal_to != -1:
            # if there is =, then the first data is a destination
            c_instruction['dest'] = str(instructionString[:index_of_equal_to])
        # find index of semi-colon
        index_of_semi_colon = instructionString.find(';')

        if index_of_semi_colon != -1:
            # if there is ; then second data is computation
            c_instruction['comp'] = str(instructionString[index_of_equal_to+1:index_of_semi_colon])
            if space_index != -1:
                c_instruction['jump'] = str(instructionString[index_of_semi_colon+1:space_index])
            else:
                c_instruction['jump'] = str(instructionString[index_of_semi_colon+1:])
        else:
            if space_index != -1:
                c_instruction['comp'] = str(instructionString[index_of_equal_to+1:space_index])
            else:
                c_instruction['comp'] = str(instructionString[index_of_equal_to+1:len(instructionString)])
        decodeC(c_instruction)


# Decoding A instructions
def decodeA(operand):
    print("instruction is ",'@'+operand)
    opcode = '0'
    # Check if operand is LABEL or Pre-defined
    # check if its a letter
    if operand[0].isdigit() == False:
        # check if its a label or predefined
        if operand in symbol_table.keys():
            operand = symbol_table[operand]
        else:
            # else it is a variable, use next available memory
            symbol_table[operand] = symbol_table['memory']
            operand = symbol_table[operand]
            symbol_table['memory'] = str(int(symbol_table['memory']) + 1)
    # compute the binary representation
    operand_int = int(operand)
    operand_bin_string = str(bin(operand_int).replace("0b", ""))
    padding = (15-len(operand_bin_string)) *'0'
    instruction = opcode + padding + operand_bin_string + '\n'
    with open('Max.hack', 'a') as machineFile:
        machineFile.write(instruction)


# Decode C instructions
def decodeC(c_instruction):
    print("Instruction is ", c_instruction)
    opcode = '111'
    jmp = jump_instructions[c_instruction['jump']]
    destination = dest_instructions[c_instruction['dest']]
    comp = c_instruction['comp']
    if comp.find('M') != -1:
        comp = cMD_instructions[c_instruction['comp']]
    else:
        comp = cAD_instructions[c_instruction['comp']]
    operand = comp + destination + jmp
    instruction = opcode+operand+'\n'
    with open('Max.hack', 'a') as machineFile:
        machineFile.write(instruction)

def firstPass():
    print('## FIRST PASS ##\n')
    line_number = 0
    with open('Max.asm') as assemblyFile:
        line = assemblyFile.readline()
        while(line !=''):
            line = line.strip()
            if line != '':
                if line[0] == '/':
                    line = assemblyFile.readline()
                    continue
                elif line[0] == '(':
                    ind = line.find(')')
                    label = line[1:ind]
                    print("Found label ", label)
                    if label not in symbol_table.keys():
                        symbol_table[label] = line_number
                        line = assemblyFile.readline()
                else:
                    line = assemblyFile.readline()
                    line_number = line_number + 1
            else:
                line = assemblyFile.readline()
                continue

def secondPass():
    print('## SECOND PASS ##\n')
    with open('Max.asm') as assemblyFile:
        line = assemblyFile.readline()
        while(line !=''):
            line = line.strip()
            if line != '':
                if line[0] == '/' or line[0] == '(':
                    line = assemblyFile.readline()
                    continue
                else:
                    parser(line)
                    line = assemblyFile.readline()
            else:
                line = assemblyFile.readline()
                continue

def main():
    print('## STARTING ASSEMBLER ##\n')
    firstPass()
    secondPass()
    print(symbol_table)
    print("DONE..OK\n")

if __name__ == "__main__":
    main()