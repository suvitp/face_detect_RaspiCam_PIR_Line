import face_recognition
import cv2
import time
from picamera2 import Picamera2, Preview
import argparse
import requests
import os
from os import listdir
from os.path import isfile, join
from imutils.video import VideoStream
import imutils
import pickle
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
GPIO.setwarnings(False)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(23, GPIO.IN)

def linenotify(message):
	url = 'https://notify-api.line.me/api/notify'
	token = '-------------------------------' # Line Notify Token
	img = {'imageFile': open('facedetect.jpg','rb')} #Local picture File
	data = {'message': message}
	headers = {'Authorization':'Bearer ' + token}
	session = requests.Session()
	session_post = session.post(url, headers=headers, files=img, data =data)
	print(session_post.text) 

def CamCapture():
	picam = Picamera2()
	picam.start()
	time.sleep(2)
	picam.capture_file("facedetect.jpg")
	picam.close()
	print("Picture Captured")

known_face_encodings = []
known_face_names = []
pathKnownImg = "encodings.pickle"
data = pickle.loads(open(pathKnownImg, "rb").read())
known_face_encodings = data["encodings"]
#known_face_names = data["name"]

def face_detect() :
	face_locations = []
	face_encodings = []
	face_names = []
	output = face_recognition.load_image_file("facedetect.jpg")

    # Find all the faces and face encodings in the current frame of video
	face_locations = face_recognition.face_locations(output)
	print("Found {} faces in image.".format(len(face_locations)))
	face_encodings = face_recognition.face_encodings(output, face_locations)

    # Loop over each face found in the frame to see if it's someone we know.
	for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
		matches = face_recognition.compare_faces(known_face_encodings, face_encoding,0.4)
		name = "Unknown Person"
		if True in matches:
			matchedIdxs = [i for (i, b) in enumerate(matches) if b]
			counts = {}
			for i in matchedIdxs:
				name = data["names"][i]
				counts[name] = counts.get(name, 0) + 1
			name = max(counts, key=counts.get)
		face_names.append(name)
		myString = ",".join(face_names)
	if len(face_locations)==0 :
		return "not detect"
	else :	
		return myString
while True:
	i = GPIO.input(23)
	print(i)
	if (i == 0) :
		GPIO.output(27, GPIO.LOW)
		print('no intruders',i)
		print('LED OFF')
	elif(i == 1):
		GPIO.output(27, GPIO.HIGH)
		time.sleep (1)
		GPIO.output(27, GPIO.LOW)
		time.sleep (1)
		GPIO.output(27, GPIO.HIGH)
		time.sleep (1)
		GPIO.output(27, GPIO.LOW)
		time.sleep (1)
		CamCapture()
		msg = face_detect()
		print('LED OFF')
		print(msg)
		linenotify(msg)
		time.sleep(10)