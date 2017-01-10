import word_link_tool
from word_link_tool import give_me_wordlinks
from word_link_tool import prep_sentence
import phrase_finder_tool
from phrase_finder_tool import find_phrase 
import string
def get_word_links(prepped_sens):
	return give_me_wordlinks(prepped_sens[0], prepped_sens[1])

# chunk sentence to phrases
def get_phrases(sen=[]):
	phrases=[]
	for i in range(len(sen)):
		phrase = find_phrase(sen[i])
		phrase.pop()
		phrase = filter(lambda x: x[1] >= 0 and x[2] >= 0, phrase)
		phrases+=[phrase]
	return phrases
#prepare the list of sentnece before creating wordlink
def get_prep(sen=[]):
	sens=[]
	for i in range(len(sen)):
		temp_sen = prep_sentence(sen[i])
		sens+=[temp_sen]
	return sens

def remove_nonlink_phrases(word_link, phrases):
	new_phrases=[[],[]]
	for i in range(len(phrases)):
		for j in range(len(phrases[i])):
			found=False
			for a in range(len(word_link)):
				if(found==True):
					break
				else:
					wordlink_index=word_link[a][i]
					phrase_start=phrases[i][j][1]
					phrase_end=phrases[i][j][2]
					if(wordlink_index>=phrase_start and wordlink_index<=phrase_end):
						new_phrases[i].append(phrases[i][j])
						found=True
	return new_phrases

#common phrases between 2 sentences
def give_me_equiv_phrases(word_link, phrases):
	phrases= remove_nonlink_phrases(word_link, phrases)
	equiv_phrases=[]
	for i in range(len(phrases[0])):
		for j in range(len(phrases[1])):
			type1=phrases[0][i][0]
			type2=phrases[1][j][0]
			if(type1==type2):
                                status=check_equiv_wordlink(word_link,[phrases[0][i],phrases[1][j]])
                                if(status==True):
                                    equiv_phrases.append([phrases[0][i],phrases[1][j]])
	equiv_phrases=sorted(equiv_phrases, key=lambda x: -1 *(x[0][2]-x[0][1]))		
	return equiv_phrases
#check if 2 phrases from 2 sens have common link
def check_equiv_wordlink(word_link, phrases):
        has_atleast_1link=False
        link_mismatched=False
        phrase1_start=phrases[0][1]
	phrase1_end=phrases[0][2]
	phrase2_start=phrases[1][1]
	phrase2_end=phrases[1][2]
        for i in range(len(word_link)):
                wordlink_phrase1=word_link[i][0]
                wordlink_phrase2=word_link[i][1]
                if((wordlink_phrase1>=phrase1_start and wordlink_phrase1<=phrase1_end) and (wordlink_phrase2>=phrase2_start and wordlink_phrase2<=phrase2_end)):
                        has_atleast_1link=True
                elif(
			(wordlink_phrase1<phrase1_start or wordlink_phrase1>phrase1_end) and 
			(wordlink_phrase2<phrase2_start or wordlink_phrase2>phrase2_end)
		    ):
                        pass
                else:
                        link_mismatched=True
                                                
        return (link_mismatched==False and has_atleast_1link==True)

#remove white_space before punct and remove duplicate
def remove_space_at_punct(sen):
	sen=sen.split()
	list_of_contraction=['t','d','ll','m','ve','s','re']
	i=1
	while i in range(1,len(sen)):
		if(sen[i] in string.punctuation or sen[i] in list_of_contraction):
			temp=sen[i]
			sen[i-1]+=temp
			sen.pop(i)
		i+=1
	return " ".join(sen)
		
def process_sentences(sens):
	for i in range(len(sens)):
		sens[i]=remove_space_at_punct(sens[i])
	return sens
import word_link_tool as wlt
import string 

def index_sentence_as_str(senx, letter_id = "X"):
	sen_list = wlt.tokenize_text(senx)
	#print sen_list
	index_list = []
	original_token_list = []
	d_id2tok = {}
	for i, token in enumerate(sen_list):
		index_list += [letter_id+"_"+str(i)+"_"]
		if token[-1] in string.punctuation:
			index_list += [token[-1]]
			original_token_list += [token[:-1]]
			d_id2tok[letter_id+"_"+str(i)+"_"] = token[:-1]
		else:
			original_token_list += [token]
			d_id2tok[letter_id+"_"+str(i)+"_"] = token
	return " ".join(index_list), original_token_list, d_id2tok

#need 2 sentences and 1 equiv_phrase of sen1 + sen2( 2d[[],[]]) same goes for 1 set of 2 prepped sens
lowerCase_eng_sentences = []
def give_me_equiv_sentences(sen1,sen2,prepped_sens,phrases):
	eq_phs = give_me_equiv_phrases(get_word_links(prepped_sens), phrases)
	#print eq_phs
	(sen1_index_list , sen1_orig_tokens, sen1_d_id2tok) = index_sentence_as_str(sen1, "A")
	(sen2_index_list , sen2_orig_tokens, sen2_d_id2tok) = index_sentence_as_str(sen2, "B")
	d_id2tok = dict(sen1_d_id2tok.items() + sen2_d_id2tok.items())
	#print sen1_index_list , sen1_orig_tokens, sen1_d_id2tok
	#print sen2_index_list , sen2_orig_tokens, sen2_d_id2tok

	known_sentences = [sen1_index_list, sen2_index_list]
	for eq_ph in eq_phs[:]:
		phA = " ".join(map(lambda x: "A_"+str(x)+"_", range(eq_ph[0][1], eq_ph[0][2]+1)))
		phB = " ".join(map(lambda x: "B_"+str(x)+"_", range(eq_ph[1][1], eq_ph[1][2]+1)))
		#print phB
		new_sentences = []
		for known_sentence in known_sentences:
			if phA in known_sentence:
				new_sentences += [known_sentence.replace(phA,phB)]
			elif phB in known_sentence:
				new_sentences += [known_sentence.replace(phB,phA)]
		known_sentences += new_sentences
		known_sentences = list(set(known_sentences))

	eng_sentences = []
	global lowerCase_eng_sentences
	#lowerCase_eng_sentences += [sen1.lower(), sen2.lower()]
	for known_sentence in known_sentences:
		for id in d_id2tok.keys():
			known_sentence = known_sentence.replace(id, d_id2tok[id])
		if(known_sentence.lower() not in lowerCase_eng_sentences):
			lowerCase_eng_sentences+= [known_sentence.lower()]
			eng_sentences += [known_sentence]

	eng_sentences = sorted(list(set(eng_sentences)))
	return eng_sentences[:]

#get all equiv sens from a list
def give_me_all_equiv_sentences(sens=[]):
	sens_prepped=get_prep(sens)
	sens_phrases=get_phrases(sens)
	#print sens_phrases
	all_result_sens=[]
	for i in range(len(sens)-1):
		for j in range(i+1,len(sens)):
			new_result=give_me_equiv_sentences(sens[i],sens[j],[sens_prepped[i],sens_prepped[j]],[sens_phrases[i],sens_phrases[j]])
			all_result_sens+=new_result
	all_result_sens=process_sentences(all_result_sens)
	all_result_sens = filter(lambda x: x.lower() not in map(lambda y: y.lower(), sens), all_result_sens)
	return all_result_sens
			

