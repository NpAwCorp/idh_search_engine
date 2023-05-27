# company_search_engine

## Pre-requisite
1. Docker
2. OpenAI API key

## Step to install and run
Run the following command to build and start the service:
```
docker-compose up --build -d
```
**remark** : If you only need to access an API endpoint, the API service is available at localhost:8000

## API Endpoint
- The service provides a single endpoint to use : http://localhost:8000/api/search
- Once the service is started, you can access the Swagger UI at  http://localhost:8000/api/docs

## Frountend
- Once the service is started, the frontend web application will be accessible at http://localhost:8501
**We strongly recommend testing via our frontend web application for the best experience.**

## Invoke an endpoint using python
If you need to access the API directly without using our frontend, you can use the following code in Python:
# python
```
import requests

response = requests.post("http://localhost:8000/api/search", json={"company": "<company>", "country": "<country>", "website": "<website [OPTIONAL]>")
print(response.json())
```
# curl
```
curl -X 'POST' 'http://localhost:8000/api/search' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "company": "<company>",
  "country": "<country>",
  "website": "<website [OPTIONAL]>"
}'
```
