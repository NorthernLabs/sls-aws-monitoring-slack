import json
import os
import urllib.request

# NOTE: make sure to keep the list updated
ACCOUNT_NAMES = {
    "PTI - bridge": "282732021601",
    "PTI - dev": "959419304096",
    "PTI - prod": "581733511217",
    "PTI - shared": "042601855799",
    "MM - bridge": "662038480128",
    "MM - dev": "232250609916",
    "MM - prod": "391107411852",
    "MM - shared": "165402626052",
    "NL - bridge": "200663706791",
    "NL - dev": "227102687118",
    "NL - jeff_lee": "772101405989",
    "NL - michael_pavlovsky": "847408358735",
    "NL - razvan_draghici": "732667860842",
    "NL - lemmax_dev": "573354913153",
    "NL - lemmax_prod": "516595672765",
}

def format_message(data):
    severity_level = get_severity_level(data['detail']['severity'])
    account_name = get_account_name(data['detail']['accountId'])
    payload = {
        'username': 'GuardDuty Finding',
        'icon_emoji': ':guardduty:',
        'text': '{} GuardDuty Finding in {}'.format(severity_level['mention'], data['detail']['region']),
        'attachments': [
            {
                'fallback': 'Detailed information on GuardDuty Finding.',
                'color': severity_level['color'],
                'title': data['detail']['title'],
                'text': data['detail']['description'],
                'fields': [
                    {
                        'title': 'Account Name',
                        'value': account_name,
                        'short': True
                    },
                    {
                        'title': 'Account ID',
                        'value': data['detail']['accountId'],
                        'short': True
                    },
                    {
                        'title': 'Severity',
                        'value': severity_level['label'],
                        'short': True
                    },
                    {
                        'title': 'Type',
                        'value': data['detail']['type'],
                        'short': False
                    }
                ]
            }
        ]
    }
    return payload

def get_severity_level(severity):
    # ref: http://docs.aws.amazon.com/guardduty/latest/ug/guardduty_findings.html#guardduty_findings-severity
    if severity == 0.0:
        level = {'label': 'Information', 'color': 'good', 'mention': ''}
    elif 0.1 <= severity <= 3.9:
        level = {'label': 'Low', 'color': 'warning', 'mention': ''}
    elif 4.0 <= severity <= 6.9:
        level = {'label': 'Medium', 'color': 'warning', 'mention': '<!here>'}
    elif 7.0 <= severity <= 8.9:
        level = {'label': 'High', 'color': 'danger', 'mention': '<!channel>'}
    elif 9.0 <= severity <= 10.0:
        level = {'label': 'Critical', 'color': 'danger', 'mention': '<!channel>'}
    else:
        level = {'label': 'Unknown', 'color': '#666666', 'mention': ''}
    return level

def get_account_name(account_id):
    for name, id in ACCOUNT_NAMES.items():
        if id == account_id:
            return name
    return "⚠️ Unknown ⚠️"

def notify_slack(url, payload):
    data = json.dumps(payload).encode('utf-8')
    method = 'POST'
    headers = {'Content-Type': 'application/json'}

    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(request) as response:
        return response.read().decode('utf-8')

def lambda_handler(event, context):
    webhook_urls = os.environ['WEBHOOK_URLS']
    payload = format_message(event)
    responses = []
    for webhook_url in webhook_urls.split(','):
        responses.append(notify_slack(webhook_url, payload))
    return responses
