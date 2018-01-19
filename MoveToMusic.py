#importation des libs

from rtmidi import (API_UNIX_JACK, MidiOut)
from statistics import mean
import time
import imutils
import numpy as np
import cv2
import copy

#Création de variables Midi et CV2

midiout = MidiOut()
available_ports = midiout.get_ports()
print(available_ports)
midiout.open_port(1)

min_area = 300
resolutionX = 640
resolutionY = 480
cap = cv2.VideoCapture(0)
time.sleep(0.5)
listX=[]
listÝ=[]
#Mise en place de la première Frame
firstFrame = None

#Boucle d'affichage et de calcul
while True:
    
    #lecture de la caméra
    (ret, frame) = cap.read()
    #calcul sur l'image (frame)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    
    #vérification de la création de la première image
    if firstFrame is None:
        firstFrame = gray
        continue
    #*Suite* calcul sur l'image
    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 50, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    (_a, cnts, _b) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    #boucle de détéction des contours
    for c in cnts:
        if cv2.contourArea(c) < min_area:
            continue
        
        #création des carrés sur les mouvements
        (x, y, w, h) = cv2.boundingRect(c)
        frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)

        #calcul pour la création des variables midi 
        axialX = (w/2) + x
        axialY = (h/2) + y
        MidiX = (axialX * 127) / resolutionX
        MidiY = (axialY * 127) / resolutionY
        MidiX = int(MidiX)
        MidiY = int(MidiY)
        listX.append(MidiX)
        listY.append(MidiY)
        if len(listX) == 50:
            #calcul de la moyenne des valeurs
            MidiXmean(listX)
            MidiY=mean(listY)
            #création variable midi
            noteonX = [0xb0, 0x60, MidiX]
            noteonY = [0x90, 0x61, MidiY]
            
            #envoi message midi
            midiout.send_message(noteonX)
            midiout.send_message(noteonY)
            print(noteonX, ",", noteonY)
            listX=[]
            listY=[]
    
    #affichage de la caméra
    #cv2.imshow('Frame Delta', frameDelta)
    #cv2.imshow('Threshold', thresh)
    cv2.imshow('Real', frame)
    
    #stop programme
    key = cv2.waitKey(33)
    if key == 27:
        #for i in range(0, 127):
            #noteOff = [0x0b, i, 0]
            #midiout.send_message(noteOff)
        break

#arrêt de l'ensemble des paramètres
del midiout
cap.release()
cv2.destroyAllWindows()