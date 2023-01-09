from rdflib import URIRef
from model import g

# This function return SPARQL query, 
# That able to get the disease from symptoms
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

# Get the entity 'text' from the URIRef
def get_text_from_uri(uri):
    for s, p, o in g:
        if s == uri and p == URIRef("https://ontology.drpawspaw.com/text"):
            return o

# Get the URIRef for given keyword
def get_ref(keyword):
    return URIRef("https://ontology.drpawspaw.com/" + keyword)

# Check the keyword already exist or not in collection
def is_exist_ss(keyword, collection):
    for _, k, _ in collection:
        if k == keyword:
            return True

# Check the keyword exist or not
def is_exist_es(keyword, collection):
    for _, entity in collection:
        if keyword == entity:
            return True