from sentence_transformers import SentenceTransformer, util
from rdflib import Graph, Namespace, Literal, RDF, URIRef
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForTokenClassification
from huggingface_hub import from_pretrained_keras
from nltk.corpus import stopwords
from linker.utils import get_ref, is_exist_es, is_exist_ss, get_text_from_uri, build_query, features
from linker.model import g, pos_tagger, ssm, tsm
import tensorflow as tf
import transformers
import numpy as np
import nltk
import os

# Define the tensorflow logger levels
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

word_join_character = " "  # Use to join the words in an array
stop_words = stopwords.words("english")
labels = ["negative_similarity", "positive_similarity", "neutral"]

# List of synonyms and symptoms as one single object
expanded_symp = []

# List of symptoms and their synonyms
symp_syn = []

def init_cfg():
    # Append all the symptoms and their synonyms
    for s, p, o in g:  # subject, predicate, object
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
            if not is_exist_ss(x, symp_syn):
                try:
                    idx = o.toPython()
                    symp_syn.append((idx, x, curr_symp_syn))
                except:
                    continue
    # Expand the entities with synonyms and URIs
    for idx, word, syns in symp_syn:
        for s in syns:
            if not is_exist_es(s, expanded_symp):
                expanded_symp.append((idx, s))
        if not is_exist_es(word, expanded_symp):
            expanded_symp.append((idx, word))

# Entity linker component - This function accepts the sentence as string and return the predicted values
def entity_linker(sentence):
    etq = []  # Entities to query
    # annotate_tokens = ner(word_join_character.join(
    #     [token for token in nltk.word_tokenize(sentence) if token.lower() not in stop_words]
    # ))
    # annotate_entity = [en['word'] for en in annotate_tokens
    #                    if en['entity_group'] == "Sign_symptom" and en['score'] > 0.75]
    
    # Tokenize the sentence
    tokens = nltk.word_tokenize(sentence)

    # Remove stop words, (stopwords are getting fromt the NLTK library)
    filtered_tokens = [token for token in tokens if token.lower() not in stop_words]

    # Filtered tokens as sentence
    filtered_user_input = " ".join(filtered_tokens)

    annotated_entites = [en for en in list(
        pos_tag(nltk.word_tokenize(filtered_user_input)) # Filter entities annotate as "SYMPTOM"
    ) if en[1] == "SYMPTOM"]
    
    for e in annotated_entites:
        current_entity_candidates = get_most_similarity_entities(e[0], expanded_symp)
        etq.append(get_highest_ctx_similarity(e[0], current_entity_candidates))
    current_query = build_query(list(map(lambda x: x[0][0], etq)))
    return [rq for rq in g.query(current_query)]


# Part-of-Speech tagger, this will annotate the named entities
def pos_tag(sentence):
    tags = pos_tagger.predict([features(sentence, index) for index in range(len(sentence))])
    return zip(sentence, tags)


# "get_highest_ctx_similarity" function return the highest context similarity as tuple (URI, Word, ctx_similarity)
def get_highest_ctx_similarity(entity, nodes):
    scores = map(lambda e: calculate_semantic_similarity(e[0], e[1], entity), nodes)
    return sorted(list(scores), key=lambda x: x[2], reverse=True)[:1]


# Calculate the semantic similarity of the identified entity and nodes in ontology
# "calculate_semantic_similarity" functions accepts, the URI, text and identified entity
def calculate_semantic_similarity(uri, ctx, entity):
    sentence_pairs = np.array([[str(entity), str(ctx)]])
    test_data = BertSemanticDataGenerator(
        sentence_pairs, labels=None, batch_size=1, shuffle=False, include_targets=False,
    )
    probs = ssm.predict(test_data[0])[0]
    labels_probs = {labels[i]: float(probs[i]) for i, _ in enumerate(labels)}
    return (uri, ctx, labels_probs["positive_similarity"])


# At the current implementation, we only get first five entities
# "entity" - identified named entity, "nodes" - named entities in the onotology (in format of [(idx, text)])
def get_most_similarity_entities(entity, nodes):
    scores = map(lambda e: get_similarity(e[0], e[1], entity), nodes)
    return sorted(list(scores), key=lambda x: x[2], reverse=True)[:5]


# Calculate the similarity
# Here "tsm" means the text-similarity-model, that we loaded in "Load required pre-trained models"
# "get_similarity" accepts the URI, identified named entity, entity from ontology
def get_similarity(idx, word, ne):  # Return a tuple, contain URI, node, similarity_score
    embedding_1 = tsm.encode(ne, convert_to_tensor=True)
    embedding_2 = tsm.encode(word, convert_to_tensor=True)
    return (idx, word, util.pytorch_cos_sim(embedding_1, embedding_2))

# BertSemanticDataGenerator to calculate the similarity between two words
# In here, we are taking the context similarity not the word/text similarity
class BertSemanticDataGenerator(tf.keras.utils.Sequence):
    """Generates batches of data."""

    def __init__(
            self,
            sentence_pairs,
            labels,
            batch_size=32,
            shuffle=True,
            include_targets=True,
    ):
        self.sentence_pairs = sentence_pairs
        self.labels = labels
        self.shuffle = shuffle
        self.batch_size = batch_size
        self.include_targets = include_targets
        # Load our BERT Tokenizer to encode the text.
        # We will use base-base-uncased pretrained model.
        self.tokenizer = transformers.BertTokenizer.from_pretrained(
            "bert-base-uncased", do_lower_case=True
        )
        self.indexes = np.arange(len(self.sentence_pairs))
        self.on_epoch_end()

    def __len__(self):
        # Denotes the number of batches per epoch.
        return len(self.sentence_pairs) // self.batch_size

    def __getitem__(self, idx):
        # Retrieves the batch of index.
        indexes = self.indexes[idx * self.batch_size: (idx + 1) * self.batch_size]
        sentence_pairs = self.sentence_pairs[indexes]

        # With BERT tokenizer's batch_encode_plus batch of both the sentences are
        # encoded together and separated by [SEP] token.
        encoded = self.tokenizer.batch_encode_plus(
            sentence_pairs.tolist(),
            add_special_tokens=True,
            max_length=128,
            return_attention_mask=True,
            return_token_type_ids=True,
            pad_to_max_length=True,
            return_tensors="tf",
        )

        # Convert batch of encoded features to numpy array.
        input_ids = np.array(encoded["input_ids"], dtype="int32")
        attention_masks = np.array(encoded["attention_mask"], dtype="int32")
        token_type_ids = np.array(encoded["token_type_ids"], dtype="int32")

        # Set to true if data generator is used for training/validation.
        if self.include_targets:
            labels = np.array(self.labels[indexes], dtype="int32")
            return [input_ids, attention_masks, token_type_ids], labels
        else:
            return [input_ids, attention_masks, token_type_ids]

# Initialize the configurations
init_cfg()