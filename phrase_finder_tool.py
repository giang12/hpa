import hpa_tests_stanford_parser
from hpa_tests_stanford_parser import sentence2tree
from hpa_tests_stanford_parser import stop_stanford_parser_process
from word_link_tool import remove_punct
import string

SENTENCE_1=""


def find_phrase(sentence_1=""):
	stop_stanford_parser_process()
	global SENTENCE_1
	SENTENCE_1=sentence_1
	phrases=get_me_phrase()
	#print phrases
	phrases=packaging_phrase_list(phrases)
	return phrases

def get_me_phrase():
	global SENTENCE_1
	tree_1=sentence2tree(SENTENCE_1)
	tree_1=tree_1[0]
	ctr = 0
	#print tree_1
	for i in range(len(tree_1.leaves())):
		if len(tree_1[tree_1.leaf_treeposition(i)]) == 1 and tree_1[tree_1.leaf_treeposition(i)] in string.punctuation:
			tree_1[tree_1.leaf_treeposition(i)]=-1
		elif tree_1[tree_1.leaf_treeposition(i)] in [ "'d", "'ll", "'m", "'ve", "n't", "'s", "'", "re", "'re"]:
			tree_1[tree_1.leaf_treeposition(i)]=-1
		else:
			tree_1[tree_1.leaf_treeposition(i)]=ctr
			ctr += 1
	phrase_list=tree_to_list_ofPhrase(tree_1)
	return phrase_list

def tree_to_list_ofPhrase(trees):
	list_of_phrase=[]
	for i in range(len(trees)):
		list_of_phrase.append(trees[i])
		if(len(trees[i])>1):
			list_of_phrase.extend(tree_to_list_ofPhrase(trees[i]))	
	return list_of_phrase

def packaging_phrase_list(phrase_list):
	for i in range(len(phrase_list)):
		phrase_list[i]=[phrase_list[i].node, phrase_list[i].leaves()[0], phrase_list[i].leaves()[len(phrase_list[i].leaves())-1]]
 
	return phrase_list

