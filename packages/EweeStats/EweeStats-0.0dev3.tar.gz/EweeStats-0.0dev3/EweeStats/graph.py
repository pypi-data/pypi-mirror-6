#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  graph.py
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

import pygal
import os
import sys

def create_graph(analogSensors, dataDir):
    """
    Création du graphique à l'aide de pygal
    
    :param analogSensors: nombre de capteurs
    :type analogSensors: integer
    
    :param dataDir: dossier contenant les fichiers
    :type dataDir: string
    """

    #Ouverture des fichiers
    timePath = os.path.join(dataDir, 'timestamp')
    with open(timePath, 'r') as t:
        timestamp = [line.rstrip() for line in t]

    dataList = []
    for i in range(analogSensors):
        filePath = os.path.join(dataDir, "data_{i}".format(i = str(i)))
        with open(filePath, 'r') as di:
            dataList.append([line.rstrip() for line in di])

    # Formatage des listes
    timestamp = map(str, timestamp)
    
    for i, elt in enumerate(dataList):
        dataList[i] = map(float, elt)

    # Fermeture des fichiers
    t.close()
    for i in range(analogSensors):
        di.close


    linechart                   = pygal.Line()
    linechart.x_label_rotation  = 20
    linechart.show_dots         = False
    linechart.human_readable    = True
    linechart.title             = 'Tension en fonction du temps'
    linechart.x_title           = 'Temps (s)'
    linechart.x_labels          = timestamp
    linechart.x_labels_major_count = 20
    linechart.show_minor_x_labels = False
    for i, elt in enumerate(dataList):
        linechart.add('Pot %s'%str(i), elt)
    
    # Création d'une image temporaire et d'un définitive
    # car l'image est réeffacée avant chaque création du graph
    linechart.render_to_file('linechart_temp.svg')
    # image définitive
    os.rename('linechart_temp.svg', 'linechart.svg')
    
    return 0
