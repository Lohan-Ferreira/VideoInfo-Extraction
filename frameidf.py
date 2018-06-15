import glob
from nltk.tokenize import word_tokenize
import nltk
import enchant
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import pairwise_distances


def ocr_distance(path):
	D = glob.glob(path+"*frame*.txt")
	dict = enchant.Dict("en_US")

	qnt = len(D)/2



	frametokens = []
	for x in range(0,int(qnt)):
		tokens1 = []
		tokens2 = []
		clear_tokens = ''
		f1 = open (path+"frameb" + str(x) + ".txt", 'r',encoding='utf-8')
		f2 = open (path+"framem" + str(x) + ".txt", 'r',encoding='utf-8')
		tokens1 = word_tokenize(f1.read())
		tokens2 = word_tokenize(f2.read())
		for t in tokens1:
			if(dict.check(t)):
				clear_tokens += t +" "
		for t in tokens2:
			if(dict.check(t)):
				clear_tokens += t +" "
		frametokens.append(clear_tokens)


	tfidf_vectorizer = TfidfVectorizer(max_features=10000,stop_words = 'english', ngram_range=(1,1))

	tf = tfidf_vectorizer.fit_transform(frametokens)

	distance = pairwise_distances(tf, metric = 'cosine')
	 
	words = tfidf_vectorizer.get_feature_names()
	return distance
