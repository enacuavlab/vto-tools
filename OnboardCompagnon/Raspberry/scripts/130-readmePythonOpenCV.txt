sudo apt-get install python3-pip

time pip3 -vv install opencv-contrib-python-headless
=>
Installing collected packages: numpy, opencv-contrib-python-headless
...
real	62m28.831s
user	60m55.465s
sys	0m58.653s

sudo apt update

sudo apt install libhdf5-100
sudo apt install libcblas3
sudo apt install libatlas-base-dev
sudo apt install libjasper-dev


python3
import cv2
cv2.__version__
=>
'3.4.4'
quit()


---------------------------------------------------------------
pip3 install picamera

---------------------------------------------------------------
# Ouvrir un terminal et executer la commande ci dessous
# python3 reconnaissance_objets.py --prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel
 
# importer tout les packages requis
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2
 
 
# construction des arguments
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
 
# chargement des fichiers depuis le répertoire de stockage 
print(" ...chargement du modèle...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
 
# initialiser la caméra du pi, attendre 2s pour la mise au point ,
# initialiser le compteur FPS
print("...démarrage de la Picamera...")
vs = VideoStream(usePiCamera=True, resolution=(1600, 1200)).start()
time.sleep(2.0)
fps = FPS().start()
 
# boucle principale du flux vidéo
while True:
	# récupération du flux vidéo, redimension 
	# afin d'afficher au maximum 800 pixels 
	frame = vs.read()
	frame = imutils.resize(frame, width=800)
 
	# récupération des dimensions et transformation en collection d'images
	(h, w) = frame.shape[:2]
	blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
		0.007843, (300, 300), 127.5)
 
	# determiner la détection et la prédiction 
	net.setInput(blob)
	detections = net.forward()
 
	# boucle de détection 
	for i in np.arange(0, detections.shape[2]):
		# calcul de la probabilité de l'objet détecté 
		# en fonction de la prédiction
		confidence = detections[0, 0, i, 2]
		
		# supprimer les détections faibles 
		# inférieures à la probabilité minimale
		if confidence > args["confidence"]:
			# extraire l'index du type d'objet détecté
			# calcul des coordonnées de la fenêtre de détection 
			idx = int(detections[0, 0, i, 1])
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = box.astype("int")
 
			# creation du contour autour de l'objet détecté
			# insertion de la prédiction de l'objet détecté 
			label = "{}: {:.2f}%".format(CLASSES[idx],
				confidence * 100)
			cv2.rectangle(frame, (startX, startY), (endX, endY),
				COLORS[idx], 2)
			y = startY - 15 if startY - 15 > 15 else startY + 15
			cv2.putText(frame, label, (startX, y),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
			# enregistrement de l'image détectée 
			cv2.imwrite("detection.png", frame)

    # la touche q permet d'interrompre la boucle principale
	if key == ord("q"):
		break
 
	# mise à jour du FPS 
	fps.update()
 
# arret du compteur et affichage des informations dans la console
fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
 
cv2.destroyAllWindows()
vs.stop()