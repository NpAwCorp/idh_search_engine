import openai
import re
import requests
import json
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.parse
import urllib.request
from utils.translator import EasyGoogleTranslate
from openai.error import APIConnectionError, APIError, InvalidRequestError
from fastapi import HTTPException
from tldextract import TLDExtract

cfg = json.load(open("config.json"))
openai.api_key = cfg["api_key"]
openai.api_base = cfg["api_base"]

class GPTSearch():
    def __init__(self, model="text-davinci-003"):
        self.model = model
    
    def search_based_gpt(self, company, country, list_limit="ten"):
        response = openai.Completion.create(
            model= self.model,
            prompt=f"What are the product/services that {company} from {country} offers? Answer me in JSON format which each answer in list not contain more than {list_limit} "+ 'elements => { "Product/service" : [ <answer>, ..., <answer>] , "Keywords"  : [ <answer>, ..., <answer>], "SIC":[{"code":<answer>,...}], "NAICS":[{"code":<answer>,...}], "status" : <"success" or "fail">}. If unable to answer or cannot find relevant info. please preserve this format, add null to all except status which should be "fail". Need ONLY requested JSON',
            temperature=0.2,
            max_tokens=2000,
            ) 
        return response

    def gpt_sic_naics(self, prodserv_str_list):
        response = openai.Completion.create(
            model= self.model,
            prompt=f"specify SIC and NAICS codes from this list {prodserv_str_list}, elements in both list must be limited to 5" +' and summarize to this json => { "SIC" : [ { "code":<answer> , "description" : <answer> } , ... ], "NAICS" : [ { "code":<answer> , "description" : <answer> } ] , ... }, "status" : <"success" or "fail"> }. If unable to answer or cannot find relevant info. please preserve this format, add null to all except status which should be "fail". Need ONLY requested JSON',
            temperature=0.2,
            max_tokens=1024,
            )       
        return response

    def gpt_sic_only(self, prodserv_str_list):
        response = openai.Completion.create(
            model= self.model,
            prompt=f"specify SIC codes from this list {prodserv_str_list}, elements in both list must be limited to 5" +' and summarize to this json => { "SIC" : [ { "code":<answer> , "description" : <answer> } , ... ], "status" : <"success" or "fail"> }. If unable to answer or cannot find relevant info. please preserve this format, add null to all except status which should be "fail". Need ONLY requested JSON',
            temperature=0.2,
            max_tokens=1024,
            )     
        return response

    def gpt_naics_only(self, prodserv_str_list):
        response = openai.Completion.create(
            model= self.model,
            prompt=f"specify NAICS codes from this list {prodserv_str_list}, elements in both list must be limited to 5" +' and summarize to this json => { "NAICS" : [ { "code":<answer> , "description" : <answer> } ] , ... }, "status" : <"success" or "fail"> }. If unable to answer or cannot find relevant info. please preserve this format, add null to all except status which should be "fail". Need ONLY requested JSON',
            temperature=0.2,
            max_tokens=1024,
            )
        return response

    def codes_from_prodserv(self, prodserv_str_list):
        response = self.gpt_sic_naics(prodserv_str_list)
        if 'error' in response:
            print("[X]GPT ERROR : Retry 1 time")
            response = self.gpt_sic_naics(prodserv_str_list)
        if 'error' in response:
            return {'SIC': [], 'NAICS': []}
        try: # To handle maxmimum token problem from gpt
            result = json.loads("{" + response.choices[0].text.split("{",1)[-1])
        except: 
            # If it meet the problem, imply that by generating both sic and naics may too long
            # Thus, by asking gpt seperate may solve the problem
            result = {'SIC':[], 'NAICS': []}
            response_sic = self.gpt_sic_only(prodserv_str_list)
            if 'error' not in response_sic:
                try:
                    sic_dict = json.loads("{" + response_sic.choices[0].text.split("{",1)[-1])
                except:
                    sic_dict = {'SIC': []}
                result.update(sic_dict)
            response_naics = self.gpt_naics_only(prodserv_str_list)
            if 'error' not in response_naics:
                try:
                    naics_dict = json.loads("{" + response_naics.choices[0].text.split("{",1)[-1])
                except:
                    naics_dict = {'NAICS': []}
                result.update(naics_dict)
        return result
    
    def search_from_company_html(self, company, country, website = ""):
        result = {}
        result_desc = {}
        if website == "":
            url = company_official_web_search(company, country)
        else:
            extractor = TLDExtract()
            split_url = urllib.parse.urlsplit(website)
            split_suffix = extractor.extract_urllib(split_url)
            url = f"{split_url.scheme}://{split_suffix.registered_domain}"

        web = about_company_from_web(url)
        if web[-4:] == ".pdf":
            web = about_company_from_web(url, exclude_pdf = True)
        headers = {"User-Agent":"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}
        print("[X]About URL : ", web)
        try: 
            html_resp = requests.get(web,headers=headers,timeout=10)
        except:
            print("[X]Something wrong with the request")
            print("[X]Try again with next index URL")
            url = company_official_web_search(company, country, 1)
            web = about_company_from_web(url)
            print("[X]About URL : ", web)
            try:
                html_resp=requests.get(web,headers=headers,timeout=10)
            except:
                return {}
        html_text = text_from_html(html_resp.text)
        if html_text != "":
            clean_pattern = re.compile(r'\s+')
            clean_sentence = re.sub(clean_pattern, ' ', html_text).strip()
        else:
            clean_sentence = html_resp.text

        translator = EasyGoogleTranslate(
            target_language="en",
            timeout=10
        )
        try:
            en_sentence = translator.translate(clean_sentence[:2000])
        except:
            en_sentence = translator.translate(clean_sentence[:1000])

        for lim in [2000,1000,500]:
            try: # To handle maxmimum token problem from gpt
                result = self.prod_serv_keyword(en_sentence, lim)
                break
            except (APIConnectionError, APIError, InvalidRequestError) as e:
                raise HTTPException(status_code=401, 
                                    detail={'desc':'Invalid OpenAI API key. Please contact us via email : annop1765@gmail.com',
                                            'exception': str(e)}
                                    )
        for lim in [2000,1000,500]:
            try: # To handle maxmimum token problem from gpt
                result_desc = {"description" : self.company_description(en_sentence, lim)}
                break
            except:
                pass
        result.update(result_desc)
        return result
    
    def prod_serv_keyword(self,sentence, limit=2000, list_limit="ten"):
        response = openai.Completion.create(
            model= self.model,
            prompt=f"According to this company information '{sentence[:limit]}' what are their offered product/services (answer in categories) and product keywords, generate the specified JSON format and number of answers in both keys should be limited to {list_limit}" + ' elements => { "Product/service_category" : [ <answer>, ..., <answer>] , "Keywords"  : [ <answer>, ..., <answer>], "status" : <"success" or "fail">}. If unable to answer or cannot find relevant info. please preserve this format, add null to all except status which should be "fail". Need ONLY requested JSON',
            temperature=0.2,
            max_tokens=1024
            )
        return json.loads("{" + response.choices[0].text.split("{",1)[-1])
    
    def company_description(self,sentence, limit=2000):
        response = openai.Completion.create(
            model= self.model,
            prompt=f"According to this company information '{sentence[:limit]}' Please describe this company",
            temperature=0.2,
            max_tokens=1024
            )
        return response.choices[0].text.strip()

def company_web_search(company, country):
    country_ = country.lower()
    q_text = f"{company} {country_} about products and services"
    q_parse = urllib.parse.quote(q_text)
    headers={"User-Agent":"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}
    target_url=f"https://www.bing.com/search?q={q_parse}&rdr=1&first=1"
    resp=requests.get(target_url,headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    completeData = soup.find_all("li",{"class":"b_algo"})
    for i in range(len(completeData)):
        result = completeData[i].find("a").get("href")
        if result != None:
            break
    return result

def company_official_web_search(company, country, num = 0):
    country_ = country.lower()
    if "linkedin" not in company.lower():
        q_text = f"{company} {country_} corporate website -site:linkedin.com"
    else:
        q_text = f"{company} {country_} corporate website"
    q_parse = urllib.parse.quote(q_text)
    headers={"User-Agent":"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}
    target_url=f"https://www.bing.com/search?q={q_parse}&rdr=1&first=1"
    resp=requests.get(target_url,headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    completeData = soup.find_all("li",{"class":"b_algo"})
    # print(completeData)
    for i in range(num,len(completeData)):
        result = completeData[i].find("a").get("href")
        if result != None:
            break
    return re.sub(result.replace("https://", "").replace("http://", "").split('/',1)[1], "", result)

def about_company_from_web(url, exclude_pdf = False):
    q_text = f"site:{url} (about products and services)"
    if exclude_pdf:
        q_text = q_text + " -filetype:pdf"
    q_parse = urllib.parse.quote(q_text)
    headers={"User-Agent":"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}
    target_url=f"https://www.bing.com/search?q={q_parse}&rdr=1&first=1"
    resp=requests.get(target_url,headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    completeData = soup.find_all("li",{"class":"b_algo"})
    if len(completeData) == 0:
        return url
    for i in range(len(completeData)):
        result = completeData[i].find("a").get("href")
        if result != None:
            break
    return result
    
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

gpt_search = GPTSearch()
