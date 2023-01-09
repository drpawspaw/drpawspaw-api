from rdflib import Graph, Namespace, Literal, RDF, URIRef

# Get the URIRef for given keyword
def get_ref(keyword):
    return URIRef("https://ontology.drpawspaw.com/"+keyword)

# Get the entity 'text' from the URIRef
def get_text_from_uri(uri):
    for s,p,o in g:
        if s == uri and p == URIRef("https://ontology.drpawspaw.com/text"):
            return o