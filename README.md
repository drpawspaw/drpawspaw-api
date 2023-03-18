# drpawspaw-api
REST API service for drpawspaw.com

## CURL Requests

### Pets

1. Create pet's profile
```
curl --location 'http://localhost:8000/api/v1/pets' \
--header 'Content-Type: application/json' \
--data '{
    "name": "Tyson",
    "birthdate": "2023-02-02T06:50:04.254+00:00",
    "lastVaccination": "Parvo",
    "lastVaccinationDate": "2023-03-22T06:50:04.254+00:00",
    "bread": "Shitzu",
    "category": "dog"
}'
```