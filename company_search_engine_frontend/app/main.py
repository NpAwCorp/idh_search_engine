import streamlit as st
import requests
import json
import io
import base64
import pandas as pd
import validators

df = pd.read_csv("countries.csv")

def search_backend(company, country, website):
    import streamlit as st
    
    if company == "":
        st.text("Please enter a company name")

    elif website != "" and not validators.url(website):
        st.warning(f"Your website {website} is not in correct format. Please make sure that it is in full URL format. [e.g.] https://www.google.com, https://www.adidas.de or https://www.eikonnex.ai")
    else:
        with st.spinner('Please Wait...'):
            response = requests.post("http://backend:8000/api/search",json={"company" : company, "country" : country, "website" : website}, timeout=120)

        # Product/service, Keywords, SIC, NAICS, image
        resp_json = response.json()
        if "error" in resp_json:
            st.text(resp_json["error"])
        elif response.status_code == 200:
            if resp_json != {}:
                if "description" in resp_json:
                    st.header('Company description')
                    try:
                        resp_json["description"]
                    except:
                        pass
                if "Product/service_category" in resp_json and len(resp_json["Product/service_category"]) > 0:
                    st.header('Products and Services')
                    for ele in resp_json["Product/service_category"]:
                        try:
                            st.markdown("* "+ele)
                        except:
                            continue
                if "Keywords" in resp_json and len(resp_json["Keywords"]) > 0:
                    st.header('Keywords')
                    for ele in resp_json["Keywords"]:
                        try:
                            st.markdown("* "+ele)
                        except:
                            continue
                if "SIC" in resp_json and len(resp_json["SIC"]) > 0:
                    st.header('SIC codes')
                    for ele in resp_json["SIC"]:
                        try:
                            st.text("* "+str(ele["code"]) + " - " + ele["description"])
                        except:
                            continue
                if "NAICS" in resp_json and len(resp_json["NAICS"]) > 0:
                    st.header('NAICS codes')
                    for ele in resp_json["NAICS"]:
                        try:
                            st.text("* "+str(ele["code"]) + " - " + ele["description"])
                        except:
                            continue
                if "image" in resp_json and len(resp_json["image"]) > 0:
                    st.header('Products/Services images')
                    for ele in resp_json["image"]:
                        try:
                            st.image(io.BytesIO(base64.b64decode(ele)))
                        except:
                            continue
        elif response.status_code == 401:
            st.warning(resp_json['detail']['desc'], icon="⚠️")
        else:
            st.warning("An unexpected error occurs. Please try again")

company_input = st.sidebar.text_input("Company name")

country_input = st.sidebar.selectbox('Country',pd.concat([pd.Series(['']), df["name"]], ignore_index=True))

website_input = st.sidebar.text_input("Website")

if st.sidebar.button("Search"):
    search_backend(company_input, country_input, website_input)