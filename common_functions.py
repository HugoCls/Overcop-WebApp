import Levenshtein
import re
from fractions import Fraction


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


def get_closer_5_euros_price(price):

    price = round(price / 5) * 5
    
    return price


def convert_to_decimal(size):

    size = size.replace(',','.')

    if ' ' in size:
        whole, frac = size.split()
        
        return round(float(whole) + float(Fraction(frac)) / 10, 2)
    else:
        return round(float(size), 2)
        

def get_closer_sizes_price(WTN_prices, given_shoe_size):
    
    given_size = convert_to_decimal(given_shoe_size)
    
    sizes = {float(convert_to_decimal(k)): float(v) for k, v in WTN_prices.items()}
    
    sorted_sizes = sorted(sizes.keys())
    
    index = 0
    
    for i, size in enumerate(sorted_sizes):
        if size < given_size:
            index = i + 1
        else:
            break

    closest_sizes = sorted_sizes[max(0, index - 1):index + 1]

    if len(closest_sizes) == 2:
        average_price = (sizes[closest_sizes[0]] + sizes[closest_sizes[1]]) / 2

        return average_price, f' with {closest_sizes[0]} ({sizes[closest_sizes[0]]}€) and {closest_sizes[1]} ({sizes[closest_sizes[1]]}€)'
    
    elif len(closest_sizes) == 1:
        return sizes[closest_sizes[0]], f' with {closest_sizes[0]} ({sizes[closest_sizes[0]]}€)'
    
    else:
        prices_as_floats = [float(price) for price in sizes.values()]
                                    
        average_price = sum(prices_as_floats) / len(prices_as_floats)
        
        return average_price, f' with complete average ({average_price}€)'