# SMARTAPI-PYTHON

SMARTAPI-PYTHON is a Python library for dealing AMX,that is a set of REST-like HTTP APIs that expose many capabilities required to build stock market investment and trading platforms. It lets you execute orders in real time.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install smartapi-python.

```bash
pip install smartapi-python
```

## Usage

```python
# package import statement
from smartapi.smartConnect import SmartConnect

#create object of call
obj=SmartConnect()

#login api call

data = obj.generateSession("D88311","Angel@444")
refreshToken= data['data']['refreshToken']

#fetch User Profile
userProfile= obj.getProfile(refreshToken)
#place order
try:
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
    orderId=obj.placeOrder(orderparams)
    print("The order id is: {}".format(orderId))
except Exception as e:
    print("Order placement failed: {}".format(e.message))

#logout
try:
    logout=obj.terminateSession('D88311')
    print("Logout Successfull")
except Exception as e:
    print("Logout failed: {}".format(e.message))


License
MIT


