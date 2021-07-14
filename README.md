## split_compound_words
#### Use this repository to split the compound words in a textline into a collection of dictionary words.
#### for e.g.: 
#### {'breakingnews': [('breaking', 'news')]}
#### {'steeringwheel': [('steering', 'wheel')]}
#### {'therabbithole': [('the', 'rabbit', 'hole'), ('th', 'era', 'bb', 'it', 'hole')]}

### Dependencies
Dependencies are listed in requirements.txt. You can install all requirements using:
``
pip install -r requirements.txt
``
> If using spacy, download its model like this: ``python -m spacy download en_vectors_web_lg``

### How to use it

    decompound.sentence_to_words(sentence: str, preferred_words: List[str]=[], translate:bool = False, use_common: bool = True,
                      top_limit: int = 0) -> dict
  
    Use this function to tokenize sentences which have compound words.

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
 
    
### Examples:
##### > To get all possible combinations of common English dictionary words forming the given word:
####
     
    import decompound
    decompound.sentence_to_words('sorttimetogether kid!')
    
##### output: {'sorttimetogether': [('sort', 'time', 'together'), ('sort', 'time', 'to', 'get', 'her')], 'kid': ['kid']}
##### > To get all possible combinations of all English Dictionary words forming the given word:
#####
     sentence_to_words('youaregreat', use_common=False)
##### output: {'youaregreat': [('you', 'are', 'great'), ('you', 'a', 'reg', 're', 'at')]}
##### > To get top 1 or n combination(s) of English dictionary words for the given word:
#####
      sentence_to_words('forgetthatpage', top_limit=1)
##### all combinations: {'forgetthatpage': [('forget', 'that', 'page'), ('for', 'get', 'that', 'page')]}
##### output: {'forgetthatpage': [('forget', 'that', 'page')]}
##### > If you have a list of preferred words e.g. high-frequency words in your data, can pass that in ''preferred_words' argument to get only those sets of combinations which have words from the given list, if  possible.
      

      
    
