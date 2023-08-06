#!/usr/bin/python
#Autor: Wellington Viana Lobato Junior
#Espero que goste dessa pequena biblioteca
#Importar a biblioteca "os" para chamar funcoes do sistema operacional
import os
def trocar_wallpaper(local_imagem,nome_imagem):#Parametro de entrada deve ser uma string
  #Chama o comando gsettings, deve ser instalado no linux
  os.system("gsettings set org.gnome.desktop.background picture-uri file:///%s/%s.jpg"%(local_imagem,nome_imagem))


