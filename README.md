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
Brief module explanation. 

## Functions 
Brief function explanations
