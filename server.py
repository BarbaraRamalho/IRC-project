#********
#servidor
#********


import socket

#                                               INICIALIZACOES 

SERVER_PORT=12000 #porto onde se recebem os comandos "REGISTO <nome>", "RESPOSTA", "CONVIDAR <nome>" ou "SAIR" 

server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server.bind(('',12000))

addrs   = {} # dict: nome -> endereco. Ex: addrs["user"]=('127.0.0.1',17234)
clients = {} # dict: endereco -> nome. Ex: clients[('127.0.0.1',17234)]="user"
players = {} # dict: nome -> estado. Ex: lista["JogadorA"]=('ocupado')
convites = {} # dict: jogadorA -> jogadorB. Ex: convites["JogadorA"]="JogadorB"

simbolodic={}# nome-> simbolo X ou O

tabuleiro=([[11,12,13],[21,22,23],[31,32,33]])

trinco= 1

fim="gameon"


#                                              FUNCOES PRINCIPAIS

#Registo

def registo(name,addr):
  respond_msg = "Utilizador "+  name + " " + "REGISTADO" 
  if not name in addrs and not addr in clients:  # se o nome nao existe e o endereco nao esta a ser usado
    state="livre"
    addrs[name] = addr
    clients[addr] = name
    players[name] = state
    server.sendto(respond_msg.encode(),addr)  #informa o utilizador que ficou registado
  else:
    respond_msg = "ERRO: " + name + " " + "JA EXISTE"
    print(addr)
    server.sendto(respond_msg.encode(),addr) #informa o utilizador que o nome que escolheu ja existe


#Lista de jogadores

def mostra_lista():
  respond_msg = "LISTA" + " : " + str(players)
  for name in players: # por cada nome de utilizador
    state = players[name] # o estado e' o valor do dicionario com que tem como key "name" 
  server.sendto(respond_msg.encode(),addr)
  print(players) # imprime a listagem de jogadores registados


#Convites

def convite(name, quem_convidou):
  if name in addrs: #novamente, se estiver no dicionario o utilizador existe
    if players[quem_convidou]=="ocupado" or players[name]=="ocupado":
      respond_msg="ERRO: pelo menos um dos jogadores esta ocupado"
      addr = addrs[quem_convidou]
      server.sendto(respond_msg.encode(),addr)
    elif name in convites or quem_convidou in convites:
      respond_msg="ERRO: ha um convite pendente de resposta"
      addr = addrs[quem_convidou]
      server.sendto(respond_msg.encode(),addr)
    else:
      respond_msg = "CONVITE de " + quem_convidou + " para " + name + "\n"  
      addr = addrs[name]
      server.sendto(respond_msg.encode(),addr)
      # memorizar quem convidou quem
      convites[quem_convidou]= name
      convites[name]= quem_convidou
  else:
    respond_msg="ERRO: destinatario nao encontrado"
    addr = addrs[quem_convidou]
    server.sendto(respond_msg.encode(),addr)


def resposta_convite(answer,addr):
  if addr in clients: #se addr estiver no dicionario clients, o utilizador existe
    if clients[addr] in convites:
      destino= addrs[convites[clients[addr]]]
    else:
      respond_msg = "Ninguem o convidou!"
      server.sendto(respond_msg.encode(),addr) #quando um jogador aceita um convite sem ser convidado
      return
    if answer == "SIM":
      players[clients[addr]] = "ocupado"
      players[clients[destino]] = "ocupado"
      respond_msg = "RESPOSTA" + " " + answer + " PODE JOGAR!"
      server.sendto(respond_msg.encode(),destino)
      simbolodic[clients[addr]]= "X"
      simbolodic[clients[destino]]= "O"
    elif answer == "NAO":
      respond_msg = "RESPOSTA" + " " + answer + " CONVITE RECUSADO"
      server.sendto(respond_msg.encode(),destino)
    else:
      respond_error(addr)


#Jogo

def jogada(linha, coluna, addr):
  global trinco
  global fim

  respond_msg = "JOGADA " + linha + "," + coluna
  if addr in clients: #se addr estiver no dicionario clients, o utilizador existe
      
    # Verificar se a jogada e' valida, se e' a vez do jogador jogar, e se a posicao que escolhe esta' livre
    if (clients[addr] in convites) and (clients[addr] in simbolodic) and \
       (linha =='1' or linha =='2' or linha =='3') and \
       (coluna=='1' or coluna =='2' or coluna=='3') and \
       ((simbolodic[clients[addr]]=="X" and trinco==0) or (simbolodic[clients[addr]]=="O" and trinco==1)) and \
       tabuleiro[int(linha)-1][int(coluna)-1]!="O" and tabuleiro[int(linha)-1][int(coluna)-1]!="X":
       
      destino= addrs[convites[clients[addr]]]
      tabuleiro[int(linha)-1][int(coluna)-1]= simbolodic[clients[addr]] 
      trinco= (trinco+1)%2
      respond_msg = str(tabuleiro)
      server.sendto(respond_msg.encode(),destino)
      server.sendto(respond_msg.encode(),addr)
      if (fim()=="acabou"): 
        print("Acabou")


    else:
      respond_msg = "NAO PODE JOGAR"
      server.sendto(respond_msg.encode(),addr)
      return

  else:
    print("NUMERO ERRADO. TENTE OUTRA VEZ")
    respond_msg += "\n"
    server.sendto(respond_msg.encode(),destino)


def respond_error(addr):
  respond_msg = "INVALID MESSAGE\n"
  server.sendto(respond_msg.encode(),addr)

  
def fim():
  destino= addrs[convites[clients[addr]]]

  for jogador in simbolodic:
    #linhas
    respond_msg= "FIM DO JOGO: JOGADOR " +  jogador + " GANHOU"

    #ganhar por linha
    if ((tabuleiro[0][0]==tabuleiro[0][1]==tabuleiro[0][2]==simbolodic[jogador]) or \
    (tabuleiro[1][0]==tabuleiro[1][1]==tabuleiro[1][2]==simbolodic[jogador]) or \
    (tabuleiro[2][0]==tabuleiro[2][1]==tabuleiro[2][2]==simbolodic[jogador])):
      server.sendto(respond_msg.encode(),destino)
      server.sendto(respond_msg.encode(),addr)
      exit()

    #ganhar por coluna
    elif ((tabuleiro[0][0]==tabuleiro[1][0]==tabuleiro[2][0]==simbolodic[jogador]) or \
    (tabuleiro[0][1]==tabuleiro[1][1]==tabuleiro[2][1]==simbolodic[jogador]) or \
    (tabuleiro[0][2]==tabuleiro[1][2]==tabuleiro[2][2]==simbolodic[jogador])):
      server.sendto(respond_msg.encode(),destino)
      server.sendto(respond_msg.encode(),addr)
      exit()

    #ganhar por diagonal
    elif ((tabuleiro[0][0]==tabuleiro[1][1]==tabuleiro[2][2]==simbolodic[jogador]) or \
    (tabuleiro[0][2]==tabuleiro[1][1]==tabuleiro[2][0]==simbolodic[jogador])):
      server.sendto(respond_msg.encode(),destino)
      server.sendto(respond_msg.encode(),addr)
      exit()

    #empate
    elif (tabuleiro[0][0] and tabuleiro[0][1] and tabuleiro[0][2] and \
    tabuleiro[1][0] and tabuleiro[1][1] and tabuleiro[1][2] and \
    tabuleiro[2][0] and tabuleiro[2][1] and tabuleiro[2][2]) == ("X" or "O"):
      respond_msg = "FIM DO JOGO" + " EMPATE" 
      server.sendto(respond_msg.encode(),destino)
      server.sendto(respond_msg.encode(),addr)
      exit()

    else:
      fim="acabou"


#                                            CORPO PRINCIPAL

while True:
  (msg,addr) = server.recvfrom(1024)

  cmds = msg.decode().split()
  if(cmds[0]=="REGISTO"): # "REGISTO <nome>" - regista um cliente como <nome>
    registo(cmds[1],addr)

  elif(cmds[0]=="LISTA"): # "LISTA" - mostra lista de jogadores registados ate ao momento
    mostra_lista()

  elif(cmds[0]=="CONVIDAR"): # "CONVIDAR <nome>" - envia CONVITE para o cliente <nome>
    if addr in clients: # se o addr estiver no dicionario clients, o utilizador existe
      quem_convidou = clients[addr]
      convite(cmds[1], quem_convidou)
    else:
      print("Cliente nao encontrado")

  elif(cmds[0]=="RESPOSTA"): # "RESPOSTA" - responde SIM ou NAO
    resposta_convite(cmds[1],addr)

  elif(cmds[0]=="JOGADA"):
    if addr in clients: # se o addr estiver no dicionario clients, o utilizador existe
      jogada(cmds[1], cmds[2],addr)

  elif(cmds[0]=="SAIR"): # "SAIR" - mata o servidor

    break
  else:
    respond_error(addr)

server.close()
