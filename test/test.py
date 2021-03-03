from smartapi import SmartConnect

#---------for smartExceptions---------
#import smartapi.smartExceptions
#or
#from smartapi import smartExceptions

smartApi =SmartConnect(api_key="Your Api Key")

login = smartApi.generateSession('Your Client Id', 'Your Password')

refreshToken = login['data']['refreshToken']

feedToken = smartApi.getfeedToken()

smartApi.getProfile(refreshToken)

smartApi.generateToken(refreshToken)

orderparams = {
    "variety": "NORMAL",
    "tradingsymbol": "SBIN-EQ",
    "symboltoken": "3045",
    "transactiontype": "BUY",
    "exchange": "NSE",
    "ordertype": "LIMIT",
    "producttype": "INTRADAY",
    "duration": "DAY",
    "price": "19500",
    "squareoff": "0",
    "stoploss": "0",
    "quantity": "1"
}
orderid = smartApi.placeOrder(orderparams)

modifyparams = {
    "variety": "NORMAL",
    "orderid": orderid,
    "ordertype": "LIMIT",
    "producttype": "INTRADAY",
    "duration": "DAY",
    "price": "19500",
    "quantity": "1",
    "tradingsymbol":"SBIN-EQ",
    "symboltoken":"3045",
    "exchange":"NSE"
}
smartApi.modifyOrder(modifyparams)

smartApi.cancelOrder(orderid, "NORMAL")

smartApi.orderBook()

smartApi.tradeBook()

smartApi.rmsLimit()

smartApi.position()

smartApi.holding()

exchange = "NSE"
tradingsymbol = "SBIN-EQ"
symboltoken = 3045
smartApi.ltpData("NSE", "SBIN-EQ", "3045")

params={
    "exchange": "NSE",
    "oldproducttype":"DELIVERY",
    "newproducttype": "MARGIN",
    "tradingsymbol": "SBIN-EQ",
    "transactiontype":"BUY",
    "quantity":1,
    "type":"DAY"

}

smartApi.convertPosition(params)
gttCreateParams={
	    "tradingsymbol" : "SBIN-EQ",
	    "symboltoken" : "3045",
	    "exchange" : "NSE", 
	    "producttype" : "MARGIN",
	    "transactiontype" : "BUY",
	    "price" : 100000,
	    "qty" : 10,
	    "disclosedqty": 10,
	    "triggerprice" : 200000,
	    "timeperiod" : 365
	}
rule_id=smartApi.gttCreateRule(gttCreateParams)

gttModifyParams={
		"id": rule_id,
		"symboltoken":"3045",
		"exchange":"NSE",
		"price":19500,
		"quantity":10,
		"triggerprice":200000,
		"disclosedqty":10,
		"timeperiod":365
	}
modified_id=smartApi.gttModifyRule(gttModifyParams)

cancelParams={
		"id": rule_id, 
		"symboltoken":"3045",
		"exchange":"NSE"
		}	
    
cancelled_id=smartApi.gttCancelRule(cancelParams)

smartApi.gttDetails(rule_id)

smartApi.gttLists('List of status',<page>,<count>)

smartApi.terminateSession('Your Client Id')

## Websocket Programming

from smartapi import WebSocket
FEED_TOKEN=feedToken 
CLIENT_CODE="Your Client Id"
token=None
ss = WebSocket(FEED_TOKEN, CLIENT_CODE)
def on_tick(ws, tick):
    print("Ticks: {}".format(tick))

def on_connect(ws, response):
    ws.send_request(token)

def on_close(ws, code, reason):
    ws.stop()

# Assign the callbacks.
ss.on_ticks = on_tick
ss.on_connect = on_connect
ss.on_close = on_close

ss.connect( )