# support_volume.py
# This script is designed to be run once an hour
# it counts the Zendesk tickets created over the past hour
# and saves the information to a database
# in the event of a "spike" (abnormally high ticket volume)
# an email is sent to <reporters>

import configparser
import pandas as pd
import logging
import smtplib
import json
import os
import TicketCounter as TC


config = configparser.RawConfigParser()
config.read('../src/auth.ini')
OUTPUT_FILE = config['default']['SpikeDB'].strip('"')
DOMAIN = config['zendesk']['Domain'].strip('"')
AUTH = config['zendesk']['Credentials'].strip('"')
SENDER = config['email']['Sender'].strip('"')
PASS = config['email']['Password'].strip('"')
RECIPIENT = config['email']['Recipient'].strip('"')
OMITTED = config['misc']['OmittedTags']
N_HOURS = 4380
SPIKE_THRESHOLD = 0.6

def main(logger):

    # load up the database for reading and writing to
    # check if output file exists and create it if it doesn't
    logger.warning('Loading Database...')
    columns = list(range(24))
    TicketCount = pd.DataFrame(columns = columns)

    logger.warning('Checking if Output File exists...')
    if os.path.exists(OUTPUT_FILE) == False:
        logger.warning('Output File not found. Creating...')
        TC.run(logger, OUTPUT_FILE, N_HOURS, DOMAIN, AUTH)
        logger.warning('Output File generated and ready for usage.')
    else:
        logger.warning('Output File already exists. Proceeding with uhhhh stuff.')

    st0, st1, xdst0, xtst0, xtst1 = TC.get_formatted_datetimes(1)

    try:
        # perform zendesk search of all tickets between those times
        logger.warning('Searching tickets created today between {}:00 and {}:00...'.format(xtst0,xtst1))

        TicketCountResult = TC.get_ticket_count(DOMAIN, AUTH, st0, st1)
        TicketCountResult = json.loads(TicketCountResult.text)

        TicketCountVar = TicketCountResult['count'] 
        logger.warning('{} new tickets created today between {}:00 and {}:00...'.format(TicketCountVar, xtst0,xtst1))
        logger.warning('Updating Output File...')

        # return the 'count' of the result and store it in the database
        TicketCount.at[str(xdst0), int(xtst0)] = str(TicketCountResult["count"]) 
        TicketCount.to_csv(OUTPUT_FILE)
    except Exception as e: 
        logger.warning('Error getting and storing ticket count, ', str(e))
        logger.exception('{}\nError trying to call the Zendesk search API! '.format(str(e)))
        exit()

    TicketCountHistory = pd.read_csv(OUTPUT_FILE) 
    spike,delta = calc_spike(TicketCountHistory, TicketCountVar, xtst0)
    spike = True
    logger.warning("Is there a spike? {}".format(spike))
    if spike:
        tags = frequent_tags(TicketCountResult['results'])
        logger.warning("These are the tags:\n {}".format(tags))
        try:
            logger.warning("Sending report to {}\n".format(RECIPIENT))
            send_report(RECIPIENT, TicketCountVar, tags, delta, (SENDER, PASS))
        except Exception as e:
            logger.exception('{}\nError sending the report!'.format(str(e)))
        logger.warning('SUCCESS')

# takes the database/pandas dataframe, the ticket count of the past hour, 
# the current column/hour, and the spike threshold as arguments
# returns a boolean of whether it qualifies as a spike and the % increase over the mean

def calc_spike(db, count, col, spike=SPIKE_THRESHOLD):
    threshold = db[col].mean()*(spike+1)
    return count > threshold, (count - db[col].mean()) / db[col].mean() * 100

# takes the json output of tickets as an argument (requests.get().text['results'], 
# the number of tags to return, and a list of tags to omit from the search (i.e. - infrastructure tags)
# returns a list of the top N tags in the source ticket list

def frequent_tags(tickets, n_tags=10, omitted=OMITTED):
    tags = {}
    for ticket in tickets:
        for tag in ticket['tags']:
            if tag in omitted:
                continue
            if tag not in tags.keys():
                tags[tag] = 1
            else:
                tags[tag] += 1
    top_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)[:n_tags]
    return top_tags

# takes the recipient email, hourly count, and frequent tags as arguments
# auth should be a tuple containing the sender email id and sender email id password
# builds a message and sends it to the recipient

def send_report(to, count, tags, delta, auth = None, subject='Ticket Spike Alert!'):
    try:
        # creates SMTP session
        email = smtplib.SMTP('smtp.gmail.com', 587)

        # start TLS for security
        email.starttls()

        # authentication
        email.login(auth[0], auth[1])

        # craft the message
        message = ("Greetings Crunchyroll Humans, \n\n"
                "My calculations have detected the emergence of a potential spike in the past hour! \n\n"
                "We’ve received {} tickets in the past hour. \n"
                "This is an increase of {} % over our average for this hour over the past 6 months. \n\n"
                "Below you will find the most frequent tags over this past hour: \n{}").format(count, delta, tags)
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