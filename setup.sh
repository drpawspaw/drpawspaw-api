#!/bin/sh

# Downlaod data sources from relavant repository
echo "--- Download animal disease symptom ontology ---"
curl -L "https://raw.githubusercontent.com/viraj-lakshitha/animal-disease-symptom-ontology/develop/ADSOv1.0.3.owl" --output "adso.owl"
mv adso.owl data

# Install python packages