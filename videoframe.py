import http.client, urllib.parse, json, os, time
from sys import argv
from os.path import join, dirname
from bs4 import BeautifulSoup
import wave
import contextlib
import glob
from lxml import html
import urllib.request
import xmltodict
import re
from time import sleep

from PIL import Image # Importando o módulo Pillow para abrir a imagem no script
import cv2

import pytesseract # Módulo para a utilização da tecnologia OCR



'''fname = '/tmp/test.wav'
with contextlib.closing(wave.open(fname,'r')) as f:
    frames = f.getnframes()
    rate = f.getframerate()
    duration = frames / float(rate)
    print(duration)'''


def durationCount(path_to_audio_file):
	with contextlib.closing(wave.open(path_to_audio_file,'r')) as f:
    		frames = f.getnframes()
    		rate = f.getframerate()
    		duration = frames / float(rate)
    		return duration



D = 183
def transcribeAudio(path_to_audio_file, samplerate):
    headers = {"Content-type": "audio/wav; codec=\"audio/pcm\"; samplerate="+samplerate}

    with open(path_to_audio_file, 'rb') as audio_file:
        response = ""
        try:
            body = audio_file.read()
            #Connect to server to recognize the wave binary
            conn = http.client.HTTPConnection("200.131.219.151:8082")
            conn.request("POST", "/client/dynamic/recognize",
                   body, headers)
            response = conn.getresponse().read().decode("UTF-8")
            conn.close()
        finally:
            audio_file.close()

        return response


def anotacao(text, index):
	f = {"text":text}
	a = urllib.parse.urlencode(f)
	#print(a)
	conn = http.client.HTTPConnection("model.dbpedia-spotlight.org:80")
	conn.request("GET", "/pt/annotate?" +a)
	response = conn.getresponse().read().decode("UTF-8")
	soup = BeautifulSoup(str(response), 'lxml')
	l = soup.find_all('a', href=True)
	if (l):
		f = open("anotation"+str(index)+".txt","a")
		for a in l :
			#print('here!')
			f.write(a['href'])
			f.write("\n")




def durationConvert(durt):
	if(len(durt) == 2):
		durt_list.append(int(durt[0])*60 + int(durt[1]) )
	if(len(durt) == 3):
		durt_list.append(int(durt[0])*3600 + int(durt[1])*60 + int(durt[2]) )






'''def extraction(text):
	f = open("videoaula.html","r")
	soup = BeautifulSoup(f, 'lxml')
	l = soup.find_all("li", id = True)
	if(l):
		for a in l:
			
			m = re.search('\d\d:\d\d:\d\d|\d\d:\d\d',str(a))
			if (m):
				print(m.group(0).split(':'))
				durationConvert(m.group(0).split(':'))'''




#durt_list= []
#extraction("ab")

#print (durt_list)
text =""
index = ""

tag = 0
while(os.path.isdir("video" + str(tag))):
	tag = tag + 1

dir_path = "video" + str(tag)

os.system("mkdir " + dir_path)

#filename= argv[1].split('.')[0]



os.system("ffmpeg -i " + argv[1] + " -vn -ac 1 -ab 256k -ar 16000 " + dir_path +"/pureAudio.wav")
os.system("python py-webrtcvad-master/example.py 3 "+ dir_path +"/pureAudio.wav " + dir_path)

D = len(glob.glob("*"+ dir_path +"/chunk*"))
cap = cv2.VideoCapture(argv[1])
fps = cap.get(cv2.CAP_PROP_FPS)


#print(D)
i=0
j=0
time = 0.0
timeadd=0.0
print (D)
while(i < D):
	r = ""
	
	
	if(i <= 9):
		#print(i)
		r =  transcribeAudio(dir_path + "/chunk-0" + str(i)+ ".wav", "8000")
		timeadd = durationCount(dir_path + "/chunk-0" + str(i)+ ".wav")
		sleep(1)
		

	else:
		#print(i)
		r =  transcribeAudio( dir_path + "/chunk-" + str(i)+ ".wav", "8000")
		timeadd =  durationCount( dir_path + "/chunk-" + str(i)+ ".wav")
		sleep(1)
	
	#lexical = ""
	
	desired_frame = ((time + timeadd)/2) * fps
	time = time + timeadd
	cap.set(1,desired_frame)
	success,image = cap.read()
	cv2.imwrite( dir_path+"/frame%d.jpg" % i, image)
	frame_text = pytesseract.image_to_string( Image.open(dir_path +'/frame'+str(i)+'.jpg'), lang='por' )

	data=json.loads(r)
	if data:
		if data['hypotheses'][0]:
			#anotacao(data['hypotheses'][0]['utterance'], i)
			'''if(i % 2 == 0):
				text += data['hypotheses'][0]['utterance']
				index +=str(i)
				
			else:'''
			#index += " "+str(i)
			text += data['hypotheses'][0]['utterance']
			text += " "
			#print(index)


	print(text)
	i = i + 1
	anotacao(text,j)
	anotacao(frame_text,j)
	j= j+1
	text = ""
	index=""


