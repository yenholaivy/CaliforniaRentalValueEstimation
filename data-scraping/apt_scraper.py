from bs4 import BeautifulSoup as soup
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import json
import random
import pprint
import re

def get_property_urls(master_df, city_page_url):
    time.sleep(5)
    header = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}
    print(city_page_url)
    try:
        r = requests.get(city_page_url, timeout = 30, headers = header)
        if r.status_code == 200:
            page_soup = soup(r.content, 'html.parser')
            script = page_soup.find('script',type='application/ld+json')
            script_json = json.loads(str(script)[41:-11])
            property_urls = []
            master_listing = master_df.url.values
            print("Generating property urls...")
            for item in script_json['about']:
                url = item['url']
                if url not in master_listing:
                    property_urls.append(url)
                    print(url)
                else:
                    print(f"{url} already in the master listing. Skip")   
            return property_urls
        else:
            print(f"Exception on {city_page_url}!")                  
    except:
        print(f"Exception on {city_page_url}!")
        
def get_property_name(url, page):
    try:
        return page.select("h1", {"class":"propertyName"})[0].text.strip()
    except:
        return f"Can't get property name for {url}"

def get_property_city(url, page):
    try:
        property_address = page.findAll("div", {"class":"propertyAddressContainer"})[0].text.strip()
        return property_address.split(",")[1].replace('\r\n','').lstrip()
    except:
        return f"Can't get property city for {url}"

def get_price_floor(url, page):
    try:
        div = page.find('div', {"class":"tab-section active"})

        price_lst = []
        room_lst = []
        bath_lst = []
        sq_ft = []

        rent_labels = div.findAll('span', {"class":"rentLabel"})
        detail_labels = div.findAll('h4')

        for rent, detail in zip(rent_labels, detail_labels):
            #get rent info
            price_lst.append(rent.text.replace('\r','').replace('\n', '').strip())
            #get floor info
            floor = detail.find('span', {"class":"detailsTextWrapper"})
            floor_text = floor.text.replace('\n','').replace('\r','#').split(',#')
            if len(floor_text) == 3:
                room_lst.append(floor_text[0].strip())
                bath_lst.append(floor_text[1].strip())
                sq_ft.append(floor_text[2].strip()) 
            if len(price_lst) - len(room_lst) == 1:
                price_lst = price_lst[:-1]    
        return price_lst, room_lst, bath_lst, sq_ft
    except:
        return f"Can't get pricing & floor plans for {url}"    

def get_walkscore(url, page):
    try:
        return page.find("span", {"class":"score"}).text   
    except:
        return f"Can't get property walkscore for {url}"  

 def get_apt_amenities(url, page):
    try:
        div = page.find("div", {"class":"js-viewAnalyticsSection"})
        amenities_dict = {}
        tag_re = re.compile(r'<[^>]+>')

        for tag in div.find_all():
            if tag.name == 'h3':
                amenity = tag.text
                html = u""
                for content in tag.next_siblings:
                    html += str(content)
                amenities_dict[amenity] = html
#         pp = pprint.PrettyPrinter(indent=4)
#         pp.pprint(amenities_dict) 
        df = pd.DataFrame([amenities_dict])
        for col in df.columns:
            clean_text = tag_re.sub('',df[col][0])
            clean_text = clean_text.replace('\r','').replace('   ','').replace('\n\n','').strip()
            df[col][0] = clean_text
        return df
    except:
        return f"Can't get apartment amenities for {url}"   

def create_df(url, property_name, city, price_lst, room_lst, bath_lst, sq_ft, walkscore, apt_amenities):
    num_rows = len(price_lst)
    data = {'url':[url]*num_rows,
               'property_name' : [property_name]*num_rows,
               'city' : [city]*num_rows,
               'rent' : price_lst,
               'bed' : room_lst,
               'bath' : bath_lst,
               'sq_ft' : sq_ft,
               'walkscore' : [walkscore]*num_rows}
    df = pd.DataFrame(data)
    for col in apt_amenities.columns:
        df[col] = [apt_amenities[col][0]]*num_rows
    return df

def add_to_df(master_df, new_df):
    return pd.concat([master_df, new_df], sort=False, ignore_index=True)

def apt_page_scrapper(url):
    time.sleep(5)
    print("Getting apt info")
    header = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}
    try:
        r = requests.get(url, timeout = 30, headers = header)
        request_state_code = r.status_code
        if request_state_code == 200:
            print("Status code: 200")
            page_soup = soup(r.content, 'html.parser')
            #get apt_info
            price_lst, room_lst, bath_lst, sq_ft = get_price_floor(url, page_soup)
            property_name = get_property_name(url, page_soup)
            if price_lst != []:
                city = get_property_city(url,page_soup)
                walkscore = get_walkscore(url,page_soup)
                apt_amenities = get_apt_amenities(url, page_soup)
                #create df
                df = create_df(url, property_name, city, price_lst, room_lst, bath_lst, sq_ft, walkscore, apt_amenities)
                print(f"{property_name} dataframe has been created")
                return df
            else:
                print('dataframe not created because not enough information')
                return 'Error!'       
    except requests.exceptions.ConnectionError:
        print("Request refused by the server. Retry in 1min")
        time.sleep(60)
        return 'Error!'  
    except:
        print('Something is not right with the apt info')
        return 'Error!'

def create_dataframe(count_item, city_url, master_df, first_page, last_page):
    for i in np.arange(first_page, last_page):
        try:
            if i == 1:
                property_urls = get_property_urls(master_df, city_url)
            else:
                property_urls = get_property_urls(master_df, city_url + str(i))

            for url in property_urls:
                count_item += 1
                print(f"Property #{count_item}: {url}")
                try:
                    new_df = apt_page_scrapper(url)
                    master_df = add_to_df(master_df,new_df)
                    print(f"data added")
                except:
                    print(f"data not added")
                    count_item -= 1
                print(" ")
        except:
            print(f"{city_url} page {i} is giving error!")

    return master_df, count_item

# Scrape San Francisco apartment data from page 1 to 5 and save as csv
master_df = pd.DataFrame() 
count_item = 0
url = 'https://www.apartments.com/san-francisco-ca/'
master_df, count_item = create_dataframe(count_item, url, master_df, 1, 5)

master_df.to_csv('master_data.csv')

