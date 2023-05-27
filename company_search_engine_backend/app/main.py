from fastapi import FastAPI
import asyncio
import uvicorn
from utils.translator import EasyGoogleTranslate
import json
import requests
from utils.gpt_search import gpt_search
from utils.bing import company_image_search
from structure import SearchRequest

app = FastAPI(title="Data Search API Gateway" ,docs_url='/api/docs', openapi_url='/api/openapi.json')

async def image_search(company, country):
    return company_image_search(company, country)

@app.post("/api/search")
async def search_v2(request: SearchRequest):
    task_one = asyncio.create_task(image_search(request.company, request.country))
    task_two = asyncio.create_task(search(request))
    result_one, result_two = await asyncio.gather(task_one, task_two)
    result_two.update({"image" : result_one})
    return result_two

async def search(request: SearchRequest, debug=False):
    result = gpt_search.search_from_company_html(request.company, request.country, request.website)
    if "error" in result:
        return result
    if result == {} or result['Product/service_category'][0] == None:
        return {}
    if debug:
        print(f"Input data : {request.company} | {request.country} | {request.website}")
        print(result)
    sic_naics = gpt_search.codes_from_prodserv(str(result['Product/service_category']))
    result.update(sic_naics)
    return result