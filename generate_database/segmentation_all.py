import http.client, urllib.parse, json, os, time
from sys import argv
from os.path import join, dirname
from bs4 import BeautifulSoup
import wave
import contextlib
import glob
from time import sleep
import nltk
import xml.etree.ElementTree as ET
import re
import Extraction
from PIL import Image # Importando o módulo Pillow para abrir a imagem no script
import cv2
import pytesseract # Módulo para a utilização da tecnologia OCR


'''fname = '/tmp/test.wav'
with contextlib.closing(wave.open(fname,'r')) as f:
    frames = f.getnframes()
    rate = f.getframerate()
    duration = frames / float(rate)
    print(duration)'''
def get_time_index(f):
	c = []
	tree = ET.parse(f+".index")
	root = tree.getroot()
	for i in range(2, len(root)):
		c.append(float(root[i][0].text))
		for j in range(2, len(root[i])):
			c.append(float(root[i][j][0].text))
			for k in range(2, len(root[i][j])):
				c.append(float(root[i][j][k][0].text))
	return c


def find_times(f):
	times = []
	l = re.findall("\-\(\d*\.\d*\)",f )
	for i in l:
		i = i.replace("-","")
		i = i.replace("(","")
		i = i.replace(")","")
		times.append(float(i))
		
	return times

def stem(text, index, dir_path):
	f = open(dir_path+"/transcript"+str(index)+".txt","a")
	a = text.replace(".", "")
	a = a.split(" ")


	for w in a:
		try:
			stemmer = nltk.stem.PorterStemmer()
			f.write(stemmer.stem(w))
			f.write("\n")
		except IndexError:
			print("")
			

	f.close()

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

            conn = http.client.HTTPConnection("200.131.219.151")
		
            conn.request("POST", "/asr?endofspeech=false",
                   body, headers)
            response = conn.getresponse().read().decode("UTF-8")
            conn.close()
        finally:
            audio_file.close()

        return response


def anotacao(text, index, dir):
	f = {"text":text}
	a = urllib.parse.urlencode(f)
	#print(a)
	conn = http.client.HTTPConnection("model.dbpedia-spotlight.org:80")
	conn.request("GET", "/annotate?" +a)
	response = conn.getresponse().read().decode("UTF-8")
	soup = BeautifulSoup(str(response), 'lxml')
	l = soup.find_all('a', href=True)
	f = open(dir+"/anotation"+str(index)+".txt","a")
	if (l):

		for a in l :
			
			f.write(a['href'])
			f.write("\n")
	else:
		f.write("--")
	f.close()		
	

text =""
index = ""

tag = 0

video_list = glob.glob("VideosAula/*")

print(video_list)

for v in video_list:


	filename = v
	videoname = v.split('/')[1]
	
	os.system("mkdir "+ filename +"/chunks")
	os.system("ffmpeg -i " + filename+"/"+ videoname +".mp4" +" -vn -ac 1 -ab 256k -ar 16000 "+ filename + "/pureAudio.wav")
	os.system("python py-webrtcvad-master/example.py 2 "+ filename +"/pureAudio.wav "+ filename +"/chunks> "+filename+"/seg.txt")

	f = open(filename+"/seg.txt")
	times = find_times(f.read())
	D = len(glob.glob(filename+"/chunks/chunk*"))
	cap = cv2.VideoCapture(filename+"/"+ videoname + ".mp4")
	fps = cap.get(cv2.CAP_PROP_FPS)


	print(D)
	i=0
	j=0
	t = 0
	k = 1
	tag2 = 0
	sync = []
	sync = Extraction.return_times(filename+"/"+videoname+".html")

	time = 0.0
	dir_path2 = filename+"/"+str(tag2)
	dir_path = filename+"/"
	while(i <= D-1):
		c = ""
		if(k >= len(sync)):

			if( i >= D):
				break;

			if(not os.path.isdir(filename+"/"+str(tag2+1))):
				dir_path2 = filename+"/"+str(tag2+1)
				os.system("mkdir " + dir_path2)
		

		
			if(i <= 9):
				print(i)
			
				c =  transcribeAudio(dir_path + "chunks/chunk-0" + str(i)+ ".wav", "8000")

				sleep(1)


			else:

				print(i)
		
				c =  transcribeAudio( dir_path + "chunks/chunk-" + str(i)+ ".wav", "8000")
				sleep(1)


			desired_frame = (times[i]-2) * fps
			cap.set(1,desired_frame)
			success,image = cap.read()
			cv2.imwrite(dir_path2+"/frameb%d.jpg" % i, image)
			frame_text = pytesseract.image_to_string( Image.open(dir_path2 +'/frameb'+str(i)+'.jpg'), lang='eng' )
			arcv = open(dir_path2 +"/frameb%d.txt" % i ,"w")
			arcv.write(frame_text)
			arcv.close()
	

	

			if ( i == 0 ):
				desired_frame = ( times[i]/2.0 ) * fps


			else :
				desired_frame = ( (times[i-1] + times[i])/2 ) * fps

	
			cap.set(1,desired_frame)
			success,image = cap.read()
			cv2.imwrite(dir_path2+"/framem%d.jpg" % i, image)
			frame_text = pytesseract.image_to_string( Image.open(dir_path2+'/framem'+str(i)+'.jpg'), lang='eng' )
			arcv = open(dir_path2+"/framem%d.txt" % i ,"w")
			arcv.write(frame_text)
			arcv.close()



			data=json.loads(c)
			if data:
				try:
					if data['data'][0]:
						#anotacao(data['hypotheses'][0]['utterance'], i)
						'''if(i % 2 == 0):
							text += data['hypotheses'][0]['utterance']
							index +=str(i)
		
						else:'''
						#index += " "+str(i)
						text += data['data'][0]['text']
						text += " "
						i = i + 1
						stem(text,j, dir_path2)
						anotacao(text, j, dir_path2)
						j = j +1
			
	
				except KeyError:
					print("keyError")
		
	
		while(k < len(sync)):
			r = ""
		
		
			if(os.path.isdir(filename+"/"+str(tag2))):
				tag2 = tag2 + 1

			dir_path2 =filename+"/"+str(tag2)
			os.system("mkdir " + dir_path2)
		
			while (time < sync[k]):

				if(i <= 9):
					print(i)
				
				
					r =  transcribeAudio(dir_path + "chunks/chunk-0" + str(i)+ ".wav", "8000")

					sleep(1)
		
		

				else:
				
					print(i)
				
					r =  transcribeAudio( dir_path + "chunks/chunk-" + str(i)+ ".wav", "8000")
				
					sleep(1)


				desired_frame = (times[i]-2) * fps
				cap.set(1,desired_frame)
				success,image = cap.read()
				cv2.imwrite( dir_path2+"/frameb%d.jpg" % i, image)
				frame_text = pytesseract.image_to_string( Image.open(dir_path2 +'/frameb'+str(i)+'.jpg'), lang='eng' )
				arcv = open( dir_path2 +"/frameb%d.txt" % i ,"w")
				arcv.write(frame_text)
				arcv.close()
	

	

				if ( i == 0 ):
					desired_frame = ( times[i]/2.0 ) * fps


				else :
					desired_frame = ( (times[i-1] + times[i])/2 ) * fps

	
				cap.set(1,desired_frame)
				success,image = cap.read()
				cv2.imwrite(dir_path2+"/framem%d.jpg" % i, image)
				frame_text = pytesseract.image_to_string( Image.open(dir_path2+'/framem'+str(i)+'.jpg'), lang='eng' )
				arcv = open(dir_path2+"/framem%d.txt" % i ,"w")
				arcv.write(frame_text)
				arcv.close()

				lexical = ""
				data=json.loads(r)
				if data:
					try:
						if data['data'][0]:
							#anotacao(data['hypotheses'][0]['utterance'], i)
							'''if(i % 2 == 0):
								text += data['hypotheses'][0]['utterance']
								index +=str(i)
				
							else:'''
							#index += " "+str(i)
							text += data['data'][0]['text']
							text += " "
							#print(index)
							i = i + 1
							if (i > D-1 ):
								break
							#print(text)
							stem(text,j, dir_path2)
							anotacao(text, j, dir_path2)
						
							j = j + 1
							time = times[i]
			
						
					except KeyError:
						print("keyError")						


			
			
				text = ""
				index=""
			time = 0
			k = k +1
	
		text = ''


