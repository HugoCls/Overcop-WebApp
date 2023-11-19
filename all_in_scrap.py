import httpx
from bs4 import BeautifulSoup
import regex as re
import concurrent.futures
import json
import pandas as pd
import os
from datetime import datetime
import Levenshtein
import streamlit as st

def is_valid_size(size):
    # Utilisez une expression régulière pour vérifier si la taille est un float ou un float suivi d'une fraction
    regex_pattern = r'^(\d{2}|\d{2}\.\d|\d{2} \d\/\d|\d{2}\.\d \d\/\d)$'
    
    if re.search(regex_pattern, size):
        return True
    else:
        return False
    
def calculate_match_percentage(stock_name, data_name):

    max_length = max(len(stock_name), len(data_name))

    distance = Levenshtein.distance(stock_name, data_name)

    similarity = 1 - (distance / max_length)
 
    j_nb_stock = re.findall(r"jordan (\d+)", stock_name)
    j_nb_data = re.findall(r"jordan (\d+)", data_name)

    if (len(j_nb_stock) == 1 and len(j_nb_data) == 1) and (j_nb_stock[0] != j_nb_data[0]):
        return 0
    
    return round(similarity, 3)


def format_name(name):
    name = name.lower().replace('\u00a0',' ').replace('-',' ').replace('_',' ').replace('copy of ','').replace('copie de ', '')

    for mark in ['adidas', 'ugg', 'yeezy', 'nike', 'new balance', 'air jordan', 'jordan']:

        name = name.replace(f'{mark} {mark}', f'{mark}')
    
    name = name.replace('yeezy adidas yeezy','adidas yeezy')

    return name

def get_pairs_to_scrap(df, all_WTN_pairs):
    
    unique_names = df['Name'].unique()

    correspondances_df = pd.DataFrame(columns=['Name', 'Match', 'Ratio', 'href'])

    for index, stock_pair_name in enumerate(unique_names):
        print(index, stock_pair_name)
        best_match_name = None
        best_match_price = None
        best_match_href = None
        best_match_ratio = 0

        for pair in all_WTN_pairs:

            price = all_WTN_pairs[pair]["price"]
            href = all_WTN_pairs[pair]["href"]
            
            ratio = calculate_match_percentage(format_name(stock_pair_name), format_name(pair))
            
            if ratio > best_match_ratio:
                best_match_ratio = ratio
                best_match_name = pair
                best_match_price = price
                best_match_href = href
        
        
        new_row = {
            'Name': format_name(stock_pair_name),
            'Match': format_name(best_match_name),
            'Ratio': best_match_ratio,
            'href': best_match_href,
            }
    
        correspondances_df = pd.concat([correspondances_df, pd.DataFrame([new_row])], ignore_index=True)

    return correspondances_df
    
class Scraping:
    def __init__(self):
        self.df_pairs = pd.DataFrame(columns=['Name', 'href', 'Price', 'Sizes'])

        if not os.path.exists(f'data/{self.now}'):
            os.mkdir(f'data/{self.now}')
            
        self.now = datetime.now().strftime("%Y_%m_%d")

        self.all_WTN_pairs = {}

    def run(self):
        self.scrape_pages()

        self.scrap_shoes()
        
        with open(f'data/{self.now}/all_WTN_pairs.json','w') as f:
            f.write(str(self.all_WTN_pairs))

        self.create_final_df()
        
        self.df_pairs['ProcessingDate'] = self.now

        if not os.path.exists(f'data/{self.now}'):
            os.mkdir(f'data/{self.now}')

        self.df_pairs.to_csv(f'data/{self.now}/Prices.csv')

        #self.df_pairs.to_sql('WTN_Prices', con=self.engine, if_exists='append', index=False)

        print(self.df_pairs)

        print(self.df_pairs)

    def create_final_df(self):
        for pair_name in self.all_WTN_pairs:
    
            data = {
                'Name': [pair_name],
                'href': [self.all_WTN_pairs[pair_name]['href']],
                'Price': [str(self.all_WTN_pairs[pair_name]['price'])],
                'Sizes': [','.join([f"{key}:{value}" for key, value in self.all_WTN_pairs[pair_name]['sizes'].items()])],
                }
            
            self.df_pairs = pd.concat([self.df_pairs, pd.DataFrame(data)], ignore_index=True)

    def fetch_page_data(self, page_number):

        r = httpx.get(f"https://{st.secrets['website']}/collections/all-sneakers?page={page_number}")

        if r.status_code != 200:
            raise ValueError

        soup = BeautifulSoup(r.text, "html.parser")

        elements = soup.find_all("div", class_="styles_card__GmAAu styles_ProductCard__q4Ys8")
        
        for element in elements:
            a_el = element.find("a")
            href = a_el["href"]
            pair_name = a_el.text.strip()

            try:
                price_el = element.find("p").text.strip()
                price = re.findall("(\d+)€", price_el)[0]

                self.all_WTN_pairs[pair_name] = {
                    "price": price,
                    "href": href,
                    "sizes": {}
                }
            except:
                pass

    def fetch_pair_data(self, pair_name):
        href = self.all_WTN_pairs[pair_name]['href']

        r = httpx.get(f"https://{st.secrets['website']}{href}")

        if r.status_code != 200:
            raise ValueError
        
        soup = BeautifulSoup(r.text, "html.parser")

        element = soup.find('script', id='__NEXT_DATA__').text

        data = json.loads(element)
        
        sizes = data['props']['pageProps']['product']['variantsSelect'].keys()

        for size in sizes:
            size_el = data['props']['pageProps']['product']['variantsSelect'][size]
            size_value, price = size_el['sizes']['eu'], size_el['marketplace']['unformattedPrice']['amount']

            if is_valid_size(size_value):
                try:
                    float(price)
                    self.all_WTN_pairs[pair_name]['sizes'][str(size_value)] = str(price)
                except:
                    pass
        

    def scrape_pages(self):
        print("-- Starting scraping Pages --")

        if not os.path.exists(f"data/{self.now}/all_WTN_pairs.json"):
            
            r = httpx.get(f"https://{st.secrets['website']}/collections/all-sneakers")

            if r.status_code != 200:
                raise ValueError
            
            soup = BeautifulSoup(r.text, "html.parser")

            selected_elements = soup.find_all(lambda tag: tag.name == 'a' and tag.get('class') and tag.get('class')[0].startswith('styles_link__') and tag.get('href') and tag.get('href').startswith('/collections/all-sneakers?page='))

            nb_pages = int(selected_elements[-1].text)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                page_numbers = range(1, nb_pages + 1)

                futures = {executor.submit(self.fetch_page_data, page): page for page in page_numbers}
                
                concurrent.futures.wait(futures)

            with open(f"data/{self.now}/all_WTN_pairs.json", 'w') as f:
                json.dump(self.all_WTN_pairs, f, ensure_ascii=True)

            print("-- Pages scraping completed --")
        
        else:
            with open(f"data/{self.now}/all_WTN_pairs.json", 'r') as f:
                self.all_WTN_pairs = json.load(f)

    def scrap_shoes(self):
        print("-- Starting subdata scraping --")
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            
            futures = {executor.submit(self.fetch_pair_data, pair_name): pair_name for pair_name in self.all_WTN_pairs.keys()}

            concurrent.futures.wait(futures)
        print("-- Subdata scraping completed --")