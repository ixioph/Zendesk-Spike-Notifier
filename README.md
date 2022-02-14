# Zendesk Spike Notifier
The Zendesk Spike Notifier is a tool that allows for greater efficiency when identifying and addressing large increases in incoming ticket volume. 

The tool is meant to be run as an hourly cron job, it connects to the Zendesk V2 API and pulls all tickets of a given subdomain that were created over the past hour and records the count. 

The count of each hour is compared to the mean of the counts of the same relative hour over the previous `N_HOURS` hours. If the count is greater than `(1+SPIKE_THRESHOLD)*column mean`, then the hour is considered to be a "Spike." 

Once designated a spike, the tool aggregates a list of the `N_TAGS` most frequently occuring tags from that hour. With that aggregated list, the tool sends an email notification (gmail client) to the `RECIPIENT` email address so that action may be taken by the agents. 

## Requirements
To run this tool, the following libraries first need to be installed: 
  * requests
  * pandas
  * smtplib


requests, pandas 

## Usage
To run the tool, simply navigate to ./scripts/ and run the following command: 
  * `python support_volume.py`

Usage relies on the file `/src/auth.ini` to run. An example is included with the repo, but here it is as well: 
```
[default]
SpikeDB = "../out/thePathToYourDatabase.csv"

[zendesk]
Domain = "yourZendeskDomain"
Credentials = "YOURZENDESKEMAIL@yourbiz.com/token:YOURZENDESKAPIKEY"

[email]
Sender = "theSendingEmail@yourbiz.com"
Password = "yourSendingEmailPassword"
Recipient = "theRecipientEmail@theirbiz.com"

[misc]
OmittedTags = ["list", "of", "tags", "to", "omit"]
```
## Modules 
There are 2 modules in the repo, `support_volume.py` and `ticket_counter.py`. In short, `support_volume.py` is the main driving script which performs the necessary ETL to determine whether or not there has been a spike over the last hour and notifies the email recipients. `ticket_counter.py` is the module used to poll the Zendesk database for the ticket count and generate the initial database.

### support_volume.py
`support_volume.py` requires the pandas library in order to be run. It first checks to see if their is an existing database of hourly volume, if not it calls the ticket_counter module and generates a fresh database. Otherwise, it gets the count of the tickets and compares it against the same hour over the past `N_HOURS` hours. If the volume exceeds the threshold set, it counts up the tags of all of the tickets and sends out an email notification with the offending tags included for diagnosis. 

#### Functions 
The `calc_spike()` function takes the database/pandas dataframe, the ticket count of the past hour, the current column/hour, and the spike threshold as arguments returns a boolean of whether it qualifies as a spike and the % increase over the mean.

```Python
def calc_spike(db, count, col, spike=SPIKE_THRESHOLD):
    threshold = db[col].mean()*(spike+1)
    return count > threshold, (count - db[col].mean()) / db[col].mean() * 100
```
The `frequent_tags()` function takes the json output of tickets as an argument (requests.get().text['results'], the number of tags to return, and a list of tags to omit from the search (i.e. - infrastructure tags) returns a list of the top N tags in the source ticket list
```Python
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
```

The `send_report()` function takes the recipient email, hourly count, and frequent tags as arguments auth should be a tuple containing the sender email id and sender email id password builds a message and sends it to the recipient
```Python
def send_report(to, count, tags, delta, auth = None, subject='Ticket Spike Alert!'):
    try:
        email = smtplib.SMTP('smtp.gmail.com', 587)
        email.starttls()

        email.login(auth[0], auth[1])

        message = ("Greetings Crunchyroll Humans, \n\n"
                "My calculations have detected the emergence of a potential spike in the past hour! \n\n"
                "We’ve received {} tickets in the past hour. \n"
                "This is an increase of {} % over our average for this hour over the past 6 months. \n\n"
                "Below you will find the most frequent tags over this past hour: \n{}").format(count, delta, tags)
        message = 'Subject: {}\n\n{}'.format(subject, message).encode('utf-8')

        email.sendmail(auth[0], to, message)
        email.quit()
    except Exception as e:
        print('ERROR: ', str(e))
        exit()
    return 0
```

### ticket_counter.py
Detailed description of ticket_counter.py

#### Functions 
The `run()` function... 

The `get_formatted_datetimes()` function...
```Python
def get_formatted_datetimes(t_delta):
  now = datetime.utcnow().replace(microsecond=0, second=0, minute=0)
  start_date = (now + timedelta(hours= -t_delta))
  st0 = start_date.strftime("%Y-%m-%dT%H:%M:%SZ") 
  sub_start_date = (start_date + timedelta(hours= 1))
  st1 = sub_start_date.strftime("%Y-%m-%dT%H:%M:%SZ") 
  xdst0, xtst0 = start_date.strftime("%Y-%m-%d"), start_date.strftime("%H") 
  xtst1 = now.strftime("%H")
  return st0, st1, xdst0, xtst0, 
```

The `get_ticket_count()` function...
```Python
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
```
