# import websocket
# import ssl
# import base64
# ws = websocket.WebSocket()
# from websocket import create_connection
# FEED_TOKEN='125645827'
# CLIENT_CODE='S212741'
# ws= create_connection("wss://omnefeeds.angelbroking.com/NestHtml5Mobile/socket/stream",sslopt={"cert_reqs": ssl.CERT_NONE})
# _req='{"task":"cn","channel":"","token":"' + FEED_TOKEN + '","user": "' + CLIENT_CODE + '","acctid":"' + CLIENT_CODE + '"}';
# ws.send(_req)
# strwatchlistscrips = "nse_cm|2885&nse_cm|1594&nse_cm|11536";
# _req = '{"task":"cn","channel":"'+strwatchlistscrips+'","token":"' + FEED_TOKEN + '","user": "' + CLIENT_CODE + '","acctid":"' + CLIENT_CODE + '"}'; 
# ws.send(_req)
# print("Sent")
# print("Receiving...")
# result =  ws.recv()
# print(result)
# #str = unicode(str, errors='ignore')
# print("Received '%s'" % result.decode(encoding="utf-8"))
# ws.close()

import asyncio
import websockets

async def message():
    async with websockets.connect("wss://omnefeeds.angelbroking.com/NestHtml5Mobile/socket/stream") as socket:
        await socket.send({"task":"cn","channel":"","token":"' + FEED_TOKEN + '","user": "' + CLIENT_CODE + '","acctid":"' + CLIENT_CODE + '"})
        strwatchlistscrips = "nse_cm|2885&nse_cm|1594&nse_cm|11536"
        await socket.send({"task":"cn","channel":strwatchlistscrips,"token":"' + FEED_TOKEN + '","user": "' + CLIENT_CODE + '","acctid":"' + CLIENT_CODE + '"})
        print(await socket.recv())

asyncio.get_event_loop().run_until_complete(message())
