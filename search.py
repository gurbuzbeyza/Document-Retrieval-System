import stemmer as ps
import pickle
import sys

dictionary = pickle.load(open("dictionary", "rb" ))
posindex = pickle.load(open("posindex", "rb" ))

p = ps.PorterStemmer()


def handle_conj_query(word_list):
	try:
		w1_id = dictionary[word_list[0]]
	except:
		return []
	doclist1 = list(posindex[w1_id].keys())
	for i in range(1, len(word_list)):
		if not doclist1:
			return []
		w2_id = dictionary[word_list[i]]
		doclist2 = list(posindex[w2_id].keys())
		doclist1 = [x for x in doclist1 if x in doclist2]
	return doclist1


def handle_phrase_query(word_list):

	return handle_prox_query(word_list, [0] * (len(word_list) - 1))


def handle_prox_query(word_list, prox_list):
	common_docs = handle_conj_query(word_list)
	if not common_docs:
		return []
	phrase_docs = []
	for c in common_docs:
		w1_id = dictionary[word_list[0]]
		indices = posindex[w1_id][c]
		for j in range(1, len(word_list)):
			w2_id = dictionary[word_list[j]]
			new_indices = []
			for x in posindex[w2_id][c]:
				if not indices:
					break
				for i in indices:
					if i > x:
						break
					elif abs(x - i - 1) <= prox_list[j-1]:
						new_indices.append(x)
			indices = new_indices
		if indices:
			phrase_docs.append(c)
	return phrase_docs

while True:
	q = [x for x in input('Please enter a query: ').split()]
	if q[0] == '1':
		word_list = [p.stem(x.lower(), 0, len(x)-1) for x in q[1:] if x != 'AND']
		print (word_list)
		print (str(len(handle_conj_query(word_list))) + ' documents found.\n' + str(handle_conj_query(word_list)))
	elif q[0] == '2':
		word_list = [p.stem(x.lower(), 0, len(x)-1) for x in q[1:]]
		print (str(len(handle_phrase_query(word_list))) + ' documents found.\n' + str(handle_phrase_query(word_list)))
	elif q[0] == '3':
		word_list = [p.stem(x.lower(), 0, len(x)-1) for x in q[1:] if '/' not in x]
		prox_list = [int(x[1:]) for x in q[1:] if '/' in x]
		print (str(len(handle_prox_query(word_list, prox_list))) + ' documents found.\n' + str(handle_prox_query(word_list, prox_list)))
	else:
		print (q[0] + ' is not a valid query number!')