# support_volume.py
# This script is designed to be run once an hour
# it counts the Zendesk tickets created over the past hour
# and saves the information to a database
# in the event of a "spike" (abnormally high ticket volume)
# an email is sent to <reporters>

from datetime import datetime, timedelta
import datetime as dt
from tqdm import tqdm
import configparser
import logging
import json
import pandas as pd

config = configparser.ConfigParser()
config.read('../src/auth.ini')
OUTPUT_FILE = config['default']['SpikeDB'].strip('"')
SERVICE_FILE = config['email']['ServiceFile'].strip('"')
DOMAIN = config['zendesk']['Domain'].strip('"')
AUTH = config['zendesk']['Credentials'].strip('"')
SENDER = config['email']['Sender'].strip('"')
RECIPIENT = config['email']['Recipient'].strip('"')


# NOTE: May be a better endpoint than the search API:
# https://developer.zendesk.com/api-reference/ticketing/tickets/tickets/#count-tickets
def main(logger):
    logger = logging.getLogger('Zendesk-Spike-Notifier')
    logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

# create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
    ch.setFormatter(formatter)

# add ch to logger
    logger.addHandler(ch)

# 'application' code
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('Warning, there is a Spike')
    logger.error('error message')

    # load up the database for reading and writing to
    db = None

    # get the current time
now = datetime.now()
current_date = now.date()
print('Date:', current_date)
print(type(current_date))

current_time = now.time()
print('Time', current_time)
print(type(current_time))
# subtract one hour into a second variable
start = datetime.now()
print('Current Time: ', current_time)
n = -1
now = dt.datetime.now()
delta = dt.timedelta(hours=n)
t = now.time()
print(t)
print((dt.datetime.combine(dt.date(1, 1, 1), t) + delta).time())

 # perform zendesk search of all tickets between those times
        logger.info('Searching tickets created over the past hour...')
        tickets = timed_search(DOMAIN, AUTH, start, now)
        # return the 'count' of the result and store it in the database
        count = tickets['count']
        logger.info('{} New Tickets.'.format(count))
        # update the database
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
