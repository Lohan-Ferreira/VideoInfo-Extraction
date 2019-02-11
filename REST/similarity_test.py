import zipfile
import ast
import operator
import os
import sys
from pymantic import sparql
import glob
import requests
import re



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

def find_times(f):
	times = []
	l = re.findall("\+\(\d*\.\d*\)",f )
	for i in l:
		i = i.replace("+","")
		i = i.replace("(","")
		i = i.replace(")","")
		times.append(float(i))
		
	return times


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


relationship(27,1)



