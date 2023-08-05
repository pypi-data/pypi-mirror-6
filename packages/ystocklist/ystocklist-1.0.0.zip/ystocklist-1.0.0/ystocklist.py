# Created by James Darabi (mail@jdarabi.com)

__version__ = '1.0.0'
__license__ = 'GNU LGPL'

import re
import csidatadotcom

# This function maps stock symbols from www.csidata.com to Yahoo stock symbols
def _csitoy(symbol):

  if re.search(r'-', symbol):
    symbol += 'T'

  symbol = re.sub('\.', '-', symbol)
  symbol = re.sub(r'\+', r'-P', symbol)

  return symbol

def get_list(exchange):

  exchangeid = {
    'amex'  : 80,
    'nyse'  : 79,
    'otc'   : 88
  }

  key_list = ['Symbol', 'Name', 'Exchange', 'StartDate', 'Sector', 'Industry']

  active_stock_list = csidatadotcom.get_end_of_day('stock', exchangeid[exchange.lower()])

  out = []

  for stock in active_stock_list:
    stock['Symbol'] = _csitoy(stock['Symbol'])
    data = dict(zip(key_list, [stock[key] for key in key_list]))
    out.append(data)

  return out