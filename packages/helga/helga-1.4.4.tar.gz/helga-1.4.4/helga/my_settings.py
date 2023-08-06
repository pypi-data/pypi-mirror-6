SERVER = {
    'HOST': '66.6.152.52',
    'PORT': 443,
    'SSL': True,
    'USERNAME': 'helgabot',
    'PASSWORD': 'b!gL4nd',
}

CHANNELS = [
    ('#bottest',),
]
NICK = 'helgabot-dev'

ENABLED_PLUGINS = ['stfu', 'help', 'oneliner', 'manager', 'updates']

WEBHOOKS_CREDENTIALS = []

NEWRELIC_WEBHOOK_ANNOUNCE_CHANNEL = '#bottest'
NEWRELIC_API_KEY = '89c546ce2d34d281ed164f8c645d2a0d2c25be7dea1d00f'
NEWRELIC_ACCOUNT_ID = '49454'

FES_CONFLUENCE_USER = 'shaun.duncan'
FES_CONFLUENCE_PASS = 'One19@3#2'
#FES_CONFLUENCE_JSON_URL = 'http://intranet.cmgdigital.com/rest/prototype/1/content/21037618.json'
FES_CONFLUENCE_JSON_URL = 'http://intranet.cmgdigital.com/rest/prototype/1/content/21037618.json'
FES_CONFLUENCE_EDIT_URL = 'http://intranet.cmgdigital.com/pages/editpage.action?pageId=42611283'

JIRA_AUTH = ('sduncan', 'One19@3#2')
JIRA_REST_API = 'https://jira.cmgdigital.com/rest/api/latest/issue/{ticket}'
