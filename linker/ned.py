from rdflib import Graph, Namespace, Literal, RDF, URIRef
from nltk.corpus import stopwords
from utils import get_text_from_uri, get_ref

# Define ontology path name
DATA_SOURCE = "../data/adso.owl"

# Collect named entities from ontology
diseases = []
symptoms = []
synonyms = []

# List of symptoms and their synonyms
symp_syn = []

# Exapand the all entities
expanded_symp = []

# Define stop words from NLTK package
stop_words = stopwords.words('english')

# Initialize and load ontology
g = Graph()
g.parse(DATA_SOURCE)

# Function initialize the ontology named entities before execution
def initialize_entities():
    for s,p,o in g:
        if p == get_ref("hasDisease"):
            try:
                dis = get_text_from_uri(o).toPython()
                diseases.append(dis)
            except:
                print(type(o), o)
        if p == get_ref("hasSymptom"):
            try:
                sym = get_text_from_uri(o).toPython()
                symptoms.append(sym)
            except:
                print(type(o), o)
        if p == get_ref("hasSynonym"):
            try:
                syn = get_text_from_uri(o).toPython()
                synonyms.append(syn)
            except:
                print(type(o), o)

# Check the keyword already exist or not in collection
def is_exist_ss(keyword):
    for _,k,_ in symp_syn:
        if k == keyword:
            return True