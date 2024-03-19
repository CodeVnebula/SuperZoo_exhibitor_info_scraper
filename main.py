import csv
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import os

main_url = 'https://s23.a2zinc.net/clients/WPA/SZ2022/Public/Exhibitors.aspx?Index=All'

link_ids = []

web_resp = requests.get(main_url)
html = web_resp.text
soup = BeautifulSoup(html, 'lxml')
table = soup.find('table', class_='table table-striped table-hover')   # This one gets full list of companies
rows = table.find_all('tr')
counter = 1
for row in rows:
    linked = row.find('td', class_='cf CustomField_20')         # Finding possible companies having linkedln URL's
    if linked is not None:
        counter += 1
        a = row.find('a', class_='exhibitorName')['href']       # Finds all id's of site for companies, which have linkedln URL's
        id_numbers = re.findall(r'\bBoothID=(\d+)\b', a)        # Removing link ID's from links
        link_ids.append(id_numbers)                         # Saving ID's into link_ids list for future use
print(f'{counter} Companies found with LinkedIn URL...')
print("Started getting data from the website... Hang on!")
with open('Exhibitors_temp.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Company Name', 'Location', 'Company URL', 'LinkedIn URL', 'Brands', 'Description'] 
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for i in range(len(link_ids)):
        link = 'https://s23.a2zinc.net/clients/WPA/SZ2022/Public/eBooth.aspx?IndexInList=108&FromPage=Exhibitors.aspx&ParentBoothID=&ListByBooth=true&BoothID=' + str(link_ids[i][0]) + '&fromFeatured=1'
        response = requests.get(link)
        content = response.text
        soup = BeautifulSoup(content, 'lxml')
        panel = soup.find('div', class_='panel-body')
        div_page = soup.find('div', class_ = 'col-sm-8')
        company_name = panel.find('h1').text.strip()

        city_element = panel.find('span', class_='BoothContactCity')
        city = city_element.text.strip() if city_element else ''
        
        state_element = panel.find('span', class_ = 'BoothContactState')
        state = state_element.text.strip() if state_element else ''

        company_url = panel.find('a', id='BoothContactUrl').text

        linkedin_url_element = panel.find('a', id='ctl00_ContentPlaceHolder1_ctrlCustomField_Logos_dlCustomFieldList_ctl01_lnkCustomField')
        linkedin_url = linkedin_url_element['href'].strip() if linkedin_url_element else ''

        brand_element = div_page.find('p', class_ = 'BoothBrands')
        brand = brand_element.text.strip().replace('Brands:', '') if brand_element else ''

        description_element = div_page.find('p', class_='BoothBrands').find_previous_sibling('p') if div_page.find('p', class_='BoothBrands') else div_page.find('p')
        description = description_element.text.strip() if description_element else ''

        writer.writerow({
            'Company Name': company_name,
            'Location': city + state,
            'Company URL': company_url,
            'LinkedIn URL': linkedin_url,
            'Brands' : brand,
            'Description' : description
        })
        
        print(f'{((i + 1) / len(link_ids)) * 100:.3f}% Complete...')

print("Information successfully stored into Exhibitors.csv file!")

df = pd.read_csv('Exhibitors_temp.csv', encoding='latin1')
df.to_csv('Exhibitors.csv', index=False)
os.remove('Exhibitors_temp.csv')