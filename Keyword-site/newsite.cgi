#!/usr/bin/python3


import cgi
import cgitb;



from sklearn.feature_extraction.text import TfidfVectorizer
import math
import numpy as np
from scipy.sparse import find
import http.client, urllib.parse, json, os, time
from sys import argv
from os.path import join, dirname
from bs4 import BeautifulSoup
import wave
import contextlib
import glob
from lxml import html
import urllib.request
import re
import operator
from time import sleep
from PIL import Image # Importando o módulo Pillow para abrir a imagem no script
import ast
from porterstemmer import Stemmer
from ptstemmer.implementations.OrengoStemmer import OrengoStemmer
from ptstemmer.implementations.SavoyStemmer import SavoyStemmer
from ptstemmer.implementations.PorterStemmer import PorterStemmer
from ptstemmer.support import PTStemmerUtilities
from SPARQLWrapper import SPARQLWrapper, JSON



#cgitb.enable()  # for troubleshooting



def find_times(f):
	times = []
	l = re.findall("\+\(\d*\.\d*\)",f )
	for i in l:
		i = i.replace("+","")
		i = i.replace("(","")
		i = i.replace(")","")
		times.append(float(i))
		
	return times




form = cgi.FieldStorage()
message = form.getvalue("message", "(no message)")
olddict = form.getvalue("oldict")
oldkeys = form.getvalue("oldkeys")
run = form.getvalue("run")
oldcenas = form.getvalue("oldcenas")
top_keywords = form.getvalue("top_keywords")
scene_request = form.getvalue("sceneid")
bankid = form.getvalue("bankid")
videoid = form.getvalue("videoid")

base_path = str(bankid)+"/"+str(videoid)+"/"

if(scene_request is None):
	scene_request = "0";
dicts=[]

f = open(base_path+"seg.txt")
times = find_times(f.read())
already = 0


#Stemmer - ingles
stemmer = Stemmer()

#Stemmer - portugues
s = OrengoStemmer() #or PorterStemmer or SavoyStemmer
s.enableCaching(1000)



def anotacao(text):
	f = {"text":text , "confidence" : "0.5" , "types" : "Concept"}
	a = urllib.parse.urlencode(f)
	#print(a)
	conn = http.client.HTTPConnection("model.dbpedia-spotlight.org:80")
	conn.request("GET", "/annotate?" +a)
	response = conn.getresponse().read().decode("UTF-8")
	soup = BeautifulSoup(str(response), 'lxml')
	l = soup.find_all('a', href=True)
	refs = []
	if (l):

		for a in l :
			
			refs.append(a['href'])
	return refs		
 



'''D = glob.glob("[0-9]*")
tam = len(D)
for x in range (0,tam):
	D[x] = int(D[x])
D = sorted(D)
for x in range (0,tam):
	D[x] = str(D[x])'''

stopwordspt = ["a","acerca","adeus","agora","ainda","alem","algmas","algo","algumas","alguns","ali","além","ambas","ambos","ano","anos","antes","ao","aonde","aos","apenas","apoio","apontar","apos","após","aquela","aquelas","aquele","aqueles","aqui","aquilo","as","assim","através","atrás","até","aí","baixo","bastante","bem","boa","boas","bom","bons","breve","cada","caminho","catorze","cedo","cento","certamente","certeza","cima","cinco","coisa","com","como","comprido","conhecido","conselho","contra","contudo","corrente","cuja","cujas","cujo","cujos","custa","cá","da","daquela","daquelas","daquele","daqueles","dar","das","de","debaixo","dela","delas","dele","deles","demais","dentro","depois","desde","desligado","dessa","dessas","desse","desses","desta","destas","deste","destes","deve","devem","deverá","dez","dezanove","dezasseis","dezassete","dezoito","dia","diante","direita","dispoe","dispoem","diversa","diversas","diversos","diz","dizem","dizer","do","dois","dos","doze","duas","durante","dá","dão","dúvida","e","ela","elas","ele","eles","em","embora","enquanto","entao","entre","então","era","eram","essa","essas","esse","esses","esta","estado","estamos","estar","estará","estas","estava","estavam","este","esteja","estejam","estejamos","estes","esteve","estive","estivemos","estiver","estivera","estiveram","estiverem","estivermos","estivesse","estivessem","estiveste","estivestes","estivéramos","estivéssemos","estou","está","estás","estávamos","estão","eu","exemplo","falta","fará","favor","faz","fazeis","fazem","fazemos","fazer","fazes","fazia","faço","fez","fim","final","foi","fomos","for","fora","foram","forem","forma","formos","fosse","fossem","foste","fostes","fui","fôramos","fôssemos","geral","grande","grandes","grupo","ha","haja","hajam","hajamos","havemos","havia","hei","hoje","hora","horas","houve","houvemos","houver","houvera","houveram","houverei","houverem","houveremos","houveria","houveriam","houvermos","houverá","houverão","houveríamos","houvesse","houvessem","houvéramos","houvéssemos","há","hão","iniciar","inicio","ir","irá","isso","ista","iste","isto","já","lado","lhe","lhes","ligado","local","logo","longe","lugar","lá","maior","maioria","maiorias","mais","mal","mas","me","mediante","meio","menor","menos","meses","mesma","mesmas","mesmo","mesmos","meu","meus","mil","minha","minhas","momento","muito","muitos","máximo","mês","na","nada","nao","naquela","naquelas","naquele","naqueles","nas","nem","nenhuma","nessa","nessas","nesse","nesses","nesta","nestas","neste","nestes","no","noite","nome","nos","nossa","nossas","nosso","nossos","nova","novas","nove","novo","novos","num","numa","numas","nunca","nuns","não","nível","nós","número","o","obra","obrigada","obrigado","oitava","oitavo","oito","onde","ontem","onze","os","ou","outra","outras","outro","outros","para","parece","parte","partir","paucas","pegar","pela","pelas","pelo","pelos","perante","perto","pessoas","pode","podem","poder","poderá","podia","pois","ponto","pontos","por","porque","porquê","portanto","posição","possivelmente","posso","possível","pouca","pouco","poucos","povo","primeira","primeiras","primeiro","primeiros","promeiro","propios","proprio","própria","próprias","próprio","próprios","próxima","próximas","próximo","próximos","puderam","pôde","põe","põem","quais","qual","qualquer","quando","quanto","quarta","quarto","quatro","que","quem","quer","quereis","querem","queremas","queres","quero","questão","quieto","quinta","quinto","quinze","quáis","quê","relação","sabe","sabem","saber","se","segunda","segundo","sei","seis","seja","sejam","sejamos","sem","sempre","sendo","ser","serei","seremos","seria","seriam","será","serão","seríamos","sete","seu","seus","sexta","sexto","sim","sistema","sob","sobre","sois","somente","somos","sou","sua","suas","são","sétima","sétimo","só","tal","talvez","tambem","também","tanta","tantas","tanto","tarde","te","tem","temos","tempo","tendes","tenha","tenham","tenhamos","tenho","tens","tentar","tentaram","tente","tentei","ter","terceira","terceiro","terei","teremos","teria","teriam","terá","terão","teríamos","teu","teus","teve","tinha","tinham","tipo","tive","tivemos","tiver","tivera","tiveram","tiverem","tivermos","tivesse","tivessem","tiveste","tivestes","tivéramos","tivéssemos","toda","todas","todo","todos","trabalhar","trabalho","treze","três","tu","tua","tuas","tudo","tão","tém","têm","tínhamos","um","uma","umas","uns","usa","usar","vai","vais","valor","veja","vem","vens","ver","verdade","verdadeiro","vez","vezes","viagem","vindo","vinte","você","vocês","vos","vossa","vossas","vosso","vossos","vários","vão","vêm","vós","zero","à","às","área","é","éramos","és","último"]
stopwordsen = ["'ll","'tis","'twas","'ve","10","39","a","a's","able","ableabout","about","above","abroad","abst","accordance","according","accordingly","across","act","actually","ad","added","adj","adopted","ae","af","affected","affecting","affects","after","afterwards","ag","again","against","ago","ah","ahead","ai","ain't","aint","al","all","allow","allows","almost","alone","along","alongside","already","also","although","always","am","amid","amidst","among","amongst","amoungst","amount","an","and","announce","another","any","anybody","anyhow","anymore","anyone","anything","anyway","anyways","anywhere","ao","apart","apparently","appear","appreciate","appropriate","approximately","aq","ar","are","area","areas","aren","aren't","arent","arise","around","arpa","as","aside","ask","asked","asking","asks","associated","at","au","auth","available","aw","away","awfully","az","b","ba","back","backed","backing","backs","backward","backwards","bb","bd","be","became","because","become","becomes","becoming","been","before","beforehand","began","begin","beginning","beginnings","begins","behind","being","beings","believe","below","beside","besides","best","better","between","beyond","bf","bg","bh","bi","big","bill","billion","biol","bj","bm","bn","bo","both","bottom","br","brief","briefly","bs","bt","but","buy","bv","bw","by","bz","c","c'mon","c's","ca","call","came","can","can't","cannot","cant","caption","case","cases","cause","causes","cc","cd","certain","certainly","cf","cg","ch","changes","ci","ck","cl","clear","clearly","click","cm","cmon","cn","co","co.","com","come","comes","computer","con","concerning","consequently","consider","considering","contain","containing","contains","copy","corresponding","could","could've","couldn","couldn't","couldnt","course","cr","cry","cs","cu","currently","cv","cx","cy","cz","d","dare","daren't","darent","date","de","dear","definitely","describe","described","despite","detail","did","didn","didn't","didnt","differ","different","differently","directly","dj","dk","dm","do","does","doesn","doesn't","doesnt","doing","don","don't","done","dont","doubtful","down","downed","downing","downs","downwards","due","during","dz","e","each","early","ec","ed","edu","ee","effect","eg","eh","eight","eighty","either","eleven","else","elsewhere","empty","end","ended","ending","ends","enough","entirely","er","es","especially","et","et-al","etc","even","evenly","ever","evermore","every","everybody","everyone","everything","everywhere","ex","exactly","example","except","f","face","faces","fact","facts","fairly","far","farther","felt","few","fewer","ff","fi","fifteen","fifth","fifty","fify","fill","find","finds","fire","first","five","fix","fj","fk","fm","fo","followed","following","follows","for","forever","former","formerly","forth","forty","forward","found","four","fr","free","from","front","full","fully","further","furthered","furthering","furthermore","furthers","fx","g","ga","gave","gb","gd","ge","general","generally","get","gets","getting","gf","gg","gh","gi","give","given","gives","giving","gl","gm","gmt","gn","go","goes","going","gone","good","goods","got","gotten","gov","gp","gq","gr","great","greater","greatest","greetings","group","grouped","grouping","groups","gs","gt","gu","gw","gy","h","had","hadn't","hadnt","half","happens","hardly","has","hasn","hasn't","hasnt","have","haven","haven't","havent","having","he","he'd","he'll","he's","hed","hell","hello","help","hence","her","here","here's","hereafter","hereby","herein","heres","hereupon","hers","herself","herse”","hes","hi","hid","high","higher","highest","him","himself","himse”","his","hither","hk","hm","hn","home","homepage","hopefully","how","how'd","how'll","how's","howbeit","however","hr","ht","htm","html","http","hu","hundred","i","i'd","i'll","i'm","i've","i.e.","id","ie","if","ignored","ii","il","ill","im","immediate","immediately","importance","important","in","inasmuch","inc","inc.","indeed","index","indicate","indicated","indicates","information","inner","inside","insofar","instead","int","interest","interested","interesting","interests","into","invention","inward","io","iq","ir","is","isn","isn't","isnt","it","it'd","it'll","it's","itd","itll","its","itself","itse”","ive","j","je","jm","jo","join","jp","just","k","ke","keep","keeps","kept","keys","kg","kh","ki","kind","km","kn","knew","know","known","knows","kp","kr","kw","ky","kz","l","la","large","largely","last","lately","later","latest","latter","latterly","lb","lc","least","length","less","lest","let","let's","lets","li","like","liked","likely","likewise","line","little","lk","ll","long","longer","longest","look","looking","looks","low","lower","lr","ls","lt","ltd","lu","lv","ly","m","ma","made","mainly","make","makes","making","man","many","may","maybe","mayn't","maynt","mc","md","me","mean","means","meantime","meanwhile","member","members","men","merely","mg","mh","microsoft","might","might've","mightn't","mightnt","mil","mill","million","mine","minus","miss","mk","ml","mm","mn","mo","more","moreover","most","mostly","move","mp","mq","mr","mrs","ms","msie","mt","mu","much","mug","must","must've","mustn't","mustnt","mv","mw","mx","my","myself","myse”","mz","n","na","name","namely","nay","nc","nd","ne","near","nearly","necessarily","necessary","need","needed","needing","needn't","neednt","needs","neither","net","netscape","never","neverf","neverless","nevertheless","new","newer","newest","next","nf","ng","ni","nine","ninety","nl","no","no-one","nobody","non","none","nonetheless","noone","nor","normally","nos","not","noted","nothing","notwithstanding","novel","now","nowhere","np","nr","nu","null","number","numbers","nz","o","obtain","obtained","obviously","of","off","often","oh","ok","okay","old","older","oldest","om","omitted","on","once","one","one's","ones","only","onto","open","opened","opening","opens","opposite","or","ord","order","ordered","ordering","orders","org","other","others","otherwise","ought","oughtn't","oughtnt","our","ours","ourselves","out","outside","over","overall","owing","own","p","pa","page","pages","part","parted","particular","particularly","parting","parts","past","pe","per","perhaps","pf","pg","ph","pk","pl","place","placed","places","please","plus","pm","pmid","pn","point","pointed","pointing","points","poorly","possible","possibly","potentially","pp","pr","predominantly","present","presented","presenting","presents","presumably","previously","primarily","probably","problem","problems","promptly","proud","provided","provides","pt","put","puts","pw","py","q","qa","que","quickly","quite","qv","r","ran","rather","rd","re","readily","really","reasonably","recent","recently","ref","refs","regarding","regardless","regards","related","relatively","research","reserved","respectively","resulted","resulting","results","right","ring","ro","room","rooms","round","ru","run","rw","s","sa","said","same","saw","say","saying","says","sb","sc","sd","se","sec","second","secondly","seconds","section","see","seeing","seem","seemed","seeming","seems","seen","sees","self","selves","sensible","sent","serious","seriously","seven","seventy","several","sg","sh","shall","shan't","shant","she","she'd","she'll","she's","shed","shell","shes","should","should've","shouldn","shouldn't","shouldnt","show","showed","showing","shown","showns","shows","si","side","sides","significant","significantly","similar","similarly","since","sincere","site","six","sixty","sj","sk","sl","slightly","sm","small","smaller","smallest","sn","so","some","somebody","someday","somehow","someone","somethan","something","sometime","sometimes","somewhat","somewhere","soon","sorry","specifically","specified","specify","specifying","sr","st","state","states","still","stop","strongly","su","sub","substantially","successfully","such","sufficiently","suggest","sup","sure","sv","sy","system","sz","t","t's","take","taken","taking","tc","td","tell","ten","tends","test","text","tf","tg","th","than","thank","thanks","thanx","that","that'll","that's","that've","thatll","thats","thatve","the","their","theirs","them","themselves","then","thence","there","there'd","there'll","there're","there's","there've","thereafter","thereby","thered","therefore","therein","therell","thereof","therere","theres","thereto","thereupon","thereve","these","they","they'd","they'll","they're","they've","theyd","theyll","theyre","theyve","thick","thin","thing","things","think","thinks","third","thirty","this","thorough","thoroughly","those","thou","though","thoughh","thought","thoughts","thousand","three","throug","through","throughout","thru","thus","til","till","tip","tis","tj","tk","tm","tn","to","today","together","too","took","top","toward","towards","tp","tr","tried","tries","trillion","truly","try","trying","ts","tt","turn","turned","turning","turns","tv","tw","twas","twelve","twenty","twice","two","tz","u","ua","ug","uk","um","un","under","underneath","undoing","unfortunately","unless","unlike","unlikely","until","unto","up","upon","ups","upwards","us","use","used","useful","usefully","usefulness","uses","using","usually","uucp","uy","uz","v","va","value","various","vc","ve","versus","very","vg","vi","via","viz","vn","vol","vols","vs","vu","w","want","wanted","wanting","wants","was","wasn","wasn't","wasnt","way","ways","we","we'd","we'll","we're","we've","web","webpage","website","wed","welcome","well","wells","went","were","weren","weren't","werent","weve","wf","what","what'd","what'll","what's","what've","whatever","whatll","whats","whatve","when","when'd","when'll","when's","whence","whenever","where","where'd","where'll","where's","whereafter","whereas","whereby","wherein","wheres","whereupon","wherever","whether","which","whichever","while","whilst","whim","whither","who","who'd","who'll","who's","whod","whoever","whole","wholl","whom","whomever","whos","whose","why","why'd","why'll","why's","widely","width","will","willing","wanna","gonna","wish","with","within","without","won","won't","wonder","wont","words","work","worked","working","works","world","would","would've","wouldn","wouldn't","wouldnt","ws","www","x","y","ye","year","years","yes","yet","you","you'd","you'll","you're","you've","youd","youll","young","younger","youngest","your","youre","yours","yourself","yourselves","youve","yt","yu","z","za","zero","zm","zr"]

#stopwordsen = [stemmer(w.lower()) for w in stopwordsen]


if(run=="1"):
	already=1
	keyword = ast.literal_eval(oldkeys)
	inicio_cena = ast.literal_eval(oldcenas)
	dicts = ast.literal_eval(olddict)
	top_keywords = ast.literal_eval(top_keywords)
	'''for x in range (0, len(olddict)):
		dicts.append(ast.literal_eval(olddict[0])'''
	tam = len(inicio_cena)

if(already == 0):
	cenas=[]
	inicio_cena=[]

	data = open(base_path+"GEN.json").read()
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
			aux += open(base_path+"transcript/transcript" + str(i) + ".txt").read().replace('\n',' ') + ' '
		else:
			inicio_cena.append(i)
			cenas.append(aux)
			scene_step += 1
			aux = ""
			aux += open(base_path+"transcript/transcript" + str(i) + ".txt").read().replace('\n',' ') + ' '

	cenas.append(aux)
	
	if(len(cenas)<=3):
		tfidf_vectorizer = TfidfVectorizer(max_features=2000,stop_words = stopwordsen , min_df=1, ngram_range=(1,2))
	else:
		tfidf_vectorizer = TfidfVectorizer(max_features=2000,stop_words = stopwordsen , min_df=3, ngram_range=(1,2))

	tf = tfidf_vectorizer.fit_transform(cenas)
	 
	words = tfidf_vectorizer.get_feature_names()

	'''refs = []
	for x in range (0,len(cenas)):
		refs.append(anotacao(cenas[x]))'''

	'''	#Montando matriz de co-ocorrencia !!!!PENSE EM COMO USAR ISSO AGORA!!!
	m_size = len(words)

	matrix = [[0 for x in range(m_size)] for y in range(m_size)] 

	for x in range(0,m_size):
		for y in range(0,m_size):
			if(x!=y):
				for z in range(0,len(token_lists)):
					if(words[x] in token_lists[z] and words[y] in token_lists[z]): 
						matrix[x][y]+=1			'''
	
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
		r = full_list[z][:4]
		dicts.append(dict(r))
		for key in r:
			keyword.update({stemmer(words[key[0]]):key[0]})

	#Guardando Top-Keyword de cada cena para busca externa
	top_keywords = []
	aux=''
	for x in range(0,len(dicts)):
		for w in dicts[x].keys():
			aux += words[w] + ' '	
		top_keywords.append(aux)
		aux=''
'''		word = words[list(dicts[x].keys())[1]]
		if(word not in top_keywords):
			top_keywords.append(word)
		else:
			top_keywords.append(words[list(dicts[x].keys())[2]])'''



cena=[]



#Criando lista de N-Grams das chaves de busca

message_words_list = []

one_gram = message.split(" ")
one_gram_aux = []


for w in one_gram:
	if(w not in stopwordsen):
		one_gram_aux.append([stemmer(w)])

one_gram = []
for w in one_gram_aux:
	one_gram.append(w[0])

n_gram = len(one_gram)
message_words_list.append(one_gram_aux)
for n in range (2, n_gram+1):
	if(n > len(one_gram)):
		break
	aux1 = []
	m=0
	while(m < ( len(one_gram) - (n-1) ) ):
		tupla=[]
		for count in range(0,n):
			tupla.append(one_gram[m+count])
		m = m + 1
		if(tupla):		
			aux1.append(tupla)
	message_words_list.append(aux1)

#Busca de Cenas que possuem uma N-Gram das chaves de busca
'''inp = stemmer(message)
key= keyword.get(inp)
for x in range(0,len ( dicts)):
	if(key in dicts[x].keys()):
		cena.append(str(x))'''

for x in range(0, len(message_words_list)):
	actual = message_words_list[x]
	for y in range(0,len(actual)):
		for z in range(0,len ( dicts)):
			verif = True
			for key in actual[y]:
				value = keyword.get(key)
				if(value not in dicts[z].keys()):
					verif = False
			if(verif):
				if(str(z) not in cena):
					cena.append(str(z))
'''
#Pegando links da recomendação no JSON
json = open("links.JSON").read()
aux = json.split("relatedTo>")
links=[]
for x in range(1,len(aux)):
	links.append(aux[x].split(">.<")[0].replace("<",""))
'''

#Adquirindo relacionados de cada topico

#path = os.getcwd().replace("/opt/lampp/htdocs/REST/bank_setups/",'').split('/')
#bankid = path[0]
#videoid= path[1]

sparql = SPARQLWrapper("http://localhost:9999/blazegraph/namespace/id_"+str(bankid)+"/sparql")
relateds = []
for i in range(0,len(inicio_cena)):

#First half of relateds

	relateds_aux = []
	sparql.setQuery("""
	select  ?topic ?value { ?topic <http://videos/"""+str(videoid)+"""/topics/"""+str(i)+"""> ?value FILTER (?topic != <http://timestart>) FILTER(?value > 0.9) }
	""")
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()
	#print(results)

	for result in results["results"]["bindings"]:
		relateds_aux.append([result["topic"]["value"].replace("http://videos/",'').replace("/topics",'').split('/'),result["value"]["value"]])


#Second half of relateds
	sparql.setQuery("""
	select  ?topic ?value { <http://videos/"""+str(videoid)+"""/topics/"""+str(i)+"""> ?topic ?value FILTER (?topic != <http://timestart>) FILTER(?value > 0.9) }
	""")
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()
	#print(results)

	for result in results["results"]["bindings"]:
		relateds_aux.append([result["topic"]["value"].replace("http://videos/",'').replace("/topics",'').split('/'),result["value"]["value"]])
	relateds.append(relateds_aux)






print ('Content-type: text/html; charset=utf-8')

print ("""
<html>
<link type="text/css" rel="stylesheet" href="/style.css" />
<head>
<title>Sample CGI Script</title>
  <meta charset="UTF-8">
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>

</head>



<body>

<h3>VIDEO</h3>

<video id="myvideo" width="70%" height="70%" controls>
  <source src="{0}GEN.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video> 
""".format(base_path))
print("""
<script>
  (function() {
    var cx = '004457791971694130138:zqmnlekmbk0';
    var gcse = document.createElement('script');
    gcse.type = 'text/javascript';
    gcse.async = true;
    gcse.src = 'https://cse.google.com/cse.js?cx=' + cx;
    var s = document.getElementsByTagName('script')[0];
    s.parentNode.insertBefore(gcse, s);
  })();
</script>
<div class="aditional">
Mídias Adicionais
<button title="Click to show/hide content" type="button" onclick="if(document.getElementById('search') .style.display=='none') {document.getElementById('search') .style.display=''}else{document.getElementById('search') .style.display='none'}">Google</button>
<button title="Click to show/hide content" type="button" onclick="if(document.getElementById('sdiv') .style.display=='none') {document.getElementById('sdiv') .style.display=''}else{document.getElementById('sdiv') .style.display='none'}">Wikipedia</button>
</div>












<script>
function scene_control(scene) { """)





for i in range(0,tam):
	print("""

if(scene==%s)
{
	document.getElementById("myvideo").currentTime = %s; 
}


""" % (i,times[inicio_cena[i]]))

print("""}</script>""")



print("""




""")


#Mantendo keywords organizadas na tela
kk = []
for k in keyword.keys():
	kk.append(k)
kk = sorted(kk)
'''
for x in range(0, len(kk)):
	print("""
	
<button id="%s" onclick="myFunction2('%s')">%s</button>

""" % (kk[x],kk[x],kk[x]) )


'''




tempo_inicio_cena = []
for x in range (0,len(inicio_cena)):
	tempo_inicio_cena.append(times[inicio_cena[x]])


print ("""



<div class="relateds" id="bdiv"></div>
<div id="debug"></div>

<div class=luminosity>
Brilho da tela
<button id="Luminosity" type="button" onclick="luminosity()">Alterar</button>
</div>


<script>

function luminosity() {
  if(document.body.style.backgroundColor== "black")
	{	document.body.style.backgroundColor="white";
		//document.body.style.backgroundImage="url('paper2.jpg')";
		document.body.style.color= "black";
	}
  else
	{
		document.body.style.backgroundColor= "black";
		document.body.style.color= "white";
	}
}


var tempos = %s;
var top_keywords = %s;
var relateds = %s;
var scene_request = %s;
var bankid = %s;
var cena_atual = 0;
var cena_buscada = -1;
var vid = document.getElementById("myvideo");

scene_control(scene_request);

vid.ontimeupdate = function(){
		cena_atual=0;
		while(vid.currentTime > tempos[cena_atual+1])	
		cena_atual++;
		var container = document.getElementById("bdiv");
		var container2 = document.getElementById("debug");
   		var content = container.innerHTML;
		var i;
		if(cena_atual != cena_buscada){
			while (container.firstChild) {
    				container.removeChild(container.firstChild);
			}
			
			container.append("Videos Relacionados");
			for(i = 0; i< relateds[cena_atual].length;i++){
				if(parseFloat(relateds[cena_atual][i][1]) >= 0.8){
				videoid = relateds[cena_atual][i][0][0];
				sceneid = relateds[cena_atual][i][0][1];
				var button = document.createElement("input");
				button.type = "button";
				button.value = "Video "+videoid+" topico" + sceneid;
				button.className="acount-btn";
				button.onclick = function()
				{
					var f = document.createElement("form");
					f.method = "POST";
					f.action = "newsite.cgi";

					var sceneid_input = document.createElement("input");
					sceneid_input.name="sceneid";
					sceneid_input.value=sceneid;

					var  bankid_input = document.createElement("input"); 
					bankid_input.name="bankid";
					bankid_input.value=bankid;

					var  videoid_input = document.createElement("input"); 
					videoid_input.name="videoid";
					videoid_input.value=videoid;


					f.appendChild(sceneid_input);
					f.appendChild(bankid_input);
					f.appendChild(videoid_input);

    					document.body.appendChild(f);
					f.submit();
				};
				container.appendChild(button);}}
	
			//Elemento para busca dinamica no google
			gsearch = google.search.cse.element.getElement("gsearch");
			gsearch.execute(top_keywords[cena_atual]);
			//ELemento para busca dinamica no wikipedia
			fetchResults(top_keywords[cena_atual]);
			document.getElementById('sdiv') .style.display='none';
			document.getElementById('search') .style.display='none';


		cena_buscada=cena_atual;
		}
		
}

function fetchResults(searchQuery) {
  const endpoint = `https://en.wikipedia.org/w/api.php?format=json&action=query&&generator=search&gsrsearch=${searchQuery}&gsrlimit=5&origin=*&prop=pageimages|extracts&exintro&explaintext&redirects=1`;
  fetch(endpoint)
    .then(response => response.json())
    .then(data => {
      const results = data.query.pages;
      for (var result in results){
	console.log(results[result].extract);
}
      displayResults(results);
  });
}

function displayResults(results) {
  // Store a reference to `.searchResults`
  const searchResults = document.getElementById("sdiv");
  // Remove all child elements
  searchResults.innerHTML = "";
  // Loop over results array
  searchResults.insertAdjacentHTML("beforeend",
      `<img src="../wikipedia.png" class="center" width="240" height="180">`);

  for (var result in results){
	const url = encodeURI(`https://en.wikipedia.org/wiki/${results[result].title}`);

  searchResults.insertAdjacentHTML("beforeend",
      `<div class="wikidata-in">
        <h3 class="resultItem-title">
          <a href=${url} target="_blank">${results[result].title}</a>
        </h3>
        <span class="resultItem-snippet">${results[result].extract}</span><br>
      </div>`
    );

}
//<img  src= ${results[result].thumbnail.source} width="100" height="100">

}



</script>

<form name = "myform" action = "REST/bank_setups/27/1/newsite.cgi" method = "POST">
   <input type = "hidden" value = "Run the Program!!!">
</form>


<p>
Digite uma palavra de busca :
<form name = "myform" method="post" action="newsite.cgi">
    <p><input type="text" name="message" value =""/></p>
    <p><input type="hidden" name="run" value="1" /></p>
    <p><input type="hidden" name="oldict" value="%s" /></p>
    <p><input type="hidden" name="oldcenas" value="%s" /></p>
    <p><input type="hidden" name="oldkeys" value="%s" /></p>
    <p><input type="hidden" name="top_keywords" value="%s" /></p>
    <p><input type="hidden" name="bankid" value="%s" /></p>
    <p><input type="hidden" name="videoid" value="%s" /></p>

</form>

Cenas Relacionadas:
</body>

</html>
""" % (tempo_inicio_cena,top_keywords,relateds,scene_request,bankid,dicts,inicio_cena,keyword,top_keywords,bankid,videoid))



for e in cena:
	print("""

<button class="acount-btn" id="%s" onclick="scene_control(%s)">%s</button>

</html>

""" %(e,e,e))

print("""
<div class="wikidata" id="search">
<gcse:searchresults-only gname="gsearch" webSearchQueryAddition=""></gcse:searchresults-only>
</div>
<div class="wikidata" id="sdiv">
 </div>
""")





