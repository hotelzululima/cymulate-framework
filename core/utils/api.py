import requests
import json

BASE_URI = "https://api.app.cymulate.com/v1"
HEADERS = {
    'accept': '*/*',
    'x-token': 'YOUR_TOKEN',
}


def get_executions(token: str):
    """
    This endpoint will retrieve a list of Advanced Scenarios executions
    """
    HEADERS['x-token'] = token
    response = requests.get(f'{BASE_URI}/purple-team/executions/', headers=HEADERS)
    return response.json()


def get_templates(token: str, public: bool = True):
    """
    This endpoint will retrieve a list of Advanced Scenarios templates
    """
    HEADERS['x-token'] = token
    response = requests.get(f'{BASE_URI}/purple-team/templates/', headers=HEADERS)
    if public:
        return [t for t in response.json()['data'] if t['public']]
    else:
        return response.json()


def save_results(results: dict):
    """
    Save the result to a json file
    """
    with open('results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
