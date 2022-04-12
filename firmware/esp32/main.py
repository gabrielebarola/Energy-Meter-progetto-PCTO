from MicroWebSrv2 import MicroWebSrv2
from time import sleep_ms, time
from machine import Timer, RTC
from micropython import const

_mins = const(15)

def OnWebSocketTextMessage(websocket, msg):
    if msg == 'update_data':
        websocket.SendTextMessage(str(time()))

def OnWebSocketAccepted(server, websocket):
    print(f"aperto {websocket.Request.UserAddress}")
    websocket.OnTextMessage = OnWebSocketTextMessage

def log(readings):
    print(readings)

def main():
    readings = {
        "secs": time()
    }
    
    rtc = RTC()
    print(rtc.datetime())

    to_init = True #init the timer only when time is multiple of _mins

    server = MicroWebSrv2()

    sockets = server.LoadModule("WebSockets")
    sockets.OnWebSocketAccepted = OnWebSocketAccepted

    server.NotFoundURL = "/"
    server.SetEmbeddedConfig()

    server.StartManaged()

    logging_timer = Timer(0)

    try:
        while True:
            #evaluates if minutes is multiple of 15 to start the timer
            if to_init and not rtc.datetime()[5]%_mins:
                print("entered")
                log(readings)
                logging_timer.init(period=(_mins*60000), callback= lambda t: log(readings))
                to_init = False

            readings["secs"] = time()
            sleep_ms(500)
    except KeyboardInterrupt:
        logging_timer.deinit()
        server.Stop()


main()