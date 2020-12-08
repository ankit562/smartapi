
import six
import sys
import time
import json
import struct
import logging
import threading
import base64
import zlib
from datetime import datetime
from twisted.internet import reactor, ssl
from twisted.python import log as twisted_log
from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory, connectWS


class SmartSocketClientProtocol(WebSocketClientProtocol):
    PING_INTERVAL = 2.5
    KEEPALIVE_INTERVAL = 5

    _ping_message = ""
    _next_ping = None
    _next_pong_check = None
    _last_pong_time = None
    _last_ping_time = None

    def __init__(self, *args, **kwargs):
        super(SmartSocketClientProtocol,self).__init__(*args,**kwargs)
    
    def onConnect(self, response):  # noqa
        """Called when WebSocket server connection was established"""
        self.factory.ws = self

        if self.factory.on_connect:
            self.factory.on_connect(self, response)
    
    def onOpen(self):
        # send ping
        self._loop_ping()
        # init last pong check after X seconds
        self._loop_pong_check()

        if self.factory.on_open:
            self.factory.on_open(self)

    
    def onMessage(self, payload, is_binary):  # noqa
        #print("""Called when text or binary message is received.""",payload,is_binary)
        if self.factory.on_message:
            self.factory.on_message(self, payload, is_binary)
        

    def onClose(self, was_clean, code, reason):  # noqa
        """Called when connection is closed."""
        if not was_clean:
            if self.factory.on_error:
                self.factory.on_error(self, code, reason)

        if self.factory.on_close:
            self.factory.on_close(self, code, reason)
        # Cancel next ping and timer
        self._last_ping_time = None
        self._last_pong_time = None

        if self._next_ping:
            self._next_ping.cancel()

        if self._next_pong_check:
            self._next_pong_check.cancel()

    def onPong(self, response):  # noqa
        """Called when pong message is received."""
        if self._last_pong_time and self.factory.debug:
            log.debug("last pong was {} seconds back.".format(time.time() - self._last_pong_time))

        self._last_pong_time = time.time()

        if self.factory.debug:
            log.debug("pong => {}".format(response))

    """
    Custom helper and exposed methods.
    """
    def _loop_ping(self): # noqa
        """Start a ping loop where it sends ping message every X seconds."""
        if self.factory.debug:
            log.debug("ping => {}".format(self._ping_message))
            if self._last_ping_time:
                log.debug("last ping was {} seconds back.".format(time.time() - self._last_ping_time))

        # Set current time as last ping time
        self._last_ping_time = time.time()
        # Send a ping message to server
        self.sendPing(self._ping_message)

        # Call self after X seconds
        self._next_ping = self.factory.reactor.callLater(self.PING_INTERVAL, self._loop_ping)

    def _loop_pong_check(self):
        """
        Timer sortof to check if connection is still there.
        Checks last pong message time and disconnects the existing connection to make sure it doesn't become a ghost connection.
        """
        if self._last_pong_time:
            # No pong message since long time, so init reconnect
            last_pong_diff = time.time() - self._last_pong_time
            if last_pong_diff > (2 * self.PING_INTERVAL):
                if self.factory.debug:
                    log.debug("Last pong was {} seconds ago. So dropping connection to reconnect.".format(
                        last_pong_diff))
                # drop existing connection to avoid ghost connection
                self.dropConnection(abort=True)

        # Call self after X seconds
        self._next_pong_check = self.factory.reactor.callLater(self.PING_INTERVAL, self._loop_pong_check)

class SmartSocketClientFactory(WebSocketClientFactory):
    protocol = SmartSocketClientProtocol

    def __init__(self, *args, **kwargs):
        """Initialize with default callback method values."""
        self.debug = False
        self.ws = None
        self.on_open = None
        self.on_error = None
        self.on_close = None
        self.on_message = None
        self.on_connect = None


        super(SmartSocketClientFactory, self).__init__(*args, **kwargs)


class SmartSocket(object):
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
    ROOT_URI='wss://omnefeeds.angelbroking.com/NestHtml5Mobile/socket/stream'
    feed_token=None
    client_code=None
    def __init__(self, FEED_TOKEN, CLIENT_CODE, debug=False, root=None):
        self.root = root or self.ROOT_URI
        self.feed_token= FEED_TOKEN
        self.client_code= CLIENT_CODE
        
        
        # Debug enables logs
        self.debug = debug

        # Placeholders for callbacks.
        self.on_ticks = None
        self.on_open = None
        self.on_close = None
        self.on_error = None
        self.on_connect = None
        self.on_message = None

    def _create_connection(self, url, **kwargs):
        """Create a WebSocket client connection."""
        self.factory = SmartSocketClientFactory(url, **kwargs)

        # Alias for current websocket connection
        self.ws = self.factory.ws

        self.factory.debug = self.debug

        # Register private callbacks
        self.factory.on_open = self._on_open
        self.factory.on_error = self._on_error
        self.factory.on_close = self._on_close
        self.factory.on_message = self._on_message
        self.factory.on_connect = self._on_connect


    def connect(self, threaded=False, disable_ssl_verification=False, proxy=None):
        #print("Connect")
        self._create_connection(self.ROOT_URI)
        
        context_factory = None
        #print(self.factory.isSecure,disable_ssl_verification)
        if self.factory.isSecure and not disable_ssl_verification:
            context_factory = ssl.ClientContextFactory()
        #print("context_factory",context_factory)
        connectWS(self.factory, contextFactory=context_factory, timeout=30)

        # Run in seperate thread of blocking
        opts = {}

        # Run when reactor is not running
        if not reactor.running:
            if threaded:
                #print("inside threaded")
                # Signals are not allowed in non main thread by twisted so suppress it.
                opts["installSignalHandlers"] = False
                self.websocket_thread = threading.Thread(target=reactor.run, kwargs=opts)
                self.websocket_thread.daemon = True
                self.websocket_thread.start()
            else:
                reactor.run(**opts)

    def is_connected(self):
        #print("Check if WebSocket connection is established.")
        if self.ws and self.ws.state == self.ws.STATE_OPEN:
            return True
        else:
            return False

    def _close(self, code=None, reason=None):
        #print("Close the WebSocket connection.")
        if self.ws:
            self.ws.sendClose(code, reason)

    def close(self, code=None, reason=None):
        """Close the WebSocket connection."""
        self._close(code, reason)

    def stop(self):
        """Stop the event loop. Should be used if main thread has to be closed in `on_close` method.
        Reconnection mechanism cannot happen past this method
        """
        #print("stop")
        reactor.stop()

    def send_request(self,token):
        strwatchlistscrips = token #dynamic call
        
        try:
            #print("Inside")
            request={"task":"cn","channel":"","token":self.feed_token,"user":self.client_code,"acctid":self.client_code}
            self.ws.sendMessage(
                six.b(json.dumps(request))
            )
            #print(request)
            request={"task":"mw","channel":strwatchlistscrips,"token":self.feed_token,"user":self.client_code,"acctid":self.client_code}
            #print(request)
            #request={"task":"cn","channel":token_scripts,"token":self.feed_token,"user":self.client_code,"acctid":self.client_code} //dynamic call
            self.ws.sendMessage(
                six.b(json.dumps(request))
            )
            #print(request)
            return True
        except Exception as e:
            self._close(reason="Error while request sending: {}".format(str(e)))
            raise
        
    def _on_connect(self, ws, response):
        self.ws = ws
        if self.on_connect:
            self.on_connect(self, response)

    def _on_close(self, ws, code, reason):
        """Call `on_close` callback when connection is closed."""
        log.debug("Connection closed: {} - {}".format(code, str(reason)))

        if self.on_close:
            self.on_close(self, code, reason)

    def _on_error(self, ws, code, reason):
        """Call `on_error` callback when connection throws an error."""
        log.debug("Connection error: {} - {}".format(code, str(reason)))

        if self.on_error:
            self.on_error(self, code, reason)

    def _on_message(self, ws, payload, is_binary):
        """Call `on_message` callback when text message is received."""
        if self.on_message:
            self.on_message(self, payload, is_binary)

        # If the message is binary, parse it and send it to the callback.
        if self.on_ticks and is_binary and len(payload) > 4:
            self.on_ticks(self, self._parse_binary(payload))

        # Parse text messages
        if not is_binary:
            self._parse_text_message(payload)

    def _on_open(self, ws):
        if self.on_open:
            return self.on_open(self)

    def _parse_text_message(self, payload):
        """Parse text message."""
        # Decode unicode data
        if not six.PY2 and type(payload) == bytes:
            payload = payload.decode("utf-8")
            
            data =base64.b64decode(payload)
            

        try:
            data=zlib.decompress(data)
            print(data.decode("utf-8"))

        except ValueError:
   
            return

        def _parse_binary(self, bin):
            #print("""Parse binary data to a (list of) ticks structure.""")
            packets = self._split_packets(bin)  # split data to individual ticks packet
            data = []

            for packet in packets:
                instrument_token = self._unpack_int(packet, 0, 4)
                segment = instrument_token & 0xff  # Retrive segment constant from instrument_token

                divisor = 10000000.0 if segment == self.EXCHANGE_MAP["cds"] else 100.0

                # All indices are not tradable
                tradable = False if segment == self.EXCHANGE_MAP["indices"] else True
                try:
                    last_trade_time = datetime.fromtimestamp(self._unpack_int(packet, 44, 48))
                except Exception:
                    last_trade_time = None

                try:
                    timestamp = datetime.fromtimestamp(self._unpack_int(packet, 60, 64))
                except Exception:
                    timestamp = None

                d["last_trade_time"] = last_trade_time
                d["oi"] = self._unpack_int(packet, 48, 52)
                d["oi_day_high"] = self._unpack_int(packet, 52, 56)
                d["oi_day_low"] = self._unpack_int(packet, 56, 60)
                d["timestamp"] = timestamp

                # Market depth entries.
                depth = {
                    "buy": [],
                    "sell": []
                }

                # Compile the market depth lists.
                for i, p in enumerate(range(64, len(packet), 12)):
                    depth["sell" if i >= 5 else "buy"].append({
                        "quantity": self._unpack_int(packet, p, p + 4),
                        "price": self._unpack_int(packet, p + 4, p + 8) / divisor,
                        "orders": self._unpack_int(packet, p + 8, p + 10, byte_format="H")
                    })

                d["depth"] = depth

            data.append(d)

            return data

    def _unpack_int(self, bin, start, end, byte_format="I"):
        """Unpack binary data as unsgined interger."""
        return struct.unpack(">" + byte_format, bin[start:end])[0]

    def _split_packets(self, bin):
        """Split the data to individual packets of ticks."""
        # Ignore heartbeat data.
        if len(bin) < 2:
            return []

        number_of_packets = self._unpack_int(bin, 0, 2, byte_format="H")
        packets = []

        j = 2
        for i in range(number_of_packets):
            packet_length = self._unpack_int(bin, j, j + 2, byte_format="H")
            packets.append(bin[j + 2: j + 2 + packet_length])
            j = j + 2 + packet_length

        return packets
    

