
# System modules
from datetime import datetime

# 3rd party modules
from flask import make_response, abort

import zipfile
import ast
import operator
import os
import sys
from pymantic import sparql
import glob
import requests
import re


#Starting similarity model
sys.path.insert(0, 'document_similarity/')
from document_similarity import DocSim
from gensim.models.keyedvectors import KeyedVectors


googlenews_model_path = 'document_similarity/data/GoogleNews-vectors-negative300.bin'
stopwords_path = "document_similarity/data/stopwords_en.txt"

docSim = None
model = KeyedVectors.load_word2vec_format(googlenews_model_path, binary=True)

with open(stopwords_path, 'r') as fh:
	stopwords = fh.read().split(",")

docSim = DocSim.DocSim(model, stopwords=stopwords)


#Utility funcs
def find_times(f):
	times = []
	l = re.findall("\+\(\d*\.\d*\)",f )
	for i in l:
		i = i.replace("+","")
		i = i.replace("(","")
		i = i.replace(")","")
		times.append(float(i))
		
	return times


def get_timestamp():
	return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
	
	
#Create a new namespace on blazegraph with request bankid
def create_namespace(bankid):
	xml = open("ns.xml").read().replace("MY_NAMESPACE","id_"+str(bankid))
	headers = {'Content-Type': 'application/xml'}
	requests.post('http://localhost:9999/blazegraph/namespace',data=xml,headers=headers)
	
#Insert received video data (Topics and timestart of topic) on requested bankid
def insert_in_namespace(bankid,videoid):
	server = sparql.SPARQLServer("http://127.0.0.1:9999/blazegraph/namespace/id_"+str(bankid)+"/sparql")
	path = "bank_setups/"+str(bankid)+"/"+str(videoid)

	data = open(path+"/GEN.json").read()
	data = ast.literal_eval(data)
	elements = sorted(data.items(), key=operator.itemgetter(0), reverse = True)
	sequences = []
	for e in elements:
		sequences.append(ast.literal_eval(e[0]))
	sequences = sorted(sequences)

	for i in range(0,len(sequences)):
		server.update("INSERT DATA {<http://videos/"+str(videoid)+"> <http://topics> <http://videos/"+str(videoid)+"/topics/"+str(i)+">}")
		server.update("INSERT DATA {<http://videos/"+str(videoid)+"/topics/"+str(i)+"> <http://timestart> \""+str(sequences[i])+"\" }")


#Calculate video's topics similarity with other topics from requested bankid
#Insert new similarity values on blazegraph
def relationship(bankid,videoid):
	path = "bank_setups/"+str(bankid)
	videos = glob.glob(path+"/*")


	##################Preparing Scenes############
	scenes_full_list = []
	names = []
	for v in videos:	
		f = open(v+"/seg.txt")
		times = find_times(f.read())

		cenas=[]
		inicio_cena=[]

		data = open(v+"/GEN.json").read()
		data = ast.literal_eval(data)

		elements = sorted(data.items(), key=operator.itemgetter(0), reverse = True)

		sequences = []

		for e in elements:
			sequences.append(ast.literal_eval(e[0]))

		sequences = sorted(sequences)

		tam = len(sequences)
		scene_step = 1
		aux = ""
		inicio_cena.append(0)
	
		for i in range(0, len(times)):
			if(scene_step == len(sequences) or sequences[scene_step] > times[i] ):
				aux += open(v+"/transcript/transcript" + str(i) + ".txt").read().replace('\n',' ') + ' '
			else:
				inicio_cena.append(i)
				cenas.append(aux.lower())
				scene_step += 1
				aux = ""
				aux += open(v+"/transcript/transcript" + str(i) + ".txt").read().replace('\n',' ') + ' '

		cenas.append(aux.lower())
		aux = ""
		if(times[len(times)-1] < sequences[len(sequences)-1]):
			for i in range(len(times),len(glob.glob(d+"/transcript/transcript"))):
				aux += open(v+"/transcript/transcript" + str(i) + ".txt").read().replace('\n',' ') + ' '  

			cenas.append(aux.lower())

		names.append(v)
		scenes_full_list.append(cenas)

	######Calculating Similarities & Sending to Blazegraph####################
	server = sparql.SPARQLServer("http://127.0.0.1:9999/blazegraph/namespace/id_"+str(bankid)+"/sparql")

	main_index = names.index(path+"/"+str(videoid))
	for x in range(0,len(names)):
		names[x] = names[x].replace("bank_setups/"+str(bankid)+"/",'')
	
	for i in range(0,len(scenes_full_list[main_index])):
		for j in range(0,len(scenes_full_list)):
			for k in range(0,len(scenes_full_list[j])):
				if(j==main_index and i>=k):
					continue
				result = docSim.calculate_similarity(scenes_full_list[main_index][i],scenes_full_list[j][k])
				server.update("INSERT DATA {<http://videos/"+str(videoid)+"/topics/"+str(i)+"> <http://videos/"+names[j]+"/topics/"+str(k)+"> "+str(result[0]['score'])+" }")


#Unpack received .zip with video data and stores on server
def unpack(upfile,bankid):
	zip_ref = zipfile.ZipFile(upfile, 'r')

	if(os.path.isdir("bank_setups/"+str(bankid))):
		#Send video data to bank and calculate similarity
		next = len(glob.glob("bank_setups/"+str(bankid)+"/*")) + 1
		os.system("mkdir bank_setups/"+str(bankid)+"/"+str(next))
		zip_ref.extractall("bank_setups/"+str(bankid)+"/"+str(next)+"/")
		insert_in_namespace(bankid,next)
		relationship(bankid,next)
		
	else:
		#Create new bank and add video data
		os.system("mkdir bank_setups/"+str(bankid))
		os.system("mkdir bank_setups/"+str(bankid)+"/1")
		create_namespace(bankid)
		zip_ref.extractall("bank_setups/"+str(bankid)+"/1/")
		insert_in_namespace(bankid,1)
		relationship(bankid,1)
		
	zip_ref.close()




