# TicketCounter.py

from datetime import datetime, timedelta
from base64 import b64encode
import pandas as pd
import requests
import logging
import json


def run(logger, filename, n_hours, domain, auth):
  columns = list(range(24))
  TicketCount = pd.DataFrame(columns = columns)
  TicketCount.to_csv(filename)

  logger.warning('Populating Output File. This is gonna take a while. Go drink some tea.')
  try:
    for i in range(n_hours): # (4380 HOURS IN HALF A YEAR)
      st0, st1, xdst0, xtst0, xtst1 = get_formatted_datetimes(i)

      lst = get_ticket_count(domain, auth, st0, st1)
      lst = json.loads(lst.text)

      TicketCount.at[str(xdst0), int(xtst0)] = str(lst["count"])
    TicketCount.to_csv(filename)
  except Exception as e:
    logger.warning('Error populating database: {}'.format(str(e)))

# takes an integer t_delta as an argument
# returns a set of times, with the start date being current hour - t_delta

def get_formatted_datetimes(t_delta):
  now = datetime.utcnow().replace(microsecond=0, second=0, minute=0)
  start_date = (now + timedelta(hours= -t_delta))
  #start date/time formatted for get request
  st0 = start_date.strftime("%Y-%m-%dT%H:%M:%SZ") 
  sub_start_date = (start_date + timedelta(hours= 1))
  #end date/time formatted for get request
  st1 = sub_start_date.strftime("%Y-%m-%dT%H:%M:%SZ") 
  #date/time separately formatted for excel
  xdst0, xtst0 = start_date.strftime("%Y-%m-%d"), start_date.strftime("%H") 
  xtst1 = now.strftime("%H")
  return st0, st1, xdst0, xtst0, xtst1

# takes the zendesk account subdomain, and a start and end datetime (%Y-%m-%dT%H:%M:%SZ)
# returns the result of a GET request to the Zendesk v2 API

def get_ticket_count(dom, auth, st0, st1):
  print(b64encode(auth.encode('utf-8'))[2:-1])
  header = {"Authorization": "Basic {}".format(str(b64encode(auth.encode('utf-8')))[2:-1])}
  url = f"https://{dom}.zendesk.com/api/v2/search.json?query=type:ticket+created>{st0}+created<{st1}"

  try:
    r = requests.get(url, headers=header)
    return r
  except Exception as err: 
    print('Error making zendesk GET request:', str(err))
    exit()

if __name__ =="__main__":
    # TODO: set logging level based on input
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    run(logger)