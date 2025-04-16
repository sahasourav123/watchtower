import os
import requests
import query_engine as qe

def alert_manager(monitor, state: str):
    _channel_count = len(monitor['alerts'])
    if _channel_count == 0:
        return
    elif _channel_count == 1:
        channel_ids = monitor['alerts'][0]
    else:
        channel_ids = monitor['alerts']

    alert_channels = qe.get_alert_channel({'channel_id': channel_ids, 'is_active': True})

    if not alert_channels.empty:
        for idx, channel in alert_channels.iterrows():
            recipient = channel['recipient']
            if channel['channel_type'] == 'webhook':
                webhook_alert(monitor, recipient, state)
            elif channel['channel_type'] == 'email':
                email_alert(monitor, recipient['mail'], state)
            elif channel['channel_type'] == 'slack':
                slack_alert(monitor, recipient['channel_id'], state)

def webhook_alert(monitor: dict, recipient: dict, state):
    payload = {
        'monitor_id': monitor['monitor_id'],
        'monitor_name': monitor['monitor_name'],
        'monitor_type': monitor['monitor_type'],
        'monitor_body': monitor['monitor_body'],
        'state': state,
    }
    response = requests.post(
        recipient['url'], json=payload,
        headers={'Content-Type': 'application/json', **recipient.get('headers', {})},
        timeout=5
    )
    print(response.text)

def email_alert(monitor: dict, email_id: str, state):
    url = os.getenv('EMAIL_BOT_URL')

    payload = {
        'from': {
            'address': os.getenv('EMAIL_BOT_ADDRESS')
        },
        'to': [{
                'email_address': {
                    'address': email_id,
                    'name': monitor['user_code']
                }
            }],
        'subject': f"[Watchtower] Uptime Alert on Monitor #{monitor['monitor_id']}",
        'htmlbody': f"<div>{monitor['monitor_name']} (Monitor #{monitor['monitor_id']}) is {state}.<p>{monitor['monitor_body']}</p></div>"
    }

    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': os.getenv('EMAIL_BOT_TOKEN'),
    }

    response = requests.post(url, json=payload, headers=headers)
    print(response.text)

def slack_alert(monitor: dict, channel_id: str, state):
    url = "https://slack.com/api/chat.postMessage"

    payload = {
        'channel': channel_id,
        'text': f"""{monitor['monitor_name']} (Monitor #{monitor['monitor_id']}) is {state}.
        {monitor['monitor_body']}"""
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("SLACK_BOT_TOKEN")}'
    }

    response = requests.post(url, json=payload, headers=headers)
    print(response.text)
