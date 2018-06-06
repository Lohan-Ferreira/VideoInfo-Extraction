
from sklearn.feature_extraction.text import TfidfVectorizer
import math
import numpy as np
from scipy.sparse import find
import http.client, urllib.parse, json, os, time
from sys import argv
from os.path import join, dirname
import wave
import contextlib
import glob
from lxml import html
import urllib.request
import re
from time import sleep
from PIL import Image # Importando o módulo Pillow para abrir a imagem no script
import ast


text = ''
cenas=[]
stopwordspt = ["a","acerca","adeus","agora","ainda","alem","algmas","algo","algumas","alguns","ali","além","ambas","ambos","ano","anos","antes","ao","aonde","aos","apenas","apoio","apontar","apos","após","aquela","aquelas","aquele","aqueles","aqui","aquilo","as","assim","através","atrás","até","aí","baixo","bastante","bem","boa","boas","bom","bons","breve","cada","caminho","catorze","cedo","cento","certamente","certeza","cima","cinco","coisa","com","como","comprido","conhecido","conselho","contra","contudo","corrente","cuja","cujas","cujo","cujos","custa","cá","da","daquela","daquelas","daquele","daqueles","dar","das","de","debaixo","dela","delas","dele","deles","demais","dentro","depois","desde","desligado","dessa","dessas","desse","desses","desta","destas","deste","destes","deve","devem","deverá","dez","dezanove","dezasseis","dezassete","dezoito","dia","diante","direita","dispoe","dispoem","diversa","diversas","diversos","diz","dizem","dizer","do","dois","dos","doze","duas","durante","dá","dão","dúvida","e","ela","elas","ele","eles","em","embora","enquanto","entao","entre","então","era","eram","essa","essas","esse","esses","esta","estado","estamos","estar","estará","estas","estava","estavam","este","esteja","estejam","estejamos","estes","esteve","estive","estivemos","estiver","estivera","estiveram","estiverem","estivermos","estivesse","estivessem","estiveste","estivestes","estivéramos","estivéssemos","estou","está","estás","estávamos","estão","eu","exemplo","falta","fará","favor","faz","fazeis","fazem","fazemos","fazer","fazes","fazia","faço","fez","fim","final","foi","fomos","for","fora","foram","forem","forma","formos","fosse","fossem","foste","fostes","fui","fôramos","fôssemos","geral","grande","grandes","grupo","ha","haja","hajam","hajamos","havemos","havia","hei","hoje","hora","horas","houve","houvemos","houver","houvera","houveram","houverei","houverem","houveremos","houveria","houveriam","houvermos","houverá","houverão","houveríamos","houvesse","houvessem","houvéramos","houvéssemos","há","hão","iniciar","inicio","ir","irá","isso","ista","iste","isto","já","lado","lhe","lhes","ligado","local","logo","longe","lugar","lá","maior","maioria","maiorias","mais","mal","mas","me","mediante","meio","menor","menos","meses","mesma","mesmas","mesmo","mesmos","meu","meus","mil","minha","minhas","momento","muito","muitos","máximo","mês","na","nada","nao","naquela","naquelas","naquele","naqueles","nas","nem","nenhuma","nessa","nessas","nesse","nesses","nesta","nestas","neste","nestes","no","noite","nome","nos","nossa","nossas","nosso","nossos","nova","novas","nove","novo","novos","num","numa","numas","nunca","nuns","não","nível","nós","número","o","obra","obrigada","obrigado","oitava","oitavo","oito","onde","ontem","onze","os","ou","outra","outras","outro","outros","para","parece","parte","partir","paucas","pegar","pela","pelas","pelo","pelos","perante","perto","pessoas","pode","podem","poder","poderá","podia","pois","ponto","pontos","por","porque","porquê","portanto","posição","possivelmente","posso","possível","pouca","pouco","poucos","povo","primeira","primeiras","primeiro","primeiros","promeiro","propios","proprio","própria","próprias","próprio","próprios","próxima","próximas","próximo","próximos","puderam","pôde","põe","põem","quais","qual","qualquer","quando","quanto","quarta","quarto","quatro","que","quem","quer","quereis","querem","queremas","queres","quero","questão","quieto","quinta","quinto","quinze","quáis","quê","relação","sabe","sabem","saber","se","segunda","segundo","sei","seis","seja","sejam","sejamos","sem","sempre","sendo","ser","serei","seremos","seria","seriam","será","serão","seríamos","sete","seu","seus","sexta","sexto","sim","sistema","sob","sobre","sois","somente","somos","sou","sua","suas","são","sétima","sétimo","só","tal","talvez","tambem","também","tanta","tantas","tanto","tarde","te","tem","temos","tempo","tendes","tenha","tenham","tenhamos","tenho","tens","tentar","tentaram","tente","tentei","ter","terceira","terceiro","terei","teremos","teria","teriam","terá","terão","teríamos","teu","teus","teve","tinha","tinham","tipo","tive","tivemos","tiver","tivera","tiveram","tiverem","tivermos","tivesse","tivessem","tiveste","tivestes","tivéramos","tivéssemos","toda","todas","todo","todos","trabalhar","trabalho","treze","três","tu","tua","tuas","tudo","tão","tém","têm","tínhamos","um","uma","umas","uns","usa","usar","vai","vais","valor","veja","vem","vens","ver","verdade","verdadeiro","vez","vezes","viagem","vindo","vinte","você","vocês","vos","vossa","vossas","vosso","vossos","vários","vão","vêm","vós","zero","à","às","área","é","éramos","és","último"]

D = glob.glob("[0-9]*")
tam = len(D)
for x in range (0,tam):
	D[x] = int(D[x])
D = sorted(D)
for x in range (0,tam):
	D[x] = str(D[x])
inicio_cena=[]


tr=''
for x in range(0 , tam):
	transcripts=[]
	#frames=[]
	text = ''
	tr = ''
	transcripts = glob.glob(D[x]+"/transcript*")
	for a in transcripts:
		tr += a 
	auxiliar = re.findall("transcript\d\d*",tr)
	for b in range(0,len(auxiliar)):
		auxiliar[b] = int(auxiliar[b].replace("transcript",""))
	auxiliar = sorted(auxiliar)
	#inicio_cena.append(auxiliar[0])
	#frames =glob.glob(D[x]+"/frame*")
	for tc in transcripts:
		text += open(tc,'r',encoding='utf-8').read()
	#for fm in frames:
	#	text += open(fm,'r').read()
	cenas.append(text)



tfidf_vectorizer = TfidfVectorizer(max_features=10000,stop_words = stopwordspt, ngram_range=(1,3))

tf = tfidf_vectorizer.fit_transform(cenas)
 
words = tfidf_vectorizer.get_feature_names()

full_list=[]
tuplas=[]


for y in range(0 , tam):
	tuplas=[]
	data = find(tf[y])
	for z in range (0, len(data[1])):
		tuplas.append((data[1][z],data[2][z]))
	tuplas.sort(key=lambda tup: tup[1], reverse = True)
	full_list.append(tuplas)


#Monta dicionario visivel (keyword) e dicionarios de busca (dicts)
keyword={}
dicts=[]
for z in range (0,len(full_list)):
	r = full_list[z][:5]
	dicts.append(dict(r))
	for key in r:
		keyword.update({words[key[0]]:key[0]})

file = open ("keywords.txt",'w')
for x in range (0, len(dicts)):
	file.write("Cena "+ str(x) +"\n")
	for key in dicts[x].keys():
		file.write(words[key] + ",")
	file.write('\n')


