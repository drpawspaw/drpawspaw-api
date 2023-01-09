from sentence_transformers import SentenceTransformer, util
from rdflib import Graph, Namespace, Literal, RDF, URIRef
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForTokenClassification
from huggingface_hub import from_pretrained_keras
import numpy as np
import transformers
from nltk.corpus import stopwords
import tensorflow as tf
import nltk

# Download required NLTK libraries and files
nltk.download('wordnet')  # get synonyms
nltk.download('omw-1.4')
nltk.download('stopwords')  # stop words
nltk.download('punkt')  # tokenizer

# Load ontology graph
g = Graph()
g.parse("/data/adso.owl")

# Named entity recognition model
tokenizer = AutoTokenizer.from_pretrained("d4data/biomedical-ner-all")
bme = AutoModelForTokenClassification.from_pretrained("d4data/biomedical-ner-all")
ner = pipeline("ner", model=bme, tokenizer=tokenizer, aggregation_strategy="simple")

# Text similarity model
tsm = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Semantic similarity model
ssm = from_pretrained_keras("keras-io/bert-semantic-similarity")

word_join_character = " "  # Use to join the words in an array
stop_words = stopwords.words("english")
labels = ["negative_similarity", "positive_similarity", "neutral"]

# Expand the all entities
expanded_symp = []

# List of symptoms and their synonyms
symp_syn = []


# Get the URIRef for given keyword
def get_ref(keyword):
    return URIRef("https://ontology.drpawspaw.com/" + keyword)


# Check the keyword already exist or not in collection
def is_exist_ss(keyword):
    for _, k, _ in symp_syn:
        if k == keyword:
            return True


# Get the entity 'text' from the URIRef
def get_text_from_uri(uri):
    for s, p, o in g:
        if s == uri and p == URIRef("https://ontology.drpawspaw.com/text"):
            return o


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
        if not is_exist_ss(x):
            try:
                idx = o.toPython()
                symp_syn.append((idx, x, curr_symp_syn))
            except:
                continue


def is_exist_es(keyword):
    for _, entity in expanded_symp:
        if keyword == entity:
            return True


for idx, word, syns in symp_syn:
    for s in syns:
        if not is_exist_es(s):
            expanded_symp.append((idx, s))
    if not is_exist_es(word):
        expanded_symp.append((idx, word))


def entity_linker(sentence):
    etq = []  # Entities to query
    annotate_tokens = ner(word_join_character.join(
        [token for token in nltk.word_tokenize(sentence) if token.lower() not in stop_words]
    ))
    annotate_entity = [en['word'] for en in annotate_tokens
                       if en['entity_group'] == "Sign_symptom" and en['score'] > 0.75]
    for e in annotate_entity:
        current_entity_candidates = get_most_similarity_entities(e, expanded_symp)
        etq.append(get_highest_ctx_similarity(e, current_entity_candidates))
    current_query = build_query(list(map(lambda x: x[0][0], etq)))
    return [rq for rq in g.query(current_query)]


# This function return SPARQL query, that able to get the disease from symptoms
def build_query(symptoms):
    return """
    PREFIX adso: <https://ontology.drpawspaw.com/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?diseaseName
    WHERE {{
        {sym_query}
        ?diseaseUri adso:text ?diseaseName .
    }}
    """.format(sym_query="\n".join(
        list(
            map(lambda e: "?diseaseUri adso:hasSymptom adso:{uri} .".format(uri=e),
                list(map(lambda e: e.split("/")[3], symptoms))))))


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


# Help utils for semantic similarity model
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

# TODO: (Remove) Tryout Implementation
print("Prediction: ", entity_linker("My dog has been vomiting and has diarrhea"))
