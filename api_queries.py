from openai import OpenAI
from serpapi import GoogleSearch
import os
import requests
from bs4 import BeautifulSoup

def query_serp(company_name):
    params = {
        "engine": "google",
        "q": f"{company_name} leadership team OR board of directors OR executive profiles",
        "api_key": os.getenv("SERP_API_KEY")
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    print(results)
    # urls = [result['link'] for result in results['organic_results']]
    
    return results

def clean_and_query_about_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        
        for tag in soup(["script", "style", "link"]):
            tag.decompose()
        
        relevant_tags = soup.find_all(["h1", "h2", "h3", "h5", "p", "div"])
        cleaned_text = "\n".join([tag.get_text(strip=True) for tag in relevant_tags])
        
        executives = query_chat(cleaned_text)
        return executives
    return None

def query_chat(webpage):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a webscraping assistant trying to identify the top executives at a given company."},
            {
                "role": "user",
                "content": f"""I have a chunk of HTML code parsed from a company's main website, which includes information about the company's executives. 
                            Using this HTML content, identify the names and titles of the company's top executives.
                            Here is the HTML content: {webpage}

                            I will provide a list of titles that you should be looking for in order of importance.
                            - Founders and co-founders (CEO, CTO, COO)
                            - Chief People Officer, VP of Talent Acquisition, VP of People, Chief of Staff
                            - Head of Talent Acquisition, Head of People
                            - VP of Engineering, VP of Operations
                            - Director of Engineering
                            - Anyone in talent acquisition/recruiting (keywords: talent, recruiter, chief of staff, head of people etc)
                            - Anyone who has ‘hiring’ in their linkedin name or bio 
                            The titles to look for include "CEO," "Founder," "President," "COO," "CTO," and "CFO." 
                            Return a list of names and titles of the executives.If you cannot identify any executives, return "No Executives Found" and say nothing else.
                            """
            }
        ]
    )

    return completion.choices[0].message.content

def find_linkedin_profiles(company_name):
    params = {
        "engine": "google",
        "q": f"{company_name} CEO OR COO OR CFO site:linkedin.com OR site:crunchbase.com",
        "api_key": os.getenv("SERP_API_KEY")
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    urls = [result['link'] for result in results.get('organic_results', [])]
    return urls

def get_executives_from_apollo(company_name):
    url = "https://api.apollo.io/v1/mixed_query"
    headers = {"Authorization": os.getenv("APOLLO_API_KEY")}
    params = {
        "company": company_name,
        "title": "CEO OR CFO OR COO OR President OR Executive"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code
