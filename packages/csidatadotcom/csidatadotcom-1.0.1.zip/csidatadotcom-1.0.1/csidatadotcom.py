# Created by James Darabi (mail@jdarabi.com)
# License: GNU LGPL

__version__ = '1.0.1'

import requests
import re

def get_end_of_day(type, exchangeid, active_only = True):

  payload = {'type': type, 'format': 'csv', 'exchangeid': exchangeid}
  r = requests.get('http://www.csidata.com/factsheets.php', params = payload)

  text = re.sub('\"', '', r.text)

  line_list = re.split('\r\n', text.encode('utf-8'))
  del line_list[-1]

  header = re.split(',', line_list[0])
  del line_list[0]

  out = []

  for line in line_list:
    values = re.split(',', line)
    data = dict(zip(header, values))
    if (not active_only) or (active_only and '1' == data['IsActive']):
      out.append(data)

  return out