from smartConnect import *
smartApi=SmartConnect()

#login Api

login=smartApi.generateSession('D88311','Angel@444')
refreshToken=login['data']['refreshToken']
smartApi.generateToken(refreshToken)
orderparams={
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
orderid=smartApi.placeOrder(orderparams)

modifyparams={
    "variety":"NORMAL",
    "orderid":orderid,
    "ordertype":"LIMIT",
    "producttype":"INTRADAY",
    "duration":"DAY",
    "price":"19500",
    "quantity":"1"
}
smartApi.modifyOrder(modifyparams)

smartApi.cancelOrder(orderid,"NORMAL")

smartApi.orderBook()
smartApi.tradeBook()
smartApi.rmsLimit()
smartApi.position()
smartApi.holding()
exchange="NSE"
tradingsymbol="SBIN-EQ"
symboltoken=3045
smartApi.ltpData("NSE","SBIN-EQ","3045" )