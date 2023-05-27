import requests
from bs4 import BeautifulSoup
import base64
import re
import urllib

def company_image_search(company:str = "innoscripta", country:str = "Germany", img_limit:str = "5"):
    img_limit = int(img_limit)
    country_ = country.lower()
    q_text = f"{company} {country_} products | services picture"
    q_parse = urllib.parse.quote(q_text)
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}
    target_url=f"https://www.bing.com/images/search?q={q_parse}&first=1"
    resp=requests.get(target_url,headers=headers)
    
    imgs = re.findall('murl&quot;:&quot;(.*?)&quot;', resp.text)
    pic_count = 0
    resp_pics = []
    company_1st_token = company.split()[0].lower()
    for img in imgs:
        if pic_count < img_limit:
            if company_1st_token not in img.lower():
                continue
            try:
                resp = requests.get(img, headers=headers, timeout=1)
                if resp.status_code == 200:
                    resp_pics.append(base64.b64encode(resp.content))
                    pic_count += 1
            except:
                pass
        else:
            break
    return resp_pics