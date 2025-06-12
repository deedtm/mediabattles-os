import json
import logging
import socketio
from .utils import get_donaters, save_donaters

class DonationAPI:
    def __init__(self, alert_widget_token: str):
        logging.info(f"Starting {self.__class__.__name__}...")
        sio = socketio.Client(reconnection=True, reconnection_delay=5)

        @sio.on('connect')
        def on_connect():
            sio.emit('add-user', {'token': alert_widget_token, "type": "alert_widget"})

        @sio.on('donation')
        def on_message(data):
            event = json.loads(data)
            self.__add_donater(event)
            
            
        sio.connect('wss://socket.donationalerts.ru:443', transports='websocket')
    
    
    def __add_donater(self, event: dict):
        donaters = get_donaters()
        
        username = event['username']
        amount = round(event['amount_main'])
        message = event['message']
        
        data = {'amount': amount, 'message': message}
        if username not in donaters:
            donaters.update({username: data})
        else:
            donaters[username] = data

        save_donaters(donaters)

        logging.info(f"Got {amount} RUB from {username}")
