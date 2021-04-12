# -- coding: utf8 --

#--------------Import des librairies------------#
import os
import sys
import hashlib
import datetime
import subprocess
import shutil
import time
import re
import os

from threading import Thread
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import *

from pathlib import Path
from  datetime import datetime
import sqlite3
from collections import defaultdict
import hashlib
# sous ubuntu: export DISPLAY=:0.0


#--------------------------------------------Fonctions primaires----------------------------------------------------#

#Afficher les logs ou non
afficherLog = 'true'
def log(string):
    if afficherLog == 'true':
        print(string)

# Pour cut les / de fin
def trim_slash(input_location): 
    if input_location[-1] == '/':
        input_location = input_location[:-1]
    return input_location

#On copie un élément grâce à shutil.copy
def copy(path_src, path_des):
    try:
        log("FROM: " + path_src + " To " + path_des)
        shutil.copy(path_src,path_des)
    except:
        log("File Exists")

#On parcours grace à os.walk et on fait appel à la fonction copy pour chaque élément
def each_file(path_src, path_des):
    #initialisation du filtre d'extension
    ext = ""
    #définition du filtre d'extension
    if filtre_extension.get() != "":
        ext = filtre_extension.get()
    for folderName, subfolders, filenames in os.walk(path_src):
        log('The current foler is ' + folderName)

        for subfolder in subfolders:
            log('SUBFOLDER OF ' + folderName + ': ' + subfolder)
            try:
                new_path = folderName.replace(path_src, path_des)
                os.mkdir(new_path+"\\"+subfolder)
            except:
                log("Folder Exists:" + subfolder)
        #itération sur chaque fichier du dossier
        for filename in filenames:
        #si aucune extension n'est précisée, on copie tous les fichiers
            if ext == "":
                print("-----------" + filename)
                new_path = folderName.replace(path_src,path_des)
                file = folderName + '\\' + filename
                copy(file, new_path)
            else:
                extension=filename.split('.')[-1]
                if extension == ext:
                    new_path = folderName.replace(path_src,path_des)
                    file = folderName + '\\' + filename
                    copy(file, new_path)


#Même parcours avec une verification de fichier
def each_file_with_list(listeFic, path_src, path_des):
    for folderName, subfolders, filenames in os.walk(path_src):
        log('The current foler is ' + folderName)
        for subfolder in subfolders:
            log('SUBFOLDER OF ' + folderName + ': ' + subfolder)
            try:
                new_path = folderName.replace(path_src, path_des)
                os.mkdir(new_path+"\\"+subfolder)
            except:
                log("Folder Exists:" + subfolder)
        for filename in filenames:
            tmpFil = '\\' + filename
            if tmpFil in listeFic:
                print("-----------" + filename)
                new_path = folderName.replace(path_src,path_des)
                file = folderName + '\\' + filename
                copy(file, new_path)


#-----------------------------Gestion des infos des fichiers et base de données------------------------#
#--------------------------------------------------------------------------------------------------------------------------------------

def bddCrea(loggg):
    con = sqlite3.connect("folders.db")
    print("==> Database bien ouverte")
    loggg.config(text="Database bien ouverte")
    con.execute("create table if not exists sourcefolder (keypath VARCHAR(50) PRIMARY KEY, path TEXT NOT NULL, hash TEXT UNIQUE NOT NULL)" )
    con.execute("create table if not exists targetfolder (keypath VARCHAR(50) PRIMARY KEY, path TEXT NOT NULL, hash TEXT UNIQUE NOT NULL)" )


def chunk_reader(fobj, chunk_size=1024):
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def get_hash(filename, first_chunk_only=False, hash=hashlib.sha1):
    """
        Génère le hash d'un fichier.
    """
    hashobj = hash()
    file_object = open(filename, 'rb')

    if first_chunk_only:
        hashobj.update(file_object.read(1024))
    else:
        for chunk in chunk_reader(file_object):
            hashobj.update(chunk)
    hashed = hashobj.digest()

    file_object.close()
    return hashed

class fileInfo():
    def __init__(self, fpath, path_src):
        self.path = fpath # chemin du fichier

        # chemin du fichier sans le dossier parent, pour faire la clé de comparaison entre les dossiers : 
        self.keypath = fpath.replace(path_src, '') 

        # hash du fichier, forcément propre au fichier 
        self.hash = get_hash(self.path)


    def __str__(self):
        return f"==> Object fileInfo: {self.path=}, {self.keypath=}, {self.hash=}"

def getInfoFiles(path_src):
    """
        Affiche toutes les infos nous interessant des fichiers dans un dossier indiqué par path_src.
        Utiliser en fonciton secondaire pour tester la récupération de ces infos mais inutile au programme.
    """
    print("----> The path_src is " + path_src)
    for folderName, subfolders, filenames in os.walk(path_src):
        print('The current foler is ' + folderName)

        for filename in filenames:
            # Gestion des bons slashs selon win ou linux
            if sys.platform.startswith('linux'):
                file = folderName + '/' + filename
            else:
                file = folderName + '\\' + filename

            fichier = fileInfo(file, path_src)
            print(fichier)


def clearDb():
    """
        Supprime le contenu des tables représentant les dossiers.
    """
    try:                
        with sqlite3.connect("folders.db") as con:
            cur = con.cursor()
            cur.execute("DELETE from sourcefolder;")
            cur.execute("DELETE from targetfolder;")

            con.commit()
    except:
        con.rollback()



def updateDb(path_src, path_tgt):
    """
        Supprime le contenu des bases de données puis insert tout les fichiers dedans avec les hashs.
    """

    ## Vide les bases de données pour faire place aux bonnes données 
    clearDb()
    
    ## Synchro de la BDD du dossier source
    log("----> The path_src is " + path_src)
    for folderName, subfolders, filenames in os.walk(path_src):
        log('The current foler is ' + folderName)

        for filename in filenames:
            
            # Gestion des bons slashs selon win ou linux
            if sys.platform.startswith('linux'):
                file = folderName + '/' + filename
            else:
                file = folderName + '\\' + filename

            fichier = fileInfo(file, path_src)
            print("Hash of ",file," : ", fichier.hash)

            try:                
                with sqlite3.connect("folders.db") as con:
                    cur = con.cursor()
                    cur.execute("INSERT into sourcefolder (keypath, path, hash) values (?,?,?)", (fichier.keypath, fichier.path, fichier.hash)) 

                    log("==> exe ok")
                    con.commit()
                    log("==> commit ok")

            except:
                con.rollback()
    
    ## Synchro de la BDD du dossier cible
    log("----> The path_tgt is " + path_tgt)
    for folderName, subfolders, filenames in os.walk(path_tgt):
        log('The current foler is ' + folderName)

        for filename in filenames:

            # Gestion des bons slashs selon win ou linux
            if sys.platform.startswith('linux'):
                file = folderName + '/' + filename
            else:
                file = folderName + '\\' + filename

            print("Hash of ",file," : ", get_hash(file))

            fichier = fileInfo(file, path_tgt)
            # log(fichier)

            print("Hash of ",file," : ", fichier.hash)

            try:                
                with sqlite3.connect("folders.db") as con:
                    cur = con.cursor()
                    cur.execute("INSERT into targetfolder (keypath, path, hash) values (?,?,?)", (fichier.keypath, fichier.path, fichier.hash)) 

                    log("==> exe ok")
                    con.commit()
                    log("==> commit ok")
            except:
                con.rollback()


def showDB():
    """
        Affiche les bases de données correspondant aux dossiers source et target
    """
    try:
        with sqlite3.connect("folders.db") as con:
            print("====== Source folder ======")
            cur = con.cursor()
            cur.execute("SELECT * FROM sourcefolder;")
            [print(row) for row in cur.fetchall()] 
            # print(cur.fetchall())

    except:
        con.rollback()

    try:
        with sqlite3.connect("folders.db") as con:
            print("====== Target folder ======")
            cur = con.cursor()
            cur.execute("SELECT * FROM targetfolder;")
            [print(row) for row in cur.fetchall()] 
            # print(cur.fetchall())

    except:
        con.rollback()
        

def getChangedFiles(keypath=True):
    """
        Retourne la liste des chemins des fichiers qui diffère entre les deux dossiers.
        Si keypath est True: retourne l'emplacement sous le dossier source sans le mentionner e.g.: /file1
        Si keypath est False: retourne le chemin complet du fichier e.g.: ./sourcefolder/file1
    """

    result = []

    index_value = 0
    if keypath:
        index_value = 1
    
    # Récupération des chemins des fichiers existant dans les deux dossiers mais différents.
    try:
        with sqlite3.connect("folders.db") as con:
            cur = con.cursor()
            cur.execute("SELECT s.path, s.keypath FROM sourcefolder as s JOIN targetfolder t on s.keypath=t.keypath WHERE s.hash != t.hash;")
    except:
        con.rollback()

    # Ajout de ces chemins à la liste de résultat
    for fi in cur.fetchall():
        result.append(fi[index_value])

    # Récupération des chemins des fichiers n'existant pas dans le dossier cible.
    try:
        with sqlite3.connect("folders.db") as con:
            cur = con.cursor()
            cur.execute("SELECT s.path, s.keypath FROM sourcefolder as s LEFT JOIN targetfolder t on s.keypath=t.keypath WHERE t.hash IS NULL;")
    except:
        con.rollback()

    # Ajout de ces chemins à la liste de résultat
    for fi in cur.fetchall():
        result.append(fi[index_value])
    
    return result

#-----------------------------------------------INTERFACE GRAPHIQUE---------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------------------------------------

# #Définition des variables
rep_source = ""
rep_dest = ""
synchro_active = False

#Cette fonction permet de sélectionner le dossier source pour synchronisation
def get_source():
    global rep_source
    global synchro_active

    synchro_active = False
    rep_source = filedialog.askdirectory(title="Répertoire de travail") 
    label_source.config(text=rep_source)
    return rep_source

#Cette fonction permet de sélectionner le dossier de destination pour synchronisation
def get_dest():
    global rep_dest
    #on stop la synchro lorsque l'on change de dossier
    global synchro_active
    synchro_active = False
    rep_dest = filedialog.askdirectory(title="Répertoire de travail") 
    label_dest.config(text=rep_dest)
    return rep_dest

#Cette fonction permet d'initier la boucle de synchronisation 
def synchro():
    source_exists = False
    dest_exists = False
    global synchro_active
    #On détermine si les dossiers existent
    if os.path.exists(rep_source):
        print("répertoire source : " + rep_source)
        source_exists = True
    else:
        print("répertoire source n'existe pas")

    if os.path.exists(rep_dest):
        print("répertoire source : " + rep_dest)
        dest_exists = True
    else:
        print("répertoire source n'existe pas")
    if source_exists == True and dest_exists == True:
        synchro_active = True
        mon_thread=Thread(target=synchro_boucle)   #définit la fonction a executer en arrière-plan
        mon_thread.start()    #lance la fonction, sans faire freezer la fenêtre
            
#Cette fonction permet d'arrêter la boucle de synchronisation
def stop_synchro():
    global synchro_active
    synchro_active = False

#Cette fonction permet d'appeler en boucle la fonction each_file(src,dest) qui effectue la synchronisation des fichier
def synchro_boucle():
    global synchro_active
    print(synchro_active)
    while synchro_active == True:
        try:
            each_file(rep_source,rep_dest)
            print("synchronisation effectuée")
        except:
            print("Echec de la synchronisation")
        time.sleep(1)

#Cette fonction permet d'arrêter la synchronisation lors de la fermeture de l'IHM
def exit_prg():
    stop_synchro()
    fenetre.destroy()

def bddun():
    updateDb(rep_source, rep_dest)
    print("---------------0---------")
    showDB()
    print("---------------1---------")
    print(getChangedFiles())
    
    lachaine = "Base de données mise à jour\n" + "Liste des fichiers altérés : \n"
    for elem in getChangedFiles():
        lachaine += elem
        lachaine += "\n"
    log_area.config(text=lachaine)

def bdddeux():
    print("----------yyyy------------")
    yo = ""
    for pat in getChangedFiles():
        yo += "Application changement au " + pat + "\n"
    log_area.config(text=yo)
    global rep_source
    global rep_dest
    each_file_with_list(getChangedFiles(), rep_source, rep_dest)



#----------Définition de la fenêtre----------#
fenetre = Tk()
fenetre.geometry('500x600')
fenetre.title("Interface de synchronisation de fichiers (Schametz, Braibant, Ghyselinck")
fenetre.configure(background ="light blue")

#---------Définition des boutons-------------#
bouton_src = Button(fenetre, text="Dossier source", fg="black", bg = "#DBD1D1", width = 20, command = get_source)
bouton_src.pack()
bouton_src.place(x = 200, rely=0.05, height=40, width=120)

bouton_dest = Button(fenetre, text="Dossier de destination", fg="black", bg = "#DBD1D1", width = 20, command = get_dest)
bouton_dest.pack()
bouton_dest.place(x = 200, rely=0.15, height=40, width=120)

bouton_synchro = Button(fenetre, text="Lancer la synchronisation continue", fg="black", bg = "#DBD1D1", width = 20, command = synchro)
bouton_synchro.place(relx = 0.05, rely=0.52, width=200)

bouton_stop_synchro = Button(fenetre, text="Arrêter la synchronisation continue", fg="black", bg = "#DBD1D1", width = 20, command = stop_synchro)
bouton_stop_synchro.place(relx = 0.55, rely=0.52, width=200)

#-------------------------------------------

bouton_bdd1 = Button(fenetre, text="Sauvegarder état dans la BDD", fg="black", bg = "#DBD1D1", width = 20, command = bddun)
bouton_bdd1.place(relx = 0.05, rely=0.60, width=200)

bouton_bdd2 = Button(fenetre, text="Maj fichiers avec la BDD", fg="black", bg = "#DBD1D1", width = 20, command = bdddeux)
bouton_bdd2.place(relx = 0.55, rely=0.60, width=200)

#-------------------------------------------

bouton_quit = Button(fenetre, text="Quitter", fg="black", bg = "#DBD1D1", width = 20, padx=3, pady=8, command = exit_prg)
bouton_quit.place(relx = 0.4, rely=0.70, width=100)

#---------Définition des labels------------#
#Extension a donner sans le "."
label_filtre = Label(fenetre, text="Extension (pdf,txt)")
label_filtre.place(relx = 0.19, rely=0.45, width=100)
filtre_extension = Entry(fenetre, bd =5)
filtre_extension.place(relx = 0.4, rely=0.44, width=100)

label_source= Label(fenetre, text="Répertoire source non sélectionné", fg="black", bg="white",borderwidth = 5, relief="groove")
label_source.config(font=("Arial Black",8))
label_source.place(x = 50, rely=0.25, height=40, width=400)

label_dest= Label(fenetre, text="Répertoire de destination non sélectionné", fg="black", bg="white",borderwidth = 5, relief="groove")
label_dest.config(font=("Arial Black",8))
label_dest.place(x = 50, rely=0.35, height=40, width=400)


log_area= Label(fenetre, text="", fg="black", bg="white",borderwidth = 5, relief="groove")
log_area.config(font=("Arial Black",8))
log_area.place(relx = 0, rely = 0.78, height=110, width=500)

fenetre.protocol("WM_DELETE_WINDOW", exit_prg)

bddCrea(log_area)

fenetre.mainloop()


 
