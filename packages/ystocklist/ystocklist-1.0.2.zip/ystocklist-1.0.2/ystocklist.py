# Created by James Darabi (mail@jdarabi.com)

__version__ = '1.0.2'
__license__ = 'GNU LGPL'

import re
import csidatadotcom

# This function maps stock symbols from www.csistock_dict.com to Yahoo stock symbols
def _csitoy(symbol):

  if re.search(r'-', symbol):
    symbol += 'T'

  symbol = re.sub('\.', '-', symbol)
  symbol = re.sub(r'\+', r'-P', symbol)

  return symbol

def get_list():

  exchange_list = ['amex', 'nyse', 'otc']
  exchangeid = dict(zip(exchange_list, [80, 79, 88]))

  stock_list = []

  for exchange in exchange_list:
    stock_list += csidatadotcom.get_end_of_day('stock', exchangeid[exchange])

  key_list = ['Symbol', 'Name', 'Exchange', 'StartDate', 'Sector', 'Industry']

  out = []

  for stock in stock_list:
    stock['Symbol'] = _csitoy(stock['Symbol'])
    stock_dict = dict(zip(key_list, [stock[key] for key in key_list]))
    out.append(stock_dict)

  return out