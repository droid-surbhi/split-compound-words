import json
import re
from typing import List, Tuple

import numpy as np
import spacy
from googletrans import Translator

translator = Translator()
nlp1 = spacy.load('en_vectors_web_lg')
eng_words = json.load(open('eng_words.json', 'r'))
common_words = json.load(open('common_words.json', 'r'))


def sentence_to_words(sentence: str, preferred_words: List[str]=[], translate:bool = False, use_common: bool = True,
                      top_limit: int = 0) -> dict:
    """
    use this function to tokenize sentences which have compound words.

    Parameters:
    ----------
    sentence: str
        input string to be tokenized
    
    preferred_words: list
        list of preferred words, useful when some words are more likely to occur in input text, 
        e.g. 'together' can be 'to get her' combined. Giving 'together' in this list will make sure it doesn't split further
        If not using this, can remove spacy
    
    translate: bool
        if giving non-english words as input, then translation is required
    
    use_common: bool
        if true, returns only the combinations of words which are common in English, else returns all valid ones.
    
    top_limit: int
        if 0, returns all found valid combinations else only top 'top_limit' number of combinations.

    Returns:
    --------
    result: dict with key as word and value as possible combinations of words for that key
            e.g: 'sorttimetogether kid' => {'sorttimetogether': [('sort', 'time', 'together'),
                                            ('sort', 'time', 'to', 'get', 'her')], 'kid': ['kid']}
    """
    # tokenize the sentence using delimiters
    phrases = re.split('[ -/(,)&$%#@!]+', sentence)
    phrases = [y.strip() for y in phrases if y.strip()!='']
   
    # for each token in phrases, find valid combinations of English words which can make the token 
    words = {}
    for i in range(len(phrases)):
        # translate to English
        if translate:
            try:
                phrases[i] = translator.translate(phrases[i]).text
            except: 
                pass
        
        if phrases[i] not in eng_words:     
            valid_parts = get_valid_parts(phrases[i], words)
            valid_parts = list(set([tuple(y) for y in valid_parts]))
            flag = False
            if use_common and len(valid_parts)>1:
                valid_parts = use_common_words(valid_parts)
                flag = True
            if preferred_words and len(valid_parts)>1:
                valid_parts = identify_preferred(valid_parts, preferred_words)
                flag = True
            if top_limit >0 and len(valid_parts)>top_limit:
                if not flag:
                    valid_parts = use_common_words(valid_parts, light=True)
                valid_parts = valid_parts[:top_limit]
        else:
            valid_parts = [(phrases[i])]
        words[phrases[i]] = valid_parts
    
    # filter required keys in dictionary
    result = {}
    for key in words:
        if key in phrases:
            result[key] = words[key]
    return result 


def identify_preferred(valid_parts: List[Tuple[str]], preferred_words: List[str]) -> List[Tuple[str]]:
    """
    return valid parts which have words from or are similar to words in the given list of words
    """

    # words in valid parts direclty match the words in the given list 
    selection = [(y, sum([x in preferred_words for x in y])) for y in valid_parts]
    selection = [y for y in selection if y[1]>0]
    selection = sorted(selection, key=lambda x: x[1], reverse=True)
    selection = [y[0] for y in selection]
    
    if len(selection) > 0:
        return selection
    
    # identify valid parts based on word similarity beteen words in the combination and in the given list
    else:
        max_sim = 0
        similarities = []
        for vec in range(len(valid_parts)):
            sim_vec = []
            for word in valid_parts[vec]:
                if sum(abs(nlp1.vocab[word].vector)) != 0:
                    sim = [nlp1.vocab[word].similarity(nlp1.vocab[preferred]) for preferred in preferred_words]
                    max_sim = max(sim)
                else:
                    max_sim = 0
                sim_vec.append(max_sim)
            similarity = np.mean(np.array(sim_vec))
            similarities.append(similarity)
        valid_parts = [(valid_parts[i], similarities[i]) for i in range(len(valid_parts))]
        valid_parts = sorted(valid_parts, key = lambda x: x[1], reverse=True)
        if valid_parts[0][1]>0:
            selection = [y[0] for y in valid_parts if y[1]>0]
        else:
            selection = [y[0] for y in valid_parts]
        return(selection) 



def use_common_words(decompounds: List[Tuple[str]], light: bool =False) -> List[Tuple[str]]:
    """
    identify decompounds which have common English words
    """
    candidates = []
    candidates_light = []
    for candidate in decompounds:
        inter = [y in common_words for y in candidate]
        if all(inter):
            candidates.append(candidate)
        if any(inter):
            candidates_light.append((candidate, sum(inter)/len(inter)))
    
    if not candidates or light:
        candidates = sorted(candidates_light, key=lambda x: x[1], reverse=True)
        candidates = [y[0] for y in candidates]
    if not candidates:
        candidates = decompounds
    return candidates   
    

def get_valid_parts(compound_word: str, saved_words: dict = {}) -> List[str]:
    """
    divide given compound word into list of valid words, 
    e.g.: straightline -> [straight, line]

    Parameters:
    ----------- 
    compound_word: str
        input word to  be processed
    saved_words: dict
        dictionary with keys as compound words and values as valid combinations of words

    Returns
    -------
    decompound: list of splitted words
    """
    # alreaady computed
    if compound_word in saved_words:
        return saved_words[compound_word]
    # all possible ways of splitting the word in 2 parts
    ngrams = [[compound_word[:i], compound_word[i:]] for i in range(1, len(compound_word))] 
    are_words = [[x in eng_words, y in eng_words] for x,y in ngrams]

    # if both parts are valid English words, then its most certain combination
    definite_parts = [ngrams[i] for i, y in enumerate(are_words) if y[0] and y[1]]   
    if len(definite_parts) > 0:
        saved_words[compound_word] = definite_parts
        return definite_parts
    else:
        # split the part further to match words in English dictionary
        possible_parts = [[(ngrams[i][0], y[0]), (ngrams[i][1], y[1])] for i, y in enumerate(are_words) if y[0] or y[1]]
        possible_parts = [y for y in possible_parts if not((len(y[0][0])==1 and not y[0][1]) or (len(y[1][0])==1 and not y[1][1]))]
        if len(possible_parts) == 0:
            return([[compound_word]])
    
        for i, pair in enumerate(possible_parts):
            #print(pair)
            if not pair[0][1]:
                instant = get_valid_parts(pair[0][0], saved_words=saved_words)
                #print(instant)
                all_instants = [y + [pair[1][0]] for y in instant]
                if all_instants:
                    definite_parts.extend(all_instants)
                
            elif not pair[1][1]:
                instant = get_valid_parts(pair[1][0], saved_words=saved_words)
                #print(instant)
                all_instants = [[pair[0][0]] + y for y in instant]
                if all_instants:
                    definite_parts.extend(all_instants)
    if not definite_parts:
        definite_parts = [[compound_word]]
    saved_words[compound_word] = definite_parts
    return definite_parts


if __name__=='__main__':
    print(sentence_to_words('sorttimetogether kid!', top_limit=10))