import requests


HEADERS = {
    'x-token': 'YOUR_TOKEN',
}


def get_executions(token: str):
    HEADERS['x-token'] = token
    response = requests.get('https://api.app.cymulate.com/v1/purple-team/executions/', headers=HEADERS)
    return response.json()
