from rdflib import URIRef
from linker.model import g

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

# Get URI from text
def get_uri_from_text(text):
  for s, p, o in g:
    if p == URIRef("https://ontology.drpawspaw.com/text"):
      if o.toPython().lower() == text.lower():
        return s
  return None

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

# Helper functions to define the properties of the pos-tagger model
def features(sentence, index):
    return {
        'word': sentence[index],
        'is_first': index == 0,
        'is_last': index == len(sentence) - 1,
        'is_capitalized': sentence[index][0].upper() == sentence[index][0],
        'is_all_caps': sentence[index].upper() == sentence[index],
        'is_all_lower': sentence[index].lower() == sentence[index],
        'prefix-1': sentence[index][0],
        'prefix-2': sentence[index][:2],
        'prefix-3': sentence[index][:3],
        'suffix-1': sentence[index][-1],
        'suffix-2': sentence[index][-2:],
        'suffix-3': sentence[index][-3:],
        'prev_word': '' if index == 0 else sentence[index - 1],
        'next_word': '' if index == len(sentence) - 1 else sentence[index + 1],
        'has_hyphen': '-' in sentence[index],
        'is_numeric': sentence[index].isdigit(),
        'capitals_inside': sentence[index][1:].lower() != sentence[index][1:]
    }