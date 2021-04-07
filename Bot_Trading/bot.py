import websocket, json, pprint, talib, numpy 
import config
from binance.client import Client
from binance.enums import *


SOCKET = "wss://stream.binance.com:9443/ws/btceur@kline_1m"

PERIOD = 15
Tendance_Forte = 70
TRADE_SYMBOL = 'BTCEUR'
TRADE_QUANTITY = 0.005

highli = []
lowli = []

dans_le_portefeuille = False

client = Client(config.API_KEY, config.API_SECRET, tld='us')
client.API_URL = 'https://testnet.binance.vision/api'

def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True

    
def on_open(ws):
    print('Connexion Ouverte')

def on_close(ws):
    print('Connexion Fermée')

def on_message(ws, message):
    try:
        global highli,lowli, in_position
        print('Message Recu')
        json_message = json.loads(message)
        #pprint.pprint(json_message)
        candle = json_message['k']

        Low= float(candle['l'])
        High = float(candle['h'])
        highli += [High]
        lowli +=[Low]
        if len(highli) >  PERIOD:
               
                np_high = numpy.array(highli)
                np_low = numpy.array(lowli)
               
                print(highli)
                print(lowli)
                print(np_high)
                print(np_low)
                aroondown, aroonup = talib.AROON(np_high,np_low, PERIOD)
                print("Tous les aroon calculé")
                print("aroondown :",aroondown)
                print("aroonup :",aroonup)
                last_aroondown = aroondown[-1]
                last_aroonup = aroonup[-1]


                if last_aroonup > last_aroondown and last_aroonup > Tendance_Forte :
                    if not dans_le_portefeuille:
                        print("On achète car tendance haussière")
                        # ordre d'achat de la crypto
                        order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                        if order_succeeded:
                            in_position = True
                    else:
                        print("Déja acheté, on attend la vente avant de racheter")
                
                if last_aroondown > last_aroondown and last_aroondown > Tendance_Forte:
                    if dans_le_portefeuille:
                        print("On vend car tendance à la baisse")
                        order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                        if order_succeeded:
                            in_position = False
                    else:
                        print("On ne peut pas vendre la crypto avant de l'avoir acheté")
    except Exception as e:
        print(e)
            
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()