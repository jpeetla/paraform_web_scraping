from bs4 import BeautifulSoup
import requests
import api_queries

def waterfall_find_executives(company_name):
    about_urls = api_queries.find_about_page(company_name)
    for url in about_urls:
        executives = api_queries.clean_and_query_about_page(url)
        if executives:
            return executives  

    linkedin_urls = api_queries.find_linkedin_profiles(company_name)
    for url in linkedin_urls:
        executives = api_queries.clean_and_query_about_page(url)
        if executives:
            return executives 

    executives = api_queries.find_executives_with_apollo(company_name)
    if executives:
        return executives
    
    return "No Executives Found"

company_name = "280 Earth"
executives = waterfall_find_executives(company_name)

