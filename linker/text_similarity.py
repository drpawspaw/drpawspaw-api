from nltk.corpus import wordnet
from sentence_transformers import SentenceTransformer, util
from setup import tsm

def generate_synonyms(uri, keyword, syns):
    for synonym in wordnet.synsets(keyword):
        for item in synonym.lemmas():
            if keyword != synonym.name() and len(synonym.lemma_names()) > 1:
                syns.append(item.name())
    return (uri, keyword, syns)

def is_exist_es(keyword, collection):
    for _,word in collection:
        if keyword == word:
            return True

# Calculate the similariity
# Here "tsm" means the text-similarity-model, that we loaded in "Load required pre-trained models"
# "get_similarity" accepts the URI, identified named entity, entity from ontology
def get_similarity(idx, word, ne): # Return a tuple, contain URI, node, similarity_score
    embedding_1 = tsm.encode(ne, convert_to_tensor=True)
    embedding_2 = tsm.encode(word, convert_to_tensor=True)
    return (idx, word, util.pytorch_cos_sim(embedding_1, embedding_2))

# At the current implementation, we only get first five entities
# "entity" - identified named entity, "nodes" - named entities in the onotology (in format of [(idx, text)])
def get_most_similarity_entities(entity, nodes):
  scores = map(lambda e: get_similarity(e[0], e[1], entity), nodes)
  return sorted(list(scores), key=lambda x:x[2], reverse=True)[:5]