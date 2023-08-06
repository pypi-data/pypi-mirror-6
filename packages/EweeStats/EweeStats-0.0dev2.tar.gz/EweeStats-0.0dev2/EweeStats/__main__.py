#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  EweeStats.py
#  
#  Copyright 2014 Gabriel Hondet <gabrielhondet@gmail.com>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#

import threading
import Queue
import time
import os
import sys
import pygal
from pyfirmata import Arduino, util
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

# Variable globale définissant le nombre de capteurs branchés en analogique
analogSensors = 2

class AnalogGraphThreads():
    """
        Classe destinée aux threads de lecture des valeurs analogiques
        et de création du graph
    """

    def __init__(self):
        """
            Constructeur de la classe : va créer transmit_is_ready
            pour contrôler l'état des threads et créer une queue d'un
            élément
        """

        self.transmit_is_ready = True
        self.my_queue = Queue.Queue(maxsize=1)
        self.stop = False

    def threadAnalogData(self):
        """
            Ce thread relève les valeurs analogiques, les stocke dans
            des fichiers et attent que le thread 2 soit prêt pour
            commencer le graph
        """
        # Init affichage lcd
        lcd = Adafruit_CharLCDPlate()
        lcd.clear()

        # Nombre de capteurs analogiques :
        global analogSensors
        # Booléen indiquant l'état de l'initialisation de l'instant 0 pour l'horodatage
        timestampInitDone = False
        # Liste des valeurs
        valueList = []                  # On crée une liste vide
        for i in range(analogSensors):
            valueList.append(0.000)     # On rajoute autant de 0 flottants qu'il y a de capteurs

        # Init Arduino et iterateur
        lcd.message("Connection de \nl'Arduino ...")
        board = Arduino('/dev/ttyACM0')
        lcd.clear()
        print('Arduino connected')
        lcd.message("Arduino connecte !")
        # Création itérateur
        iter8 = util.Iterator(board)
        iter8.start()

        #################################
        #   CREATION DES FICHIERS   #
        #################################


        # Création d'un dossier pour les fichiers nommé data dans le répertoire courant
        currentDir  = os.getcwd()   # Chemin du dossier courant
        outDir      = "data"    # dossier contenant les fichiers
        newpath     = os.path.join(currentDir, outDir) # Creation du chemin
        # Si le dossier n'existe pas, le créer
        if not os.path.exists(newpath): os.makedirs(newpath)


        # Ouvre un fichier par pin analog en écriture nommé data_X 
        fileList = []       # liste contenant tous les fichiers
        for i in range(analogSensors):
            # Création d'un nom de fichier avec indexe i (data_0, data_1 ...)
            filename = "data_%s"%str(i)
            # définition du chemin vers lequel les fichiers seront enregistrés
            filepath = os.path.join(newpath, filename)
            file = open(filepath, 'w+') # création de chaque fichier
            fileList.append(file)   # On ajoute le fichier à la liste

        filepath = os.path.join(newpath, "timestamp")   # refait le chemin
        timeFile = open(filepath, 'w+')                 # créé le fichier
        print(fileList)
        lcd.clear()
        lcd.message("fichiers ouvert")

        #################################

        # Commence l'écoute des ports nécessaires
        for i in range(analogSensors):
            board.analog[i].enable_reporting()


        # Wait for a valid value to avoid None
        start = time.time()
        while board.analog[0].read() is None:
                print "nothing after {0}".format(time.time() - start)

        print "first val after {0}".format(time.time() - start)
        lcd.clear()
        lcd.message("Debut des \nmesures")

        displayPin = 0  # Initialisation de la variable pour le choix des pins
        timeDisplay = 0 # Init variable pour le retardement de l'affichage

        ###### FIN INIT ########################################################

        while lcd.buttonPressed(lcd.SELECT) != 1: # Continue tant qu'on appuie pas sur SELECT

            # Choix du pin a afficher selection avec les boutons
            if lcd.buttonPressed(lcd.UP) == 1:      # si on appuie sur le bouton up, on affiche le pin A0
                print('--UP PRESSED--')
                displayPin = 0
            elif lcd.buttonPressed(lcd.DOWN) == 1:  # si on appuie sur le bouton down, on affiche le pin A1
                print('--DOWN PRESSED--')
                displayPin = 1


            #### INIT TIMESTAMP ####
            if timestampInitDone is False:      # Pour n'initialiser qu'une seule fois le timestamp
                timestampInit = time.time()
                timestampInitDone = True            # Booléen indiquant que timestampInit a été initialisé
            #### FIN INIT TIMESTAMP ####

            #### CREATION DU TIMESTAMP ####
            timestamp = time.time()             # Lecture du temps
            timestamp = timestamp - timestampInit   # Différence entre le temps initial et le temps de la prise
            timeFile.write(str(round(timestamp, 4)))              # écriture dans le fichier de temps
            timeFile.write('\n')

            #### TRAITEMENT DES DONNEES ####
            # Version tout en une boucle
            #for i, file in enumerate(fileList):
                # Lecture de la valeur analogique
                #value_a = board.analog[i].read()# Relève la mesure
                #print(value_a * 10)
                #file.write(str(timestamp)) # écrit le timestamp
                #file.write('\t')                # tabulation pour séparer timestamp et val
                #file.write(str(value_a))   # écrit les valeurs
                #file.write("\n")       # saut de ligne

            # Version en deux boucles : diminue le décalage de temps entre chaque lecture de données
            for i, file in enumerate(fileList):         # boucle lecture
                valueList[i] = board.analog[i].read()   # lecture et enregistrement dans la liste

            print(valueList)                            # affiche dans la console les valeurs
            for i, file in enumerate(fileList):         # boucle écriture
                file.write(str(valueList[i]))              # écriture valeur
                file.write('\n')

            #### GESTION DES THREADS ####
            # Regarde si le thread 2 est prêt
            if self.transmit_is_ready == True:
                self.my_queue.put(1)        # s'il est prêt, on met 1 dans la queue

            #### AFFICHAGE DES VALEURS SUR LCD ####
            timeLastDisplay = time.time() - timeDisplay     # Calcul du temps du dernier affichage
            if timeLastDisplay >= 0.25:                     # Si le temps excède les 250ms
                lcd.clear()
                lcd.message("Pot %s :\n"%(str(displayPin))) # Affiche le message
                lcd.message(valueList[displayPin] * 10)
                timeDisplay = time.time()                   # Enregistre le moment d'affichage

        #### EXTINCTION ####
        self.stop = True                    # On dit au thread 2 de s'arrêter
        lcd.message("Fermeture des \nlogs")
        for fi in fileList:
            fi.close()
        timeFile.close()
        lcd.clear()
        lcd.message("Extinction ...")
        time.sleep(1)
        lcd.clear()
        board.exit()


    def threadGraph(self):
        """
            Thread construisant le graph :
            lit les valeurs, les formate comme il faut, configure puis
            crée le graph
        """
        global analogSensors
        while(not self.stop):               # Tant que le thread 1 ne dit pas de s'arrêter on boucle
            # gestion du démarrage du thread : attend jusqu'à ce que la queue se remplisse
            self.my_queue.get(True)
            # Quand la queue est remplie, le thread passe en état occupé
            self.transmit_is_ready = False
            #### OUVERTURE DES FICHIERS ET CREATION DES LISTES ####
            # Fichier timestamp
            with open('data/timestamp', 'r') as t:               # Ouverture en lecture seule
                timestamp = [line.rstrip() for line in t]   # remplissage des listes en enlevant le '\n'
                # Fichier d0
            #with open('data/data_0', 'r') as d0:
            #    data_0 = [line.rstrip() for line in d0]        # voir au-dessus
            # Version générique
            dataList = []     # Création de la liste dataList contenant les listes de données de chaque fichier
            for i in range(analogSensors):                          # boucle pour ouvrir chaque fichier
                with open("data/data_%s"%str(i), 'r') as di:        # ouvre chaque fichier
                    dataList.append([line.rstrip() for line in di])   # lit le fichier
            # Formatage des listes
            timestamp = map(str, timestamp)                     # passe timestamp en string
            #for i, elt in enumerate(data_0):
            #    data_0[i] = float(elt)
            # Version générique
            for i, elt in enumerate(dataList):
                dataList[i] = map(float, elt)
            # Fermeture des fichiers
            t.close()
            #d0.close()
            for i in range(analogSensors):
                di.close


            linechart                   = pygal.Line()                      # définition du type de graphique
            linechart.x_label_rotation  = 20                                # rotation des graduations en abscisse
            linechart.show_dots         = False                             # cache les points
            linechart.human_readable    = True                              # affiche les valeurs plus clairement
            linechart.title             = 'Tension en fonction du temps'    # titre du graphique
            linechart.x_title           = 'Temps (s)'                       # Titre axe abscisse
            linechart.x_labels          = timestamp                         # graduation en x
            linechart.x_labels_major_count = 20                             # afficher 20 labels majeurs
            linechart.show_minor_x_labels = False                           # caches les labels mineurs
            #linechart.add('Pot 1', data_0)                                  # ordonnées des points
            # Version générique
            #for i in range(analogSensors):
            #    linechart.add("Pot %s"%str(i), data_i)
            for i, elt in enumerate(dataList):
                linechart.add('Pot %s'%str(i), elt)
            linechart.render_to_file('linechart_temp.svg')                  # écriture de l'image temporaire

            # Création de l'image définitive
            #os.remove('linechart.svg')                 # Inutile avec les systèmes UNIX =)
            os.rename('linechart_temp.svg', 'linechart.svg')

            # Tâche terminée, le thread 2 est prêt
            self.transmit_is_ready = True



    def startThreads(self):
        """
            Sert à lancer les threads : les crée puis les lance
        """
        # Création des threads
        self.at = threading.Thread(None, self.threadAnalogData, None)
        self.gt = threading.Thread(None, self.threadGraph, None)

        # Lancement des threads
        self.at.start()
        self.gt.start()

if __name__ == '__main__':
        data2Graph = AnalogGraphThreads()
        data2Graph.startThreads()
