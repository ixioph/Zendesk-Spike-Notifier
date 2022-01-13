#this 

from base64 import b64encode
from datetime import datetime, timedelta
import datetime as dt
from numpy import dtype, float64
from pandas.core.frame import DataFrame
from pandas.tseries.offsets import Tick
import requests
import json
import pandas as pd
import logging
import configparser

config = configparser.RawConfigParser()
config.read('../src/auth.ini')
OUTPUT_FILE = config['default']['SpikeDB'].strip('"')
DOMAIN = config['zendesk']['Domain'].strip('"')
AUTH = config['zendesk']['Credentials'].strip('"')

def run(logger):
  logger.warning('Creating Output File.')
  columns = list(range(24))
  TicketCount = pd.DataFrame(columns = columns)
  TicketCount.to_csv(OUTPUT_FILE)
  logger.warning("Output File ready for usage.")

  i = 0
  logger.warning('This is gonna take a while. Go drink some tea.')
  while i < 4: #CHANGE THIS TO NR OF HOURS NEEDED (4380 HOURS IN HALF A YEAR)
    i = i + 1
    now = datetime.utcnow().replace(microsecond=0, second=0, minute=0)
    start_date = (now + timedelta(hours= -i))
    st0 = start_date.strftime("%Y-%m-%dT%H:%M:%SZ") #start date/time formatted for get request
    sub_start_date = (start_date + timedelta(hours= 1))
    st1 = sub_start_date.strftime("%Y-%m-%dT%H:%M:%SZ") #end date/time formatted for get request
    xdst0, xtst0 = start_date.strftime("%Y-%m-%d"), start_date.strftime("%H") #date/time separately formatted for excel
    lst = get_ticket_numbers(DOMAIN, st0, st1)
    lst = json.loads(lst.text)
    
    u = int(xtst0)

    TicketCount.at[str(xdst0), u] = str(lst["count"])
    TicketCount.to_csv(OUTPUT_FILE)
  logger.warning("Output File successfully updated!")

def get_ticket_numbers(dom, st0, st1):
  print(b64encode(AUTH.encode('utf-8'))[2:-1])
  header = {"Authorization": "Basic {}".format(str(b64encode(AUTH.encode('utf-8')))[2:-1])}
  url = f"https://{dom}.zendesk.com/api/v2/search.json?query=type:ticket+created>{st0}+created<{st1}"

  try:
    r = requests.get(url, headers=header)
    return r
  except Exception as err: 
    print('ERROR:', str(err))
    return -1

if __name__ =="__main__":
    # TODO: set logging level based on input
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    run(logger)