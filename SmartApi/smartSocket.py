# Import WebSocket client library
from websocket import create_connection
# Connect to WebSocket API and subscribe to trade feed for XBT/USD and XRP/USD
import _thread
import time
import ssl
import six
import json
import base64
import binascii
import re
import struct

url="wss://omnefeeds.angelbroking.com/NestHtml5Mobile/socket/stream"
FEED_TOKEN='1096783294'
CLIENT_CODE='S212741'
MODE_FULL = "full"
MODE_QUOTE = "quote"
MODE_LTP = "ltp"
EXCHANGE_MAP = {
    "nse": 1,
    "nfo": 2,
    "cds": 3,
    "bse": 4,
    "bfo": 5,
    "bsecds": 6,
    "mcx": 7,
    "mcxsx": 8,
    "indices": 9
}
import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time

def on_message(ws, message):
    print("Printing the Messsage",message)
    #print(message)
    # data= binascii.a2b_uu(message)
    # print(data)
    # base64_message =binascii.a2b_base64(message)
    # temp=bytes(message,encoding='ascii')
    # print("temp",temp)
    # resp=temp.decode()
    resp=base64.b64decode(message)
    print("response",resp)
    ws.close()
    
def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        _req='{"task":"cn","channel":"","token":"' + FEED_TOKEN + '","user": "' + CLIENT_CODE + '","acctid":"' + CLIENT_CODE + '"}';
        ws.send(_req)
        strwatchlistscrips = "nse_cm|2885&nse_cm|1594&nse_cm|11536";
        _req = '{"task":"cn","channel":"'+strwatchlistscrips+'","token":"' + FEED_TOKEN + '","user": "' + CLIENT_CODE + '","acctid":"' + CLIENT_CODE + '"}'; 
        ws.send(_req)
        
        
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(url,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    ws.close()


