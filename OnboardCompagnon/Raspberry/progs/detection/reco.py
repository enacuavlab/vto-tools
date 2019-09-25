#!/usr/bin/python3

#--------------------------------------------------------------------------------------------- 
# https://github.com/tensorflow/models/tree/master/research/object_detection

#Get Prototext
#https://github.com/chuanqi305/MobileNet-SSD/blob/master/voc/MobileNetSSD_deploy.prototxt

#Get Caffemodel
#https://github.com/C-Aniruddh/realtime_object_recognition/blob/master/MobileNetSSD_deploy.caffemodel

# Ouvrir un terminal et executer la commande ci dessous
# python3 reconnaissance_objets.py --prototxt MobileNetSSD_deploy.prototxt --model MobileNetSSD_deploy.caffemodel

#--------------------------------------------------------------------------------------------- 
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import time
import cv2
 
 
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
	help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
	help="minimum probability to filter weak detections")
args = vars(ap.parse_args())
 
# initialiser la liste des objets entrainés par MobileNet SSD 
# création du contour de détection avec une couleur attribuée au hasard pour chaque objet
CLASSES = ["arriere-plan", "avion", "velo", "oiseau", "bateau",
	"bouteille", "autobus", "voiture", "chat", "chaise", "vache", "table",
	"chien", "cheval", "moto", "personne", "plante en pot", "mouton",
	"sofa", "train", "moniteur"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
 
print("...chargement du modèle...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
 
print("...démarrage de la Picamera et mise au point...")
vs = VideoStream(usePiCamera=True, resolution=(1600, 1200)).start()
#vs = VideoStream(0).start() For USB camera

print("...atttente de la mise au point...")
time.sleep(2.0)

print("...demarrage du FPS...")
fps = FPS().start()

print("...demarage boucle de detection...")
while True:

  print("...lecture de la camera...")
  frame = vs.read()
  
  print("...redimensionnement de l'image...")
  #frame = imutils.resize(frame, width=800, interpolation = cv2.INTER_CUBIC)

  (h, w) = frame.shape[:2]
  r = 500 / float(w)
  dim = (800, int(h * r))
  frame = cv2.resize(frame, dim, cv2.INTER_AREA)

  print("...out...")
 
  print("...récupération des dimensions et transformation en collection d'images...")
  (h, w) = frame.shape[:2]
  blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),0.007843, (300, 300), 127.5)
 
  print("... determiner la détection et la prédiction....")
  net.setInput(blob)
  detections = net.forward()
 
  print("...boucle de détection...") 
  for i in np.arange(0, detections.shape[2]):

    # calcul de la probabilité de l'objet détecté en fonction de la prédiction
    confidence = detections[0, 0, i, 2]
		
    # supprimer les détections faibles inférieures à la probabilité minimale
    if confidence > args["confidence"]:

      # extraire l'index du type d'objet détecté
      # calcul des coordonnées de la fenêtre de détection 
      idx = int(detections[0, 0, i, 1])
      box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
      (startX, startY, endX, endY) = box.astype("int")
 
      # creation du contour autour de l'objet détecté
      # insertion de la prédiction de l'objet détecté 
      label = "{}: {:.2f}%".format(CLASSES[idx],confidence * 100)
      cv2.rectangle(frame, (startX, startY), (endX, endY),COLORS[idx], 2)
      y = startY - 15 if startY - 15 > 15 else startY + 15
      cv2.putText(frame, label, (startX, y),cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

      # enregistrement de l'image détectée 
      cv2.imwrite("detection.png", frame)

      key = cv2.waitKey(1) & 0xFF
      if key == ord("q"):
        break
 
      fps.update()
 
fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
 
cv2.destroyAllWindows()
vs.stop()
