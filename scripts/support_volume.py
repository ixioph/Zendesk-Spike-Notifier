# support_volume.py
# This script is designed to be run once an hour
# it counts the Zendesk tickets created over the past hour
# and saves the information to a database
# in the event of a "spike" (abnormally high ticket volume)
# an email is sent to <reporters>

from base64 import b64encode
from numpy import dtype, float64
from pandas.core.frame import DataFrame
from pandas.tseries.offsets import Tick
from tqdm import tqdm
from datetime import datetime, timedelta
import datetime as dt
import configparser
import logging
import json
import pandas as pd
import requests
import os

config = configparser.ConfigParser()
config.read('../src/auth.ini')
OUTPUT_FILE = config['default']['SpikeDB'].strip('"')
SERVICE_FILE = config['email']['ServiceFile'].strip('"')
DOMAIN = config['zendesk']['Domain'].strip('"')
AUTH = config['zendesk']['Credentials'].strip('"')
SENDER = config['email']['Sender'].strip('"')
RECIPIENT = config['email']['Recipient'].strip('"')


def main(logger):

    # load up the database for reading and writing to
    # check if output file exists and create it if it doesn't
    logger.info('Loading Database...')
    columns = list(range(24))
    TicketCount = pd.DataFrame(columns = columns)

    logger.info('Checking if Output File exists...')
    if os.path.exists(OUTPUT_FILE) == False:
        logger.warning('Output File not found. Creating...')
        TicketCount.to_csv(OUTPUT_FILE)
        logger.info('Output File ready for usage.')
    else:
        logger.info('Output File already exists. Proceeding with uhhhh stuff.')

    i = 1
    end_date = datetime.utcnow().replace(microsecond=0, second=0, minute=0) # get the current time and round it down
    start_date = (end_date + timedelta(hours= -i)) # subtract one hour into a second variable

    st0 = start_date.strftime("%Y-%m-%dT%H:%M:%SZ") #start date/time formatted for get request
    st1 = end_date.strftime("%Y-%m-%dT%H:%M:%SZ") #end date/time formatted for get request

    xdst0, xtst0 = start_date.strftime("%Y-%m-%d"), start_date.strftime("%H") #start date/time separately formatted for excel
    xtst1 = end_date.strftime("%H")
    # perform zendesk search of all tickets between those times
    logger.info('Searching tickets created today between ' + str(xtst0) + ':00 and ' + str(xtst1) + ':00...')

    # tickets = timed_search(DOMAIN, AUTH, start, now)
    def get_ticket_count(DOMAIN): #get request that shows ticket count between start_date and end_date
        logger.debug(AUTH[2:-1]) #uhhhhh not sure if this is needed here
        header = {"Authorization": "Basic {}".format(str(AUTH)[2:-1])}
        url = f"https://{DOMAIN}.zendesk.com/api/v2/search.json?query=type:ticket+created>{st0}+created<{st1}"

        try:
            r = requests.get(url, headers=header)
            return r
        except Exception as e:
            logger.exception(
            '{}\nError trying to call the Zendesk search API! '.format(str(e)))
        exit()

    TicketCountResult = get_ticket_count(DOMAIN)
    TicketCountResult = json.loads(TicketCountResult.text) #all info related to tickets, including tags, counts are stored inside this JSON

    logger.info(str(TicketCountResult['count']) + ' new tickets created today between ' + str(xtst0) + ':00 and ' + str(xtst1) + ':00...')
    logger.info('Updating Output File...')

    TicketCount.at[str(xdst0), int(xtst0)] = str(TicketCountResult["count"]) # return the 'count' of the result and store it in the database
    TicketCount.to_csv(OUTPUT_FILE) # update the ouput file
    exit()









# logger.info('{} New Tickets.'.format(count))

db_update(OUTPUT_FILE, db, count)
    except Exception as e:
        logger.exception(
            '{}\nError trying to call the Zendesk search API! '.format(str(e)))
        exit()
    # calculate whether the past hour was a spike
    if calc_spike(db, count):
        logger.warning(' SPIKE DETECTED! ')
        try:
            # if so, get a list of the 10 most frequent tags
            tags = frequent_tags(tickets)
            # and send out an email notification to the recipient
            send_report(RECIPIENT, tags)
            logger.info('Spike report emailed to <{}>.'.format(RECIPIENT))
        except Exception as e:
            logger.exception(
                '{}\nError trying to send an email report! '.format(str(e)))
            exit()
    return count

# takes a domain, start time, and end time as arguments
# returns a json object

def timed_search(dom, auth, start, finish):
    return tickets

# takes the output filename, database, and count of past hour as arguments
# saves out the updated db to the file

def db_update(file, db, count):
    pass

# takes the database, as well as count of the past hour as arguments
# returns a boolean of whether it qualifies as a spike

def calc_spike(db, count):
    return True

# takes the json output of tickets as an argument
# returns a list of the top 10 tags over the past hour

def frequent_tags(tickets):
    for ticket in tickets:
        for tag in tqdm(ticket['tags']):
            pass
    return tags

# takes the recipient email and frequent tags as arguments
# builds a message and sends it to the recipient

def send_report(to, tags, auth=None):
    pass


if __name__ =="__main__":
    # TODO: set logging level based on input
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    main(logger)