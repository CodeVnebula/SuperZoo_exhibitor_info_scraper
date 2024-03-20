from bs4 import BeautifulSoup
import pandas as pd
import requests
import csv
import re
import os

main_url = 'https://s23.a2zinc.net/clients/WPA/SZ2022/Public/Exhibitors.aspx?Index=All'

link_ids = []       # This list is for saving link ID's  e.g.(000000) numbers for each site

web_resp = requests.get(main_url)
html = web_resp.text
soup = BeautifulSoup(html, 'lxml')
table = soup.find('table', class_='table table-striped table-hover')   # This one gets full list of companies
rows = table.find_all('tr')
counter = 1
for row in rows:
    linked = row.find('td', class_='cf CustomField_20')         # Finding possible companies having linkedln URL's
    if linked is not None:                                      # Checking if company got a LinkedIn URL
        counter += 1
        a = row.find('a', class_='exhibitorName')['href']       # Finds all id's of site for companies, which have linkedln URL's
        id_numbers = re.findall(r'\bBoothID=(\d+)\b', a)        # Removing link ID's from links
        link_ids.append(id_numbers)                             # Saving ID's into link_ids list for future use
print(f'{counter} Companies found with LinkedIn URL...')
print("Started getting data from the website... Hang on!")
with open('Exhibitors_temp.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Company Name', 'Location', 'Company URL', 'LinkedIn URL', 'Brands', 'Description']       # Determining headers of fields in the csv file
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for i in range(len(link_ids)):      # Iterating over each of found ID's !(Same amount as count)                                                        # Adding Saved ID's 6 digit
        link = 'https://s23.a2zinc.net/clients/WPA/SZ2022/Public/eBooth.aspx?IndexInList=108&FromPage=Exhibitors.aspx&ParentBoothID=&ListByBooth=true&BoothID=' + str(link_ids[i][0]) + '&fromFeatured=1'  
        response = requests.get(link)
        content = response.text
        soup = BeautifulSoup(content, 'lxml')               # Soup instance
        panel = soup.find('div', class_='panel-body')       # Name, URL's and location are stored in one div 'class=panel-body'
        div_page = soup.find('div', class_ = 'col-sm-8')    # Description and Brands must be saved into another div 'class= col-sm-8'
        company_name = panel.find('h1').text.strip()        # Company name is stored into h1 tag

        city_element = panel.find('span', class_='BoothContactCity')    # Findig city element in span tag
        city = city_element.text.strip() if city_element else ''        # If city element not found then it's set to '' (empty)  
        
        state_element = panel.find('span', class_ = 'BoothContactState')     # Findig state element in span tag
        state = state_element.text.strip() if state_element else ''          # If state element not found then it's set to '' (empty)

        company_url = panel.find('a', id='BoothContactUrl').text        # Every page must have company_url so we don't need to check if they exist or no

        linkedin_url_element = panel.find('a', id='ctl00_ContentPlaceHolder1_ctrlCustomField_Logos_dlCustomFieldList_ctl01_lnkCustomField')     # LinkedIn URL has its unique id
        linkedin_url = linkedin_url_element['href'].strip() if linkedin_url_element else ''    # Getting only url 

        description = ''
        for p_tag in div_page.find_all('p'):        # Description is stored in p tags
            if not p_tag.text.strip():              # Checking if the current p tag is empty
                pass
            else:
                if p_tag.has_attr('class') and 'BoothBrands' in p_tag.get('class', []):     # p tag with this class holds Brands which we don't need in description
                    pass
                else:
                    if any(p_tag.stripped_strings):                         # Checking if there are child tags in p tag so we need to add them too
                        description += ' '.join(p_tag.stripped_strings)
                    else:
                        description = description + p_tag.text             
        
        cleaned_description = re.sub(r'[^a-zA-Z0-9\s\.,!?]', '', description)

        brand_element = div_page.find('p', class_ = 'BoothBrands')
        brand = brand_element.text.strip().replace('Brands:', '') if brand_element else ''

        
        writer.writerow({                        # Started here in writerow() - function /// import csv
            'Company Name': company_name,         #
            'Location': city + state,              # 
            'Company URL': company_url,             # writing scraped info into the csv file
            'LinkedIn URL': linkedin_url,          # 
            'Brands' : brand,                     #  
            'Description' : cleaned_description  #
        })                                     # End 
        
        print(f'{((i + 1) / len(link_ids)) * 100:.3f}% Completed...')        # (:.3f) for saving only 3 numbers after comma

print("Information successfully stored into Exhibitors.csv file!")

df = pd.read_csv('Exhibitors_temp.csv', encoding='latin1')
df.to_csv('Exhibitors.csv', index=False)                    # Formating information into 'Exhibitors_temp.csv' 
os.remove('Exhibitors_temp.csv')                        # Then removing it and writing info into 'Exhibitors_temp.csv'