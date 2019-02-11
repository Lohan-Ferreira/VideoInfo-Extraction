import sys
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


var = docSim.calculate_similarity("i love your smile","i hate your eyes")
print(var[0]['score'])
print(type(var[0]))
