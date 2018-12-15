import discord                                                      #Biblioteca para trabalhar com o discord
import gspread                                                      #Biblioteca para manipular o Google Planilhas
from oauth2client.service_account import ServiceAccountCredentials  #Biblioteca para conectarmos ao Google Dcos
import datetime                                                     #Biblioteca para lidar com a hora
from discord.ext import commands                                    #Comandos pro discord

#CONFIGURAÇÃO-------------------------------------------------------------------------------------------------------------

#Informções de login do Google Planilha
escopo = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credenciais = ServiceAccountCredentials.from_json_keyfile_name('chave.json', escopo)

cliente = discord.Client()                                  #Conexão com o Discord

#EVENTOS------------------------------------------------------------------------------------------------------------------

#Detecta o evento de quando o Bot esta pronto
@cliente.event
async def on_ready():
    print('Logado como ' + str(cliente.user.name)+".")

##########################################################################################################################

#Detecta o evento de quando alguém mudou o status
@cliente.event
async def on_member_update(antes,depois):
    if (antes.game != depois.game):                         #Se o que mudou foi o que estava jogando
        planilha = gspread.authorize(credenciais)           #Conexão com o Google
        folha = planilha.open("Último.Jogo").sheet1
        nome=str(antes)                                     #Pegamos o nome do membro
        for x in range(1,26,3):                              #O localizamos na planilha
            if(nome== folha.cell(1,x).value):
                coluna=x                                    #A coluna do usuário em questão
                break
        linha=folha.cell(1,coluna+1).value                 #A próxima linha que deve ser escrita
        
        atual=datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S') #Hora Atual
        
        print("O usuario "+nome+" estava jogando "+str(antes.game)+" e agora está jogando "+str(depois.game)+".")
        
        if (antes.game==None and depois.game!=None):                            #Se começou a jogar
            folha.update_cell(1, coluna+2, atual)                               #Guardamos o horário

        elif (antes.game!=None and depois.game!=None):                          #Se apenas trocou de jogo
            
            #Primeiro precisamos guardar o jogo anterior
            folha.update_cell(int(linha), coluna, str(antes.game))                  #Guardamos o jogo
            inicio=folha.cell(1,coluna+2).value                                     #Quando tinha iniciado
            folha.update_cell(int(linha), coluna+1, inicio)                         #Guardamos quando iniciou o jogo
            folha.update_cell(int(linha), coluna+2, atual)                          #Guardamos quando fechou o jogo
            folha.update_cell(1, coluna+1, int(linha)+1)                            #Guardamos a próxima linha

            #E depois atualizar o novo
            folha.update_cell(1, coluna+2, atual)            #Guardamos o horário

        else:                                                                   #Se parou de jogar
            folha.update_cell(int(linha), coluna, str(antes.game))                  #Guardamos o jogo
            inicio=folha.cell(1,coluna+2).value                                     #Quando tinha iniciado
            folha.update_cell(int(linha), coluna+1, inicio)                         #Guardamos quando iniciou o jogo
            folha.update_cell(int(linha), coluna+2, atual)                          #Guardamos quando fechou o jogo
            folha.update_cell(1, coluna+1, int(linha)+1)                            #Guardamos a próxima linha

##########################################################################################################################

#Responder as mensagens
@cliente.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == cliente.user:
        return

    #Comando para checar a ultima semana
    if message.content.startswith('!7dias'):

        mensagem="Na última semana você jogou:\n"                                         #Mensagem que vamos enviar

        #Identificamos o autor
        planilha = gspread.authorize(credenciais)           #Conexão com o Google
        folha = planilha.open("Último.Jogo").get_worksheet(2)
        nome=str(message.author)                            #Pegamos o nome do membro
        for x in range(1,31,2):                             #O localizamos na planilha
            if(nome== folha.cell(1,x).value):
                coluna=x                                    #A coluna do usuário em questão
                break

        #Agora podemos percorrer linha a linha
        for linha in range(2,26):
            if ("Total geral"==folha.cell(linha,x).value):
                total=folha.cell(linha,x+1).value
                break
            else:
                mensagem=mensagem+ folha.cell(linha,x).value+" - "+folha.cell(linha,x+1).value+"\n"

        #Se o tempo total é nulo
        if(total==""):
            await cliente.send_message(message.channel, "Você não jogou nada!")
        else:
            mensagem=mensagem+"Tempo total: "+str(total)
            await cliente.send_message(message.channel, mensagem)
        return

    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    #Comando para checar o registro dos últimos 10 jogos
    if message.content.startswith('!ultimos'):

        mensagem="Seus ultimos jogos foram:\n"                                         #Mensagem que vamos enviar
        planilha = gspread.authorize(credenciais)           #Conexão com o Google

        #Primeiro pegamos o último jogo
        folha = planilha.open("Último.Jogo").sheet1
        nome=str(message.author)                            #Pegamos o nome do membro
        nome="ZéRomildo#1325"
        for x in range(1,26,3):                             #O localizamos na planilha
            if(nome== folha.cell(1,x).value):
                coluna=x                                    #A coluna do usuário em questão
                break
        ultima=int(folha.cell(1,x+1).value)-1

        if(ultima==1):
            await cliente.send_message(message.channel, "Você nunca jogou!")
            return

        #Agora precisamos identificar a coluna no segundo
        folha = planilha.open("Último.Jogo").get_worksheet(1)
        for x in range(1,26,3):                             #O localizamos na planilha
            if( nome == folha.cell(1,x).value):
                coluna=x                                    #A coluna do usuário em questão

        #E então pegamos os 10 últimos valores
        for n in range(ultima,ultima-10,-1):
            if(n==1):                                       #Se chegamos no item 1, saimos
                break
            else:
                mensagem=mensagem+folha.cell(n,coluna+2).value+" - "+folha.cell(n,coluna).value+": "+folha.cell(n,coluna+1).value+"\n"

        await cliente.send_message(message.channel, mensagem)
        return

#INICIALIZAÇÃO------------------------------------------------------------------------------------------------------------
#Rodamos nosso bot
cliente.run("NTIyOTczNjczNzEyMjU0OTg2.DvSyrA.9dTHTK_5xFjf2_j5-GL1vV28EIc")
