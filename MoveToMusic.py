from rtmidi import (API_UNIX_JACK, MidiOut)
import time
import imutils
import numpy as np
import cv2
import copy

midiout = MidiOut()
available_ports = midiout.get_ports()
print(available_ports)
midiout.open_port(1)

min_area = 500
resolutionX = 640
resolutionY = 480
cap = cv2.VideoCapture(0)
time.sleep(0.5)

firstFrame = None

while True:

    (ret, frame) = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if firstFrame is None:
        firstFrame = gray
        continue

    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    (_a, cnts, _b) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for c in cnts:
        if cv2.contourArea(c) < min_area:
            continue

        (x, y, w, h) = cv2.boundingRect(c)
        frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)

        #frame = cv2.rectangle(frame, (0, 0), (resolutionX, resolutionY), (0, 255, 0), 3)

        axialX = (x/2) + w
        axialY = (y/2) + h
        MidiX = (axialX* 127) / resolutionX
        MidiY = (axialY* 127) / resolutionY
        noteonX = [0x90, 60, MidiX]
        noteonY = [0x90, 62, MidiY]
        midiout.send_message(noteonX)
        midiout.send_message(noteonY)
        print(noteonX, ",", noteonY)

    #cv2.imshow('Frame Delta', frameDelta)
    #cv2.imshow('Threshold', thresh)
    cv2.imshow('Real', frame)

    key = cv2.waitKey(33)
    if key == 27:
        for i in range(0, 127):
            noteOff = [0x80, i, 0]
            midiout.send_message(noteOff)
        break

del midiout
cap.release()
cv2.destroyAllWindows()