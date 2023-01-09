from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForTokenClassification
import huggingface_hub
import numpy as np
import nltk
from utils import get_ref, get_text_from_uri
from ned import expanded_symp, is_exist_ss, symp_syn
from text_similarity import is_exist_es

# download dependencies for nltk library
nltk.download('wordnet') # get synonyms
nltk.download('omw-1.4')
nltk.download('stopwords') # stop words
nltk.download('punkt') # tokenizer

# download named entity recognition model
tokenizer = AutoTokenizer.from_pretrained("d4data/biomedical-ner-all")
bme = AutoModelForTokenClassification.from_pretrained("d4data/biomedical-ner-all")
ner = pipeline("ner", model=bme, tokenizer=tokenizer, aggregation_strategy="simple")

# download text-similarity model
tsm = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# download sematic-similarity model
ssm = huggingface_hub.from_pretrained_keras("keras-io/bert-semantic-similarity")

# load part-of-speech tagger model
# pos_tagger = joblib.load("./data/pos-tagger.joblib")

def intialize_linker():
    # Append all the symptoms and their synonyms
    for s,p,o in g: # subject, predicate, object
        # filter synonyms
        if p == get_ref("hasSymptom"):
            try:
                x = get_text_from_uri(o).toPython()
            except:
                continue
            curr_symp_syn = []
            for s1, p1, o1 in g:
                # filter synonym for above "o" entity
                if s1 == o and p1 == get_ref("hasSynonym"):
                    try:
                        y = get_text_from_uri(o1).toPython()
                        curr_symp_syn.append(y)                    
                    except:
                        continue
            # validate to add only one entry
            if not is_exist_ss(x):
                try:
                    idx = o.toPython()
                    symp_syn.append((idx, x, curr_symp_syn))
                except:
                    continue

    for idx,word,syns in symp_syn:
        for s in syns:
            if not is_exist_es(s, expanded_symp):
                expanded_symp.append((idx, s))
        if not is_exist_es(word, expanded_symp):
            expanded_symp.append((idx, word))