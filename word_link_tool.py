#Word-Link Function, for use in HPA
#Built by Dustin Kochensparger
#August 2012

from nltk.corpus import wordnet
from nltk.tokenize import RegexpTokenizer
import string
from nltk.tag.sequential import ClassifierBasedPOSTagger
from nltk.corpus import treebank

import pickle

#Initialize Replacement Patterns
d_pos2wnpos={}
d_pos2wnpos["NN"]   = ['n']
d_pos2wnpos["RB"]   = ['r']
d_pos2wnpos["VB"]   = ['v']
d_pos2wnpos["JJ"]   = ['a','s']

#Synset Finder
#Built by Colin Sherrill
def synsets_for_wordpos(word, wnpos):
  return filter(lambda x: "."+wnpos+"." in x.name ,wordnet.synsets(word))


def lemma_names_for_synsets(synset):
  return map(lambda lemma: lemma.name, synset.lemmas)


def all_syns(word, tpos):
  results = [] 
  if tpos in d_pos2wnpos:
    for wnpos in d_pos2wnpos[tpos]:
      results+=map(lambda synset:  lemma_names_for_synsets(synset), synsets_for_wordpos(word, wnpos))
  return filter(lambda token: "_" not in token, list(set(sum(results, []))))

#Remove punctuation (fringe cases?)
def remove_punct(sentence_raw = ""):
	return sentence_raw.translate(string.maketrans("",""), string.punctuation)

#Tokenize on whitespace
def tokenize_text(sentence_no_punct):
	tokenizer = RegexpTokenizer('\s+', gaps=True)
	return tokenizer.tokenize(sentence_no_punct)

#Tag using the Classifier Based Tagger, trained on the Treebank corpus (subject to change)
def pos_tag_text(sentence_clean =''):	
	#Find out if the file exists
	try:
		f = open('tagger.pickle', 'r')	
		tagger = pickle.load(f)
	#Create a pickled tagger if not exists
	except IOError as e:
		train_sents = treebank.tagged_sents()
		tagger = ClassifierBasedPOSTagger(train=train_sents)
		#Pickle the tagger
		f = open('tagger.pickle', 'w')
		pickle.dump(tagger, f)
		f.close()	
	return tagger.tag(sentence_clean)

#Convert Complex Tags to simple ones
def replace_tags(sentence_tagged = []):
	for i in range(len(sentence_tagged)):	
		#Copy the words from the list to be modified
		word = sentence_tagged[i][0]
		tag = sentence_tagged[i][1]
		tag_list = list(tag)	

		sentence_tagged.pop(i) #Remove the old entry from the list	
		
		#if block for replacements
		if tag_list[0] == 'V':
			tag = tag.replace(tag, 'VB')		
		elif tag_list[0] == 'N':
			tag = tag.replace(tag, 'NN')		
		elif tag_list[0] == 'J':
			tag = tag.replace(tag, 'JJ')
		elif tag_list[0] == 'R':
			if tag == 'RP':
				pass
			else:
				tag = tag.replace(tag, 'RB')		
		else:
			pass
	
		concat_str3 = word,tag	
		sentence_tagged.insert(i, concat_str3)
	return sentence_tagged

#Find word links
def find_word_links(sentence1 = [], sentence2 = []):
	word_links = []

	for i in range(len(sentence1)):
		for j in range(len(sentence2)):
			#Look for words that are identical, and have the same POS
			if sentence1[i][0] == sentence2[j][0]:
				if sentence1[i][1] == sentence2[j][1]:
					concat_str = i,j					
					word_links.append(concat_str)

			#Look for words that are synonyms, using WordNet
			elif sentence1[i][0] != sentence2[j][0]:
			
				syns1 = all_syns(sentence1[i][0], sentence1[i][1])
				syns2 = all_syns(sentence2[j][0], sentence2[j][1])				
		
				#Check to see if synonyms exist between the two words
				if set(syns1) & set(syns2):
					concat_str2 = i,j
					word_links.append(concat_str2)					
	return word_links

#Remove duplicate entries
def remove_duplicates(word_links = []):
	for i in range(len(word_links)):
		test_char = word_links.pop(0) #Remove the last entry
		removed = False #Reset boolean
		for j in word_links: #Iterate through all other words
			if test_char[0] == j[0] or test_char[1] == j[1]:
				word_links.remove(j)
				removed = True
		if removed == False: #Ensure to add only pairs that did not find matches
			word_links.append(test_char)
	return word_links
#prepare a sentence
def prep_sentence(sentence_raw):
	#Remove Punctuation
	sentence_no_punct = remove_punct(sentence_raw)

	#Tokenize
	sentence_clean = tokenize_text(sentence_no_punct)

	#POS Tag
	sentence_tagged = pos_tag_text(sentence_clean)

	#Replace Tags
	sentence_replaced = replace_tags(sentence_tagged)

	return sentence_replaced

#Return all the word links for a set of sentences
def give_me_wordlinks(sentence1_raw = "", sentence2_raw = ""):
	#Find the word links
	word_links = find_word_links(sentence1_raw, sentence2_raw)

	#Remove Duplicate Entries
	word_links = remove_duplicates(word_links)

	return word_links






























