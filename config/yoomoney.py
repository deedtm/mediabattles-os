from . import config

CLIENT_ID = config.get('yoomoney', 'client_id')
CLIENT_SECRET = config.get('yoomoney', 'client_secret')
REDIRECT_URI = config.get('yoomoney', 'redirect_uri')
SCOPE = config.get('yoomoney', 'scope').split(', ')
TOKEN = config.get('yoomoney', 'access_token')

DESCRIPTION = config.get('yoomoney', 'description')
WALLET_NUMBER = config.get('yoomoney', 'wallet_number')
FORM = config.get('yoomoney', 'quickpay_form')
