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
from datetime import datetime, timedelta
import datetime as dt
import configparser
import logging
import json
import pandas as pd
import requests
import os
import smtplib

config = configparser.RawConfigParser()
config.read('../src/auth.ini')
OUTPUT_FILE = config['default']['SpikeDB'].strip('"')
#SERVICE_FILE = config['email']['ServiceFile'].strip('"')
DOMAIN = config['zendesk']['Domain'].strip('"')
AUTH = config['zendesk']['Credentials'].strip('"')
SENDER = config['email']['Sender'].strip('"')
PASS = config['email']['Password'].strip('"')
RECIPIENT = config['email']['Recipient'].strip('"')


def main(logger):

    # load up the database for reading and writing to
    # check if output file exists and create it if it doesn't
    logger.warning('Loading Database...')
    columns = list(range(24))
    TicketCount = pd.DataFrame(columns = columns)

    logger.warning('Checking if Output File exists...')
    if os.path.exists(OUTPUT_FILE) == False:
        logger.warning('Output File not found. Creating...')
        TicketCount.to_csv(OUTPUT_FILE)
        logger.warning('Output File ready for usage.')
    else:
        logger.warning('Output File already exists. Proceeding with uhhhh stuff.')

    i = 1
    end_date = datetime.utcnow().replace(microsecond=0, second=0, minute=0) # get the current time and round it down
    start_date = (end_date + timedelta(hours= -i)) # subtract one hour into a second variable

    st0 = start_date.strftime("%Y-%m-%dT%H:%M:%SZ") #start date/time formatted for get request
    st1 = end_date.strftime("%Y-%m-%dT%H:%M:%SZ") #end date/time formatted for get request

    xdst0, xtst0 = start_date.strftime("%Y-%m-%d"), start_date.strftime("%H") #start date/time separately formatted for excel
    xtst1 = end_date.strftime("%H")
    # perform zendesk search of all tickets between those times
    logger.warning('Searching tickets created today between ' + str(xtst0) + ':00 and ' + str(xtst1) + ':00...')

    def get_ticket_count(DOMAIN): #get request that shows ticket count between start_date and end_date
        print(b64encode(AUTH.encode('utf-8'))[2:-1])
        header = {"Authorization": "Basic {}".format(str(b64encode(AUTH.encode('utf-8')))[2:-1])}
        print(header)
        url = "https://{}.zendesk.com/api/v2/search.json?query=type:ticket+created>{}+created<{}".format(DOMAIN, st0, st1)

        try:
            r = requests.get(url, headers=header)
            print(r)
            return r
            ## if r =/= 200 then puke out an exception
        except Exception as e:
            logger.exception(
            '{}\nError trying to call the Zendesk search API! '.format(str(e)))
            exit()

    TicketCountResult = get_ticket_count(DOMAIN)
    TicketCountResult = json.loads(TicketCountResult.text) #all info related to tickets, including tags, counts are stored inside this JSON

    TicketCountVar = TicketCountResult['count'] #int variable to use later
    logger.warning(str(TicketCountResult['count']) + ' new tickets created today between ' + str(xtst0) + ':00 and ' + str(xtst1) + ':00...')
    logger.warning('Updating Output File...')

    TicketCount.at[str(xdst0), int(xtst0)] = str(TicketCountResult["count"]) # return the 'count' of the result and store it in the database
    TicketCount.to_csv(OUTPUT_FILE) # update the ouput file

    TicketCountHistory = pd.read_csv(OUTPUT_FILE) #the output file into a dataframe
    
    print("Is there a spike?", calc_spike(TicketCountHistory, TicketCountVar, xtst0))
    tags = frequent_tags(TicketCountResult['results'])
    print("These are the tags blablabla", tags)
    print("Sending report", send_report(RECIPIENT, TicketCountVar, tags, (SENDER, PASS)))


# takes the database/pandas dataframe, the ticket count of the past hour, 
# the current column/hour, and the spike threshold as arguments
# returns a boolean of whether it qualifies as a spike

def calc_spike(db, count, col, spike=0.6):
    if count > db[col].mean()*(spike+1):
    # there is a spike
        return True
    # else there is not a spike
    return False

# takes the json output of tickets as an argument (requests.get().text['results'], 
# the number of tags to return, and a list of tags to omit from the search (i.e. - infrastructure tags)
# returns a list of the top N tags in the source ticket list

def frequent_tags(tickets, n_tags=10, omitted=[]):
    ### TODO: implement n_tags functionality for output (low priority)
    tags = {}
    for ticket in tickets:
        for tag in ticket['tags']:
            if tag in omitted:
                continue
            if tag not in tags.keys():
                tags[tag] = 1
            else:
                tags[tag] += 1
    return tags
    

# takes the recipient email, hourly count, and frequent tags as arguments
# auth should be a tuple containing the sender email id and sender email id password
# builds a message and sends it to the recipient

def send_report(to, count, tags, auth = None, subject='Ticket Spike Alert!'):
    try:
        # creates SMTP session
        email = smtplib.SMTP('smtp.gmail.com', 587)

        # start TLS for security
        email.starttls()

        # Authentication
        email.login(auth[0], auth[1])
        message = "Greetings Crunchyroll Humans, \nMy calculations have detected the emergence of a potential spike in the past hour! \nWe’ve received {} tickets in the past hour, which is an increase of {} % over our average for this hour over the past 6 months. \nBelow you will find the most frequent tags over this past hour: \n{}".format(count, 'PLACEHOLDER', tags)
        message = 'Subject: {}\n\n{}'.format(subject, message).encode('utf-8')
        # send the email
        email.sendmail(auth[0], to, message)

        # terminate the session
        email.quit()
    except Exception as e:
        print('ERROR: ', str(e))
        exit()
    return 0

if __name__ =="__main__":
    # TODO: set logging level based on input
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    main(logger)