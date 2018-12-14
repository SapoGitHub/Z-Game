import discord                                                      #Biblioteca para trabalhar com o discord
import gspread                                                      #Biblioteca para manipular o Google Planilhas
from oauth2client.service_account import ServiceAccountCredentials  #Biblioteca para conectarmos ao Google Dcos
import datetime                                                     #Biblioteca para lidar com a hora

#Informções de login do Google Planilha
escopo = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credenciais = ServiceAccountCredentials.from_json_keyfile_name('chave.json', escopo)

planilha = gspread.authorize(credenciais)           #Conexão com o Google
folha = planilha.open("Último.Jogo").sheet1

cliente = discord.Client()                                  #Conexão com o Discord

#Detecta o evento de quando o Bot esta pronto
@cliente.event
async def on_ready():
    print('Logado como ' + str(cliente.user.name)+".")

#Detecta o evento de quando alguém mudou o status
@cliente.event
async def on_member_update(antes,depois):
    if (antes.game != depois.game):                         #Se o que mudou foi o que estava jogando
        planilha = gspread.authorize(credenciais)           #Conexão com o Google
        folha = planilha.open("Último.Jogo").sheet1
        nome=str(antes)                                     #Pegamos o nome do membro
        for x in range(1,31,3):                              #O localizamos na planilha
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

#Rodamos nosso bot
cliente.run("NTIyOTczNjczNzEyMjU0OTg2.DvSyrA.9dTHTK_5xFjf2_j5-GL1vV28EIc")










##    print('Logado como ' + str(cliente.user.name) + ", com ID: "+str(cliente.user.id)+".")
##    print('Com o usuário '+str(cliente.user)+' nos servidores '+str(cliente.servers)+".")
##    print('Os usuários deste servidor são:')
##    for membro in cliente.get_all_members():
##        print(membro)
##    print('------')

