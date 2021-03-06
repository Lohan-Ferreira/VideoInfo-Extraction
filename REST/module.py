
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
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import find



sys.path.insert(0, 'document_similarity/')
from document_similarity import DocSim
from gensim.models.keyedvectors import KeyedVectors


googlenews_model_path = 'document_similarity/data/GoogleNews-vectors-negative300.bin'
stopwords_path = "document_similarity/data/stopwords_en.txt"

docSim = None
model = KeyedVectors.load_word2vec_format(googlenews_model_path, binary=True,limit=500000)

with open(stopwords_path, 'r') as fh:
	stopwords = fh.read().split(",")

docSim = DocSim.DocSim(model, stopwords=stopwords)



stopwordspt = ["a","acerca","adeus","agora","ainda","alem","algmas","algo","algumas","alguns","ali","além","ambas","ambos","ano","anos","antes","ao","aonde","aos","apenas","apoio","apontar","apos","após","aquela","aquelas","aquele","aqueles","aqui","aquilo","as","assim","através","atrás","até","aí","baixo","bastante","bem","boa","boas","bom","bons","breve","cada","caminho","catorze","cedo","cento","certamente","certeza","cima","cinco","coisa","com","como","comprido","conhecido","conselho","contra","contudo","corrente","cuja","cujas","cujo","cujos","custa","cá","da","daquela","daquelas","daquele","daqueles","dar","das","de","debaixo","dela","delas","dele","deles","demais","dentro","depois","desde","desligado","dessa","dessas","desse","desses","desta","destas","deste","destes","deve","devem","deverá","dez","dezanove","dezasseis","dezassete","dezoito","dia","diante","direita","dispoe","dispoem","diversa","diversas","diversos","diz","dizem","dizer","do","dois","dos","doze","duas","durante","dá","dão","dúvida","e","ela","elas","ele","eles","em","embora","enquanto","entao","entre","então","era","eram","essa","essas","esse","esses","esta","estado","estamos","estar","estará","estas","estava","estavam","este","esteja","estejam","estejamos","estes","esteve","estive","estivemos","estiver","estivera","estiveram","estiverem","estivermos","estivesse","estivessem","estiveste","estivestes","estivéramos","estivéssemos","estou","está","estás","estávamos","estão","eu","exemplo","falta","fará","favor","faz","fazeis","fazem","fazemos","fazer","fazes","fazia","faço","fez","fim","final","foi","fomos","for","fora","foram","forem","forma","formos","fosse","fossem","foste","fostes","fui","fôramos","fôssemos","geral","grande","grandes","grupo","ha","haja","hajam","hajamos","havemos","havia","hei","hoje","hora","horas","houve","houvemos","houver","houvera","houveram","houverei","houverem","houveremos","houveria","houveriam","houvermos","houverá","houverão","houveríamos","houvesse","houvessem","houvéramos","houvéssemos","há","hão","iniciar","inicio","ir","irá","isso","ista","iste","isto","já","lado","lhe","lhes","ligado","local","logo","longe","lugar","lá","maior","maioria","maiorias","mais","mal","mas","me","mediante","meio","menor","menos","meses","mesma","mesmas","mesmo","mesmos","meu","meus","mil","minha","minhas","momento","muito","muitos","máximo","mês","na","nada","nao","naquela","naquelas","naquele","naqueles","nas","nem","nenhuma","nessa","nessas","nesse","nesses","nesta","nestas","neste","nestes","no","noite","nome","nos","nossa","nossas","nosso","nossos","nova","novas","nove","novo","novos","num","numa","numas","nunca","nuns","não","nível","nós","número","o","obra","obrigada","obrigado","oitava","oitavo","oito","onde","ontem","onze","os","ou","outra","outras","outro","outros","para","parece","parte","partir","paucas","pegar","pela","pelas","pelo","pelos","perante","perto","pessoas","pode","podem","poder","poderá","podia","pois","ponto","pontos","por","porque","porquê","portanto","posição","possivelmente","posso","possível","pouca","pouco","poucos","povo","primeira","primeiras","primeiro","primeiros","promeiro","propios","proprio","própria","próprias","próprio","próprios","próxima","próximas","próximo","próximos","puderam","pôde","põe","põem","quais","qual","qualquer","quando","quanto","quarta","quarto","quatro","que","quem","quer","quereis","querem","queremas","queres","quero","questão","quieto","quinta","quinto","quinze","quáis","quê","relação","sabe","sabem","saber","se","segunda","segundo","sei","seis","seja","sejam","sejamos","sem","sempre","sendo","ser","serei","seremos","seria","seriam","será","serão","seríamos","sete","seu","seus","sexta","sexto","sim","sistema","sob","sobre","sois","somente","somos","sou","sua","suas","são","sétima","sétimo","só","tal","talvez","tambem","também","tanta","tantas","tanto","tarde","te","tem","temos","tempo","tendes","tenha","tenham","tenhamos","tenho","tens","tentar","tentaram","tente","tentei","ter","terceira","terceiro","terei","teremos","teria","teriam","terá","terão","teríamos","teu","teus","teve","tinha","tinham","tipo","tive","tivemos","tiver","tivera","tiveram","tiverem","tivermos","tivesse","tivessem","tiveste","tivestes","tivéramos","tivéssemos","toda","todas","todo","todos","trabalhar","trabalho","treze","três","tu","tua","tuas","tudo","tão","tém","têm","tínhamos","um","uma","umas","uns","usa","usar","vai","vais","valor","veja","vem","vens","ver","verdade","verdadeiro","vez","vezes","viagem","vindo","vinte","você","vocês","vos","vossa","vossas","vosso","vossos","vários","vão","vêm","vós","zero","à","às","área","é","éramos","és","último"]
stopwordsen = ["'ll","'tis","'twas","'ve","10","39","a","a's","able","ableabout","about","above","abroad","abst","accordance","according","accordingly","across","act","actually","ad","added","adj","adopted","ae","af","affected","affecting","affects","after","afterwards","ag","again","against","ago","ah","ahead","ai","ain't","aint","al","all","allow","allows","almost","alone","along","alongside","already","also","although","always","am","amid","amidst","among","amongst","amoungst","amount","an","and","announce","another","any","anybody","anyhow","anymore","anyone","anything","anyway","anyways","anywhere","ao","apart","apparently","appear","appreciate","appropriate","approximately","aq","ar","are","area","areas","aren","aren't","arent","arise","around","arpa","as","aside","ask","asked","asking","asks","associated","at","au","auth","available","aw","away","awfully","az","b","ba","back","backed","backing","backs","backward","backwards","bb","bd","be","became","because","become","becomes","becoming","been","before","beforehand","began","begin","beginning","beginnings","begins","behind","being","beings","believe","below","beside","besides","best","better","between","beyond","bf","bg","bh","bi","big","bill","billion","biol","bj","bm","bn","bo","both","bottom","br","brief","briefly","bs","bt","but","buy","bv","bw","by","bz","c","c'mon","c's","ca","call","came","can","can't","cannot","cant","caption","case","cases","cause","causes","cc","cd","certain","certainly","cf","cg","ch","changes","ci","ck","cl","clear","clearly","click","cm","cmon","cn","co","co.","com","come","comes","computer","con","concerning","consequently","consider","considering","contain","containing","contains","copy","corresponding","could","could've","couldn","couldn't","couldnt","course","cr","cry","cs","cu","currently","cv","cx","cy","cz","d","dare","daren't","darent","date","de","dear","definitely","describe","described","despite","detail","did","didn","didn't","didnt","differ","different","differently","directly","dj","dk","dm","do","does","doesn","doesn't","doesnt","doing","don","don't","done","dont","doubtful","down","downed","downing","downs","downwards","due","during","dz","e","each","early","ec","ed","edu","ee","effect","eg","eh","eight","eighty","either","eleven","else","elsewhere","empty","end","ended","ending","ends","enough","entirely","er","es","especially","et","et-al","etc","even","evenly","ever","evermore","every","everybody","everyone","everything","everywhere","ex","exactly","example","except","f","face","faces","fact","facts","fairly","far","farther","felt","few","fewer","ff","fi","fifteen","fifth","fifty","fify","fill","find","finds","fire","first","five","fix","fj","fk","fm","fo","followed","following","follows","for","forever","former","formerly","forth","forty","forward","found","four","fr","free","from","front","full","fully","further","furthered","furthering","furthermore","furthers","fx","g","ga","gave","gb","gd","ge","general","generally","get","gets","getting","gf","gg","gh","gi","give","given","gives","giving","gl","gm","gmt","gn","go","goes","going","gone","good","goods","got","gotten","gov","gp","gq","gr","great","greater","greatest","greetings","group","grouped","grouping","groups","gs","gt","gu","gw","gy","h","had","hadn't","hadnt","half","happens","hardly","has","hasn","hasn't","hasnt","have","haven","haven't","havent","having","he","he'd","he'll","he's","hed","hell","hello","help","hence","her","here","here's","hereafter","hereby","herein","heres","hereupon","hers","herself","herse”","hes","hi","hid","high","higher","highest","him","himself","himse”","his","hither","hk","hm","hn","home","homepage","hopefully","how","how'd","how'll","how's","howbeit","however","hr","ht","htm","html","http","hu","hundred","i","i'd","i'll","i'm","i've","i.e.","id","ie","if","ignored","ii","il","ill","im","immediate","immediately","importance","important","in","inasmuch","inc","inc.","indeed","index","indicate","indicated","indicates","information","inner","inside","insofar","instead","int","interest","interested","interesting","interests","into","invention","inward","io","iq","ir","is","isn","isn't","isnt","it","it'd","it'll","it's","itd","itll","its","itself","itse”","ive","j","je","jm","jo","join","jp","just","k","ke","keep","keeps","kept","keys","kg","kh","ki","kind","km","kn","knew","know","known","knows","kp","kr","kw","ky","kz","l","la","large","largely","last","lately","later","latest","latter","latterly","lb","lc","least","length","less","lest","let","let's","lets","li","like","liked","likely","likewise","line","little","lk","ll","long","longer","longest","look","looking","looks","low","lower","lr","ls","lt","ltd","lu","lv","ly","m","ma","made","mainly","make","makes","making","man","many","may","maybe","mayn't","maynt","mc","md","me","mean","means","meantime","meanwhile","member","members","men","merely","mg","mh","microsoft","might","might've","mightn't","mightnt","mil","mill","million","mine","minus","miss","mk","ml","mm","mn","mo","more","moreover","most","mostly","move","mp","mq","mr","mrs","ms","msie","mt","mu","much","mug","must","must've","mustn't","mustnt","mv","mw","mx","my","myself","myse”","mz","n","na","name","namely","nay","nc","nd","ne","near","nearly","necessarily","necessary","need","needed","needing","needn't","neednt","needs","neither","net","netscape","never","neverf","neverless","nevertheless","new","newer","newest","next","nf","ng","ni","nine","ninety","nl","no","no-one","nobody","non","none","nonetheless","noone","nor","normally","nos","not","noted","nothing","notwithstanding","novel","now","nowhere","np","nr","nu","null","number","numbers","nz","o","obtain","obtained","obviously","of","off","often","oh","ok","okay","old","older","oldest","om","omitted","on","once","one","one's","ones","only","onto","open","opened","opening","opens","opposite","or","ord","order","ordered","ordering","orders","org","other","others","otherwise","ought","oughtn't","oughtnt","our","ours","ourselves","out","outside","over","overall","owing","own","p","pa","page","pages","part","parted","particular","particularly","parting","parts","past","pe","per","perhaps","pf","pg","ph","pk","pl","place","placed","places","please","plus","pm","pmid","pn","point","pointed","pointing","points","poorly","possible","possibly","potentially","pp","pr","predominantly","present","presented","presenting","presents","presumably","previously","primarily","probably","problem","problems","promptly","proud","provided","provides","pt","put","puts","pw","py","q","qa","que","quickly","quite","qv","r","ran","rather","rd","re","readily","really","reasonably","recent","recently","ref","refs","regarding","regardless","regards","related","relatively","research","reserved","respectively","resulted","resulting","results","right","ring","ro","room","rooms","round","ru","run","rw","s","sa","said","same","saw","say","saying","says","sb","sc","sd","se","sec","second","secondly","seconds","section","see","seeing","seem","seemed","seeming","seems","seen","sees","self","selves","sensible","sent","serious","seriously","seven","seventy","several","sg","sh","shall","shan't","shant","she","she'd","she'll","she's","shed","shell","shes","should","should've","shouldn","shouldn't","shouldnt","show","showed","showing","shown","showns","shows","si","side","sides","significant","significantly","similar","similarly","since","sincere","site","six","sixty","sj","sk","sl","slightly","sm","small","smaller","smallest","sn","so","some","somebody","someday","somehow","someone","somethan","something","sometime","sometimes","somewhat","somewhere","soon","sorry","specifically","specified","specify","specifying","sr","st","state","states","still","stop","strongly","su","sub","substantially","successfully","such","sufficiently","suggest","sup","sure","sv","sy","system","sz","t","t's","take","taken","taking","tc","td","tell","ten","tends","test","text","tf","tg","th","than","thank","thanks","thanx","that","that'll","that's","that've","thatll","thats","thatve","the","their","theirs","them","themselves","then","thence","there","there'd","there'll","there're","there's","there've","thereafter","thereby","thered","therefore","therein","therell","thereof","therere","theres","thereto","thereupon","thereve","these","they","they'd","they'll","they're","they've","theyd","theyll","theyre","theyve","thick","thin","thing","things","think","thinks","third","thirty","this","thorough","thoroughly","those","thou","though","thoughh","thought","thoughts","thousand","three","throug","through","throughout","thru","thus","til","till","tip","tis","tj","tk","tm","tn","to","today","together","too","took","top","toward","towards","tp","tr","tried","tries","trillion","truly","try","trying","ts","tt","turn","turned","turning","turns","tv","tw","twas","twelve","twenty","twice","two","tz","u","ua","ug","uk","um","un","under","underneath","undoing","unfortunately","unless","unlike","unlikely","until","unto","up","upon","ups","upwards","us","use","used","useful","usefully","usefulness","uses","using","usually","uucp","uy","uz","v","va","value","various","vc","ve","versus","very","vg","vi","via","viz","vn","vol","vols","vs","vu","w","want","wanted","wanting","wants","was","wasn","wasn't","wasnt","way","ways","we","we'd","we'll","we're","we've","web","webpage","website","wed","welcome","well","wells","went","were","weren","weren't","werent","weve","wf","what","what'd","what'll","what's","what've","whatever","whatll","whats","whatve","when","when'd","when'll","when's","whence","whenever","where","where'd","where'll","where's","whereafter","whereas","whereby","wherein","wheres","whereupon","wherever","whether","which","whichever","while","whilst","whim","whither","who","who'd","who'll","who's","whod","whoever","whole","wholl","whom","whomever","whos","whose","why","why'd","why'll","why's","widely","width","will","willing","wanna","gonna","wish","with","within","without","won","won't","wonder","wont","words","work","worked","working","works","world","would","would've","wouldn","wouldn't","wouldnt","ws","www","x","y","ye","year","years","yes","yet","you","you'd","you'll","you're","you've","youd","youll","young","younger","youngest","your","youre","yours","yourself","yourselves","youve","yt","yu","z","za","zero","zm","zr"]


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

def create_namespace(bankid):
	xml = open("ns.xml").read().replace("MY_NAMESPACE","id_"+str(bankid))
	headers = {'Content-Type': 'application/xml'}
	requests.post('http://localhost:9999/blazegraph/namespace',data=xml,headers=headers)

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


def relationship(bankid,videoid):
	server = sparql.SPARQLServer("http://127.0.0.1:9999/blazegraph/namespace/id_"+str(bankid)+"/sparql")
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
			for i in range(len(times),len(glob.glob(v+"/transcript/transcript"))):
				aux += open(v+"/transcript/transcript" + str(i) + ".txt").read().replace('\n',' ') + ' '  

			cenas.append(aux.lower())

		names.append(v)
		scenes_full_list.append(cenas)

	######Calculating Keywords & Sending to Blazegraph#######################
	if(len(cenas)<=3):
		tfidf_vectorizer = TfidfVectorizer(max_features=20000,stop_words = stopwordsen , min_df=1, ngram_range=(1,2))
	else:
		tfidf_vectorizer = TfidfVectorizer(max_features=20000,stop_words = stopwordsen , min_df=3, ngram_range=(1,2))

	tf = tfidf_vectorizer.fit_transform(cenas)
	 
	words = tfidf_vectorizer.get_feature_names()

	full_list=[]
	tuplas=[]

	tam = len(cenas)
	for y in range(0 , tam):
		tuplas=[]
		data = find(tf[y])
		for z in range (0, len(data[1])):
			tuplas.append((data[1][z],data[2][z]))
		tuplas.sort(key=lambda tup: tup[1], reverse = True)
		full_list.append(tuplas)

	dicts=[]
	for z in range (0,len(full_list)):
		r = full_list[z][:10]
		keywords=''
		for key in r:
			keywords+= words[key[0]] + ' '
		server.update("INSERT DATA {<http://videos/"+str(videoid)+"/topics/"+str(z)+"> <http://keywords> \""+keywords+"\"}")



	######Calculating Similarities & Sending to Blazegraph####################


	main_index = names.index(path+"/"+str(videoid))
	for x in range(0,len(names)):
		names[x] = names[x].replace("bank_setups/"+str(bankid)+"/",'')
	text = ''
	for i in range(0,len(scenes_full_list[main_index])):
		for j in range(0,len(scenes_full_list)):
			for k in range(0,len(scenes_full_list[j])):
				if(j==main_index and i>=k):
					continue
				result = docSim.calculate_similarity(scenes_full_list[main_index][i],scenes_full_list[j][k])
				text += "<http://videos/"+str(videoid)+"/topics/"+str(i)+"> <http://videos/"+names[j]+"/topics/"+str(k)+"> \""+str(result[0]['score'])+"\"^^<http://www.w3.org/2001/XMLSchema#double>  .\n"
	open("insert.nt",'w').write(text)
	os.system("curl -X POST -H 'Content-Type:text/x-nquads' --data-binary '@insert.nt' http://localhost:9999/blazegraph/namespace/id_"+str(bankid)+"/sparql")
'''				server.update("INSERT DATA {<http://videos/"+str(videoid)+"/topics/"+str(i)+"> <http://videos/"+names[j]+"/topics/"+str(k)+"> "+str(result[0]['score'])+" }")
'''


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

	#var = docSim.calculate_similarity("i love your smile","i hate your eyes")



