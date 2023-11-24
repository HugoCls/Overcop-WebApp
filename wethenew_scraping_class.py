import httpx
from bs4 import BeautifulSoup

import pandas as pd

from datetime import datetime

import json
import os

import regex as re
import concurrent.futures

from common_functions import calculate_match_percentage, get_closer_5_euros_price, format_name, is_valid_size, get_closer_sizes_price
from sqlalchemy import create_engine

import logging
import streamlit as st

log = logging.getLogger(__name__)

def fill_image_src(group):

    default_image = "https://t3.ftcdn.net/jpg/00/36/94/26/360_F_36942622_9SUXpSuE5JlfxLFKB1jHu5Z07eVIWQ2W.jpg"  # Remplacez par le chemin de votre image par défaut

    if group["Image Src"].notnull().any():
        group["Image Src"].fillna(group["Image Src"].iloc[0], inplace=True)
    else:
        group["Image Src"].fillna(default_image, inplace=True)
    return group


class Scraping:
    def __init__(self):

        self.engine = create_engine(f'mysql://{st.secrets["MYSQL_USERNAME"]}:{st.secrets["MYSQL_PASSWORD"]}@{st.secrets["VPS_IP"]}/{st.secrets["MYSQL_DATASET"]}')

        # Initialiser les données
        self.current_date = datetime.now().strftime("%Y_%m_%d")
        
        df = pd.read_csv(f'data/{self.current_date}/products_export.csv', dtype=str)
        
        sql_df = df

        sql_df = sql_df.groupby('Handle').apply(fill_image_src)

        sql_df = sql_df[["Handle", "Option1 Value", "Variant Price", "Image Src"]]

        sql_df = sql_df.rename(columns={"Handle": "Name", "Option1 Value": "Size", "Variant Price": "Price", "Image Src": "Image"})

        pd.DataFrame(sql_df).to_sql('Database', con=self.engine, if_exists='replace', index=False)
        
        df["Name"] = df.groupby('Handle')['Vendor'].transform(lambda x: x.fillna(x.loc[x.notnull()].iloc[0])) + ' ' + df.groupby('Handle')['Title'].transform(lambda x: x.fillna(x.loc[x.notnull()].iloc[0]))
        df["Size"] = df["Option1 Value"]
        
        self.initial_ov_exported_df = df

        self.daily_ov_WTN_correspondances_df = pd.DataFrame(columns=['ov_name', 'matched', 'WTN_name', 'WTN_displayed_price', 'WTN_prices', 'WTN_href'])

        self.all_WTN_pairs = {}

        self.seuil = 0.8

        
    def run(self):
        if os.path.exists(f"data/{self.current_date}/product_export_w_new_prices.csv"):
            log.info('"product_export_w_new_prices.csv" already exists, skipping wtn scrap')
        else:
            self.scrap_shoes_main_data()

            self.get_correspondances()

            self.scrap_stock_shoes_subdata()
        
            self.create_final_csv()


    def fetch_page_data(self, page):
        #log.info(f"Page {page+1}/{self.nb_pages} | Loading Data")
                
        r = httpx.get(f"https://wethenew.com/collections/all-sneakers?page={page+1}")

        if r.status_code != 200:
            log.info('Could not scrap data for this page')
        
        else:
            soup = BeautifulSoup(r.text, "html.parser")

            elements = soup.find_all("div", class_="styles_card__GmAAu styles_ProductCard__q4Ys8")

            for element in elements:
                a_el = element.find("a")
                
                href = a_el["href"]
                
                pair_name = a_el.text.strip()

                try:
                    price_el = element.find("p").text.strip()
                    
                    price = re.findall("(\d+)€",price_el)[0]
                    
                    self.all_WTN_pairs[pair_name] = {}
                    self.all_WTN_pairs[pair_name]["price"] = price
                    self.all_WTN_pairs[pair_name]["href"] = href
                    self.all_WTN_pairs[pair_name]["sizes"] = {}

                except:
                    pass


    def fetch_pair_data(self, pair_name):
        log.info(f"Pair {self.count} | Retrieving Prices")
        self.count += 1

        href = self.daily_ov_WTN_correspondances_df.loc[self.daily_ov_WTN_correspondances_df['WTN_name'] == pair_name, 'WTN_href'].iloc[0]
        displayed_price = self.daily_ov_WTN_correspondances_df.loc[self.daily_ov_WTN_correspondances_df['WTN_name'] == pair_name, 'WTN_displayed_price'].iloc[0]
        
        WTN_prices = {}

        log.info(f"Name: {pair_name}")
        log.info(f"Href: {href}")
        log.info(f"Price: {displayed_price}€")

        r = httpx.get(f"https://wethenew.com{href}")

        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")

            element = soup.find('script', id='__NEXT_DATA__').text

            data = json.loads(element)

            sizes = data['props']['pageProps']['product']['variantsSelect'].keys()

            for size in sizes:
                size_el = data['props']['pageProps']['product']['variantsSelect'][size]

                if type(size_el['sizes']) == dict:
                    size = size_el['sizes']['eu']
                else:
                    size = size_el['sizes'].strip(' EU').replace(',','.')

                price = size_el['marketplace']['unformattedPrice']['amount']

                if is_valid_size(size):
                    try: #price != "Indisponible":
                        float(price)

                        WTN_prices[size] = price
                    except:
                        pass
        else:
            log.info('Could not scrap data for this pair')

        self.daily_ov_WTN_correspondances_df.loc[self.daily_ov_WTN_correspondances_df['WTN_name'] == pair_name, 'WTN_prices'] = json.dumps(WTN_prices)
        
        log.info(f"Sizes: {json.dumps(WTN_prices)}")
        log.info('--------------------------------------------')


    def scrap_shoes_main_data(self):
        log.info("-- Scraping all WTN pairs names & main data --")
        
        if not os.path.exists(f"data/{self.current_date}/all_WTN_pairs.json"):
            r = httpx.get("https://wethenew.com/collections/all-sneakers")

            soup = BeautifulSoup(r.text, "html.parser")

            selected_elements = soup.find_all(lambda tag: tag.name == 'a' and tag.get('class') and tag.get('class')[0].startswith('styles_link__') and tag.get('href') and tag.get('href').startswith('/collections/all-sneakers?page='))

            self.nb_pages = int(selected_elements[-1].text)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                page_numbers = range(1, self.nb_pages + 1)

                futures = {executor.submit(self.fetch_page_data, page): page for page in page_numbers}
                
                concurrent.futures.wait(futures)

            log.info("-- Pages scraping completed --")
            
            with open(f"data/{self.current_date}/all_WTN_pairs.json", 'w') as f:
                json.dump(self.all_WTN_pairs, f, ensure_ascii=True)

        else:
            with open(f"data/{self.current_date}/all_WTN_pairs.json", 'r') as f:
                self.all_WTN_pairs = json.load(f)


    def scrap_stock_shoes_subdata(self):
        
        if not os.path.exists(f"data/{self.current_date}/ov_WTN_correspondances.csv"):

            self.get_pairs_to_scrap()

            unique_WTN_names = self.daily_ov_WTN_correspondances_df['WTN_name'].dropna().unique()
            
            log.info("-- Scraping each corresponding pair main data --")
            log.info('--------------------------------------------')
            
            self.count = 1

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        
                futures = {executor.submit(self.fetch_pair_data, pair_name): pair_name for pair_name in unique_WTN_names}

                concurrent.futures.wait(futures)
                
            self.daily_ov_WTN_correspondances_df.to_csv(f"data/{self.current_date}/ov_WTN_correspondances.csv", index=False)
        
        else:
            self.daily_ov_WTN_correspondances_df = pd.read_csv(f"data/{self.current_date}/ov_WTN_correspondances.csv")

    def get_correspondances(self):

        correspondances_df = pd.DataFrame(columns=['ov_name', 'WTN_name', 'ratio', 'href', 'formated_ov_name', 'formated_WTN_name'])

        for stock_index, stock_row in self.initial_ov_exported_df.iterrows():
            stock_pair_name = stock_row["Name"]
            best_match_name = None
            best_match_price = None
            best_match_href = None
            best_match_ratio = 0

            for pair in self.all_WTN_pairs:
                
                price = self.all_WTN_pairs[pair]["price"]
                href = self.all_WTN_pairs[pair]["href"]
                
                ratio = calculate_match_percentage(format_name(stock_pair_name), format_name(pair))
                
                if ratio > best_match_ratio:
                    best_match_ratio = ratio
                    best_match_name = pair
                    best_match_price = price
                    best_match_href = href
            
            new_row = {
                'ov_name': stock_pair_name,
                'WTN_name':best_match_name, 
                'ratio':best_match_ratio,
                'href':best_match_href,
                'formated_ov_name':format_name(stock_pair_name),
                'formated_WTN_name':format_name(best_match_name),
            }

            correspondances_df = pd.concat([correspondances_df, pd.DataFrame([new_row])])
        
        correspondances_df = correspondances_df.drop_duplicates(subset=['ov_name'])
        
        correspondances_df.to_csv(f"data/{self.current_date}/correspondances.csv")


    def get_pairs_to_scrap(self):
        log.info("-- Determining which pairs to scrap specificly --")
        
        for stock_index, stock_row in self.initial_ov_exported_df.iterrows():
            stock_pair_name = stock_row["Name"]
            best_match_name = None
            best_match_price = None
            best_match_href = None
            best_match_ratio = 0

            for pair in self.all_WTN_pairs:
                
                price = self.all_WTN_pairs[pair]["price"]
                href = self.all_WTN_pairs[pair]["href"]
                
                ratio = calculate_match_percentage(format_name(stock_pair_name), format_name(pair))
                
                if ratio > best_match_ratio:
                    best_match_ratio = ratio
                    best_match_name = pair
                    best_match_price = price
                    best_match_href = href
            
            if best_match_ratio >= self.seuil:
                new_row = {
                    'ov_name': stock_pair_name,
                    'matched': True,
                    'WTN_name': best_match_name,
                    'WTN_displayed_price': best_match_price,
                    'WTN_prices': None,
                    'WTN_href': best_match_href,
                    }
            else:
                new_row = {
                    'ov_name': stock_pair_name,
                    'matched': False,
                    'WTN_name': None,
                    'WTN_displayed_price': None,
                    'WTN_prices': None,
                    'WTN_href': None,
                    }
            
            self.daily_ov_WTN_correspondances_df = pd.concat([self.daily_ov_WTN_correspondances_df, pd.DataFrame([new_row])], ignore_index=True)
        #self.daily_ov_WTN_correspondances_df.to_csv(f"data/{self.current_date}/daily_ov_WTN_correspondances.csv")
        
        Matched_ov_names = list(self.daily_ov_WTN_correspondances_df.loc[self.daily_ov_WTN_correspondances_df['matched'] == True, 'ov_name'].unique())
        Unmatched_ov_names = list(self.daily_ov_WTN_correspondances_df.loc[self.daily_ov_WTN_correspondances_df['matched'] == False, 'ov_name'].unique())
        log.info(f'Matched: {Matched_ov_names}')
        log.info(f'Unmatched: {Unmatched_ov_names}')
        #Add sizes matches
 

    def create_final_csv(self):
        if not os.path.exists(f'data/{self.current_date}/product_export_w_new_prices.csv'):
            log.info("-- Creating final data --")
            self.daily_ov_to_import_df = pd.DataFrame(columns=['Handle','Title','Body (HTML)','Vendor','Product Category','Type','Tags','Published','Option1 Name','Option1 Value','Variant Price'])

            _ProcessingDate, _Name, _Size, _Price, _State, _chosen_pair = [], [], [], [], [], []

            for index, stock_row in self.initial_ov_exported_df.iterrows():
                new_row = stock_row

                correspondances_row = self.daily_ov_WTN_correspondances_df[self.daily_ov_WTN_correspondances_df['ov_name'] == stock_row["Name"]].iloc[0]
                
                current_size = stock_row["Size"]

                if correspondances_row['matched']:
                    
                    WTN_prices = json.loads(correspondances_row['WTN_prices'])
                    
                    chosen_pair = format_name(correspondances_row['WTN_name']).title()

                    message = ''

                    if current_size in WTN_prices.keys():
                        state = "custom"

                        new_price = get_closer_5_euros_price(WTN_prices[current_size] * 0.93)

                    else:
                        if len(WTN_prices) >= 1:

                            state = "average"

                            average_price, message = get_closer_sizes_price(WTN_prices, current_size)

                            new_price = get_closer_5_euros_price(float(average_price) * 0.93)

                        else:
                            state = "displayed"
                            
                            new_price = get_closer_5_euros_price(float(correspondances_row['WTN_displayed_price']) * 0.93)

                    log.info(f"{stock_row['Handle']}, {current_size} price changed from {stock_row['Variant Price']} to {new_price} with {state} price{message}.")
                    
                    _ProcessingDate.append(datetime.now())
                    _Name.append(stock_row['Handle'])
                    _Size.append(current_size)
                    _Price.append(new_price)
                    _State.append(state)
                    _chosen_pair.append(chosen_pair)
                                                
                else:
                    new_price = stock_row['Variant Price']
                    log.info(f"{stock_row['Handle']}, {current_size} price unchanged.")
                
                new_row['Variant Price'] = new_price
                
                self.daily_ov_to_import_df = pd.concat([self.daily_ov_to_import_df, pd.DataFrame([new_row])], ignore_index=True)
            
            data = {'ProcessingDate': _ProcessingDate, 'Name': _Name, 'Size': _Size, 'Price': _Price, 'State': _State, 'chosen_pair': _chosen_pair}

            pd.DataFrame(data).to_sql(st.secrets["table_logs"], con=self.engine, if_exists='append', index=False)
            
            self.daily_ov_to_import_df.to_csv(f'data/{self.current_date}/product_export_w_new_prices.csv')