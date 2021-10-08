import sys
# FUNÇÕES DE VALIDAÇÃO E TRATAMENTO #################################

def rtrnType(op): #Retorna o tipo da instrução ou um erro
    if op in ['add', 'sub', 'and', 'or', 'xor', 'slt', 'jr']:
        return 'r'
    elif op in ['addi', 'beq', 'bne', 'lw', 'sw']:
        return'i'    
    elif op in ['j', 'jal']:
        return 'j'
    else:
        error(0,op)

def error(errorCode,var): #Recebe um código de erro e a variável incorreta, retorna o erro por escrito e finaliza o programa
    Error = ['Operação indefinida: ', 'Registrador indefinido: ','Valor não numérico na instrução addi: ', 'É esperado um registrador nesta posição. Valor incorreto: ',
    'Bloco não encontrado.', 'Quantidade de parâmetros maior que esperado.', 'A constante $zero não pode receber valores.', 'Um registrador não é esperado nesta posição'
    ]
    print ('\a')
    if var != 0:
        print("Erro! {}'{}'\nPressione ENTER para finalizar a execução..." .format(Error[errorCode],var))
    else:
         print("Erro! {}\nPressione ENTER para finalizar a execução..." .format(Error[errorCode]))
    input()
    exit(0)

def isRegister(reg): #Retorna True para um registrador corretamente inserido, ou um erro para incorretos 
    if reg in [
        '$zero', '$at', '$v0', '$v1', '$a0', '$a1', '$a2', '$a3',
        '$t0', '$t1', '$t2', '$t3', '$t4', '$t5', '$t6', '$t7',
        '$s0', '$s1', '$s2', '$s3', '$s4', '$s5', '$s6', '$s7',
        '$t8', '$t9', '$k0', '$k1', '$gp', '$sp', '$fp', '$ra' ]:
        return True
    elif reg.isnumeric():
        error(3,reg)
    else:
        error(1,reg)
    
def removeComments(line): #Remove comentarios na linha em analise na função mount32
    local = line.find('#')
    line = line[:local]
    return line

def removeNameFunctions(line): #Remove blocos da linha em analise na função mount32
    local = line.find(':')
    line = line[local+1:]
    return line

# BANCOS DE DADOS #########################################

def dataBank(value): #Banco de dados para valore binários de instruções e registradores
    dbRegister = { #REGISTRADORES 5 bits
        '$zero' : '00000',
        '$at' : '00001',
        '$v0' : '00010',
        '$v1' : '00011',
        '$a0' : '00100',
        '$a1' : '00101',
        '$a2' : '00110',
        '$a3' : '00111',
        '$t0' : '01000',
        '$t1' : '01001',
        '$t2' : '01010',
        '$t3' : '01011',
        '$t4' : '01100',
        '$t5' : '01101',
        '$t6' : '01110',
        '$t7' : '01111',
        '$s0' : '10000',
        '$s1' : '10001',
        '$s2' : '10010', 
        '$s3' : '10011',
        '$s4' : '10100',
        '$s5' : '10101',
        '$s6' : '10110',
        '$s7' : '10111',
        '$t8' : '11000',
        '$t9' : '11001',
        '$k0' : '11010',
        '$k1' : '11011',
        '$gp' : '11100',
        '$sp' : '11101',
        '$fp' : '11110',
        '$ra' : '11111'}

    dbOp = { #OPCODES 6 bits
        'addi' : '001000',
        'beq' : '000100',
        'bne' : '000101',
        'j' : '000010',
        'jal': '000011',
        'lw' : '100011',
        'sw' : '101011'}

    if value in dbRegister:
        return dbRegister[value]
    elif rtrnType(value) == 'r':
        return '000000'
    elif value in dbOp:
        return dbOp[value]
    else:
        error(7,0)
def Rspecial_dataBank(instruction): #Para SHAMT e FUNCT do tipo R pré definidos -> jr exceção, mas ainda aplicável

    db_typeR = {
        'add' : '00000100000', 
        'sub' : '00000100010', 
        'and' : '00000100100', 
        'or' : '00000100101', 
        'xor' : '00000100110', 
        'slt' : '00000101010',
        'jr' : '000000000000000001000'
    }
    if rtrnType(instruction) == 'r':
        return db_typeR[instruction]

def binConverter(number): #Conversão de numeros negativos e positivos. negativos irão ao padrão complemento de 2
    if number < 0:
        number += 65536
    return number

# MONTAGEM DAS PALAVRAS #####################################

def mount32(line, listLines): #Função principal que atribui os respectivos valores binarios às operações e registradores formando uma palavra de 32 bits
    #Tratamento da string de entrada, remoção de virgulas, parenteses, e transformando a string de entrada em um vetor de strings, exemplo: ['add', '$t0', '$t1', '$t2']
    line = removeNameFunctions(line)
    line = removeComments(line)
    line = line.replace(',',' ')
    line = line.replace('(',' ')
    line = line.replace(')','')
    line = line.split()
    tam = len(line)
    
    if tam > 4:
        error(5,0)
    try:
        if rtrnType(line[0]) == 'r': #1 verifica a operação -TIPO R
            instruction = line[0] #2 salva a operação
            if line[0] != 'jr' and tam == 4: #3 excessão
                if isRegister(line[1]): #4 verifica o registrador
                    rd = line[1]   #5 salva o registrador
                    if rd == '$zero':
                        error(6,0)
                    if isRegister(line[2]):
                        rs = line[2]
                    if isRegister(line[3]):
                        rt = line[3]
                    word32 = dataBank(instruction) + dataBank(rs) + dataBank(rt) + dataBank(rd) + Rspecial_dataBank(instruction) #Montagem da instrução tipo R (que não seja jr)
                    
            elif line[0] == 'jr':
                if tam > 2:
                    error(5,0)
                if tam == 2:
                    isRegister(line[1])
                    rs = line[1]
                    word32 = dataBank(instruction) + dataBank(rs) + Rspecial_dataBank(instruction) #Montagem da instrução jr
                elif tam == 1:
                    rs = '$ra'
                    word32 = dataBank(instruction) + dataBank(rs) + Rspecial_dataBank(instruction) #Montagem da instrução jr
                else:
                    error(5,0)
                    
        elif rtrnType(line[0]) == 'i': #Tipo I
            instruction = line[0]
            if instruction == 'addi': #addi
                if isRegister(line[1]):
                    rt = line[1]
                if isRegister(line[2]):
                    rs = line[2]
                if line[3].isnumeric() or '-' in line[3]:
                    imm = '{0:016b}'.format(binConverter(int(line[3])))
                else:
                    error(2,line[3])
                word32 = dataBank(instruction) + dataBank(rs) + dataBank(rt) + imm

            elif instruction in ['beq', 'bne']: #beq e bne
                if isRegister(line[1]):
                    rs = line[1]
                if isRegister(line[2]):
                    rt = line[2]
                if sweepUp(line[3], listLines) != -1:
                    offset = '{0:016b}'.format(sweepUp(line[3], listLines))
                else:
                    error(4,0)
                word32 = dataBank(instruction) + dataBank(rs) + dataBank(rt) + offset

            elif instruction in ['sw','lw']: #sw e lw
                if isRegister(line[1]):
                    rt = line[1]
                if line[2].isnumeric():
                    offset = '{0:016b}'.format(int(line[2]))
                else:
                    error(4,0)  
                if isRegister(line[3]):
                    rs = line[3]
                word32 = dataBank(instruction) + dataBank(rs) + dataBank(rt) + offset

        elif rtrnType(line[0]) == 'j':  #tipo J
            if tam != 2:
                error(5,0)
            instruction = line[0]
            if sweepUp(line[1], listLines) != -1:
                offset = '{0:026b}'.format(sweepUp(line[1], listLines))
            elif line[1].isnumeric():
                print(line[1])
                offset = '{0:026b}'.format(int(line[1]))
            elif line[1][0] == '$':
                error(7,0)
            else:
                error(4,0)
            word32 = dataBank(instruction) + offset
        return littleEndian(word32) #Retorno da função mount32 após a conversão da palavra de 32 bits em little-endian
    except:
        return ''

def littleEndian(word32): #Função littleEndian() para dividir a palavra de 32 bits gerada pela função mount32 em 4 linhas de 8 bits
    littleEnd = ''
    for i in range(1,5):
        for j in range(32-8*i,(32-8*(i-1))):
            littleEnd += word32[j]
        littleEnd += '\n'
    return littleEnd

# LEITURA E ANALISE DE ARQUIVO DE ENTRADA #######################

def sweepUp(name, listLines): #Função sweepUp() para varrer código em busca da linha do bloco exigido (pc = pc+offset*4)
    ctd = 0
    for i in listLines:
        if (name+':') in i:
            return ctd*4
        elif ctd == len(listLines):
            return -1
        ctd+=1

# MAIN ################################

listArgs = []
for param in sys.argv:
    listArgs.append(param) #Captação dos argumentos na linha de comando
listArgs.pop(0)
f = open(listArgs[0], "r") #Abertura do arquivo de entrada
listLines = f.readlines() #Separação linha por linha do arquivo de entrada
f.close() #Fechamento do arquivo de entrada
for i in range(len(listLines)): #Procedimento para unificar blocos às linhas ( essencial para a função sweepUp ) 
    if i+1 < len(listLines) and removeNameFunctions(listLines[i].replace(" ", "")) == "\n":
        listLines[i] = listLines[i].replace(" ", "")
        listLines[i] = listLines[i].replace("\n", " ")
        listLines[i+1] = listLines[i] + listLines[i+1]
        listLines.pop(i)
if len(listArgs) == 2 and '.dat' in listArgs[1]: #Vericação da existencia de um segundo argumento na linha de comando
    f = open(listArgs[1], "w")
else:
    f = open("memoria.dat", "w")
for i in listLines:
    f.write(mount32(i + ' ', listLines))  #Inserção das linhas em Little-endian no arquivo de saida
f.close() #Fechamento do arquivo de saida
