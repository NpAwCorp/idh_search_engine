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

## OpenAI API key
- For the time being, we will provide you with our API key, which has a usage limit of 250 credits per day.
- If you would like to use your own API key or if you need to make further improvements, you can update the key in the configuration file located at company_search_engine_backend/app/config.json.
- In the config.json file, you can modify the values for "api_key" and "api_base" to use your own key and customize the API base URL accordingly.
Please note that updating the API key and base URL in the configuration file allows you to use your own OpenAI API key and configure the API endpoint as per your requirements.

If you have any additional questions, feel free to contact us via email : annop.watth@gmail.com or natchapon.p1997@gmail.com

## API Endpoint
- The service provides a single endpoint to use : http://localhost:8000/api/search
- Once the service is started, you can access the Swagger UI at  http://localhost:8000/api/docs

## Frontend
- Once the service is started, the frontend web application will be accessible at http://localhost:8501
**We strongly recommend testing via our frontend web application for the best experience.**

## Invoke an endpoint
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
