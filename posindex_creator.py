import os
import re
import io
import string
import stemmer as ps
import pickle
import time
import operator

class Document:
	id = 0
	title = ''
	body = ''
	tokenized = []

	def __init__(self, id, title, body):
		self.id = id
		self.title = title
		self.body = body
		self.tokenized = []

bad_chars = '.:",;()\'<>'
path = 'Dataset'
stopwords = list(open('stopwords.txt'))
stopwords = [x.strip() for x in stopwords]

all_docs = []
dictionary = {}
posindex = {}
terms_before_preprocess = {}
terms_after_preprocess = {}
num_all_tokens = 0
num_non_stopword = 0

def text_tokenizer(text):
	p = ps.PorterStemmer()
	tokenized = text.split()
	tokenized = [x.strip(bad_chars) for x in tokenized if '&#' not in x and x != '' and '&lt;' not in x]
	for t in tokenized:
		if t not in terms_before_preprocess:
			terms_before_preprocess[t] = 1
		else:
			terms_before_preprocess[t] += 1
	return [p.stem(x.lower(), 0, len(x)-1) for x in tokenized]

def preprocessing(sgm_list):
	i = 0
	for s in sgm_list:
		with io.open(path + '/' + s, 'r', encoding='Latin-1') as f:
			read_data = f.read()
		reg = r'<REUTERS.*?<\/REUTERS>'
		docs_in_sgm = re.findall(reg, read_data, flags=re.DOTALL)
		for d in docs_in_sgm:
			reg = r'.*?NEWID=\"(\d+)\".*?<TEXT>.*?<TITLE>(.*?)<\/TITLE>.*?<BODY>(.*?)<\/BODY>.*?</TEXT>'
			m = re.search(reg, d, flags=re.DOTALL)
			if m:
				doc = Document(int(m.group(1)), m.group(2), m.group(3))
				all_docs.append(doc)
			else:
				m = re.search(r'NEWID=\"(\d+)\".*?<TITLE>(.*?)<\/TITLE>', d, flags=re.DOTALL)
				if m:
					i+=1
					doc = Document(int(m.group(1)), m.group(2), '')
					all_docs.append(doc)
	all_docs.sort(key=lambda x: x.id)
	for d in all_docs:
		d.tokenized = text_tokenizer(d.title)
		d.tokenized += text_tokenizer(d.body)
		d.tokenized = d.tokenized

def create_dict_posindex():
	global num_all_tokens
	global num_non_stopword
	i = 0
	for d in all_docs:
		j = 0
		for t in d.tokenized:
			if t not in stopwords:
				if t not in terms_after_preprocess:
					terms_after_preprocess[t] = 1
				else:
					terms_after_preprocess[t] += 1
				if t not in dictionary:
					dictionary[t] = i
					posindex[i] = {d.id: [j]}
					i += 1
				else:
					if d.id in posindex[dictionary[t]]:
						posindex[dictionary[t]][d.id].append(j)
					else:
						posindex[dictionary[t]][d.id] = [j]
				num_non_stopword += 1
			j += 1
			num_all_tokens += 1

	pickle.dump(dictionary, open('dictionary', 'wb'))
	pickle.dump(posindex, open('posindex', 'wb'))

def __main__():
	global num_all_tokens
	global num_non_stopword
	start_time = time.time()
	sgm_list = [x for x in os.listdir(path) if x.endswith('.sgm')]
	preprocessing(sgm_list)
	create_dict_posindex()
	print(num_all_tokens)
	print(num_non_stopword)
	print(len(terms_before_preprocess))
	print(len(terms_after_preprocess))
	print(dict(sorted(terms_before_preprocess.items(), key=operator.itemgetter(1), reverse=True)[:20]))
	print(dict(sorted(terms_after_preprocess.items(), key=operator.itemgetter(1), reverse=True)[:20]))
	print("--- %s seconds ---" % (time.time() - start_time))

__main__()