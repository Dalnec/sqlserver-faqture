import requests
import configparser

from base.db import update_venta_pgsql 
from urllib3.exceptions import InsecureRequestWarning

config = configparser.ConfigParser()
config.read('config.ini')

api_url = config['API']['API_URL']
api_token = config['API']['API_TOKEN']

# Disable flag warning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def create_document(header_dics):
    "crea boletas y facturas"     
    url = api_url
    token = api_token
    _send_cpe(url, token, header_dics)

def _send_cpe(url, token, data):
    header = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(token)
    }
    cont = 0
    for venta in data:
        if cont == 0:
            response = requests.post(
                url, json=venta, headers=header, verify=False)        
            if response.status_code == 200:
                update_venta_pgsql(int(venta['id_venta']))
                print(response.content)
            else:
                print(response.status_code)
        cont += 1