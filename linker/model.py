from sentence_transformers import SentenceTransformer
from rdflib import Graph, Namespace, Literal, RDF, URIRef
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForTokenClassification
from huggingface_hub import from_pretrained_keras

# Load ontology graph
g = Graph()
g.parse("../data/adso.owl")

# Named entity recognition model
tokenizer = AutoTokenizer.from_pretrained("d4data/biomedical-ner-all")
bme = AutoModelForTokenClassification.from_pretrained("d4data/biomedical-ner-all")
ner = pipeline("ner", model=bme, tokenizer=tokenizer, aggregation_strategy="simple")

# Text similarity model
tsm = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Semantic similarity model
ssm = from_pretrained_keras("keras-io/bert-semantic-similarity")