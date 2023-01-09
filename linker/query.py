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