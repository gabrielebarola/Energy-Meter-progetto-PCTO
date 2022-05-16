from MicroWebSrv2 import MicroWebSrv2
from time import sleep_ms, time
from machine import Timer, RTC
from micropython import const
from random import randint
from src.logger import Logger
import json

_mins = const(5)
_secs = const(5 * 60)
_diff = const(946684800)

readings = [0.0, 0.0, 0.0, 0.0]
logger = Logger("prova1db")


def OnWebSocketTextMessage(websocket, msg):
    if msg == "update_data":
        websocket.SendTextMessage(json.dumps({"type": "measures", "content": readings}))
    elif "chart-from-to" in msg:
        splitted = msg.split(":")
        from_timestamp = int(splitted[1]) - _diff
        to_timestamp = int(splitted[2]) - _diff
        websocket.SendTextMessage(json.dumps({"type": "chart-init"}))

        for i in range((to_timestamp - from_timestamp) // _secs):
            to_get = from_timestamp + ((i + 1) * _secs)
            data = logger.get(str(to_get).encode())

            websocket.SendTextMessage(
                json.dumps(
                    {
                        "type": "chart-append",
                        "content": {"timestamp": to_get + _diff, "measures": data},
                    }
                )
            )

        websocket.SendTextMessage(json.dumps({"type": "chart-init-stop"}))

    elif "chart" in msg:
        splitted = msg.split(":")
        timestamp = int(splitted[1]) - _diff
        websocket.SendTextMessage(
            json.dumps(
                {
                    "type": "chart-add",
                    "content": {
                        "timestamp": timestamp + _diff,
                        "measures": logger.get(str(timestamp).encode()),
                    },
                }
            )
        )


def OnWebSocketAccepted(server, websocket):
    websocket.OnTextMessage = OnWebSocketTextMessage


def log(readings):
    print(readings)


def main():

    rtc = RTC()
    print(rtc.datetime())

    to_init = True  # init the timer only when time is multiple of _mins

    server = MicroWebSrv2()

    sockets = server.LoadModule("WebSockets")
    sockets.OnWebSocketAccepted = OnWebSocketAccepted

    server.NotFoundURL = "/"
    server.SetEmbeddedConfig()

    server.StartManaged()

    logging_timer = Timer(0)

    try:
        while True:
            # generate fake readings
            readings[0] = 230 + randint(-100, 100) / 10
            new_current = readings[1] + randint(-10, 10) / 10
            if new_current < 0:
                new_current = 0
            if new_current > 25:
                new_current = 25
            readings[1] = new_current
            readings[2] = 50 + randint(-10, 10) / 10

            # evaluates if minutes is multiple of 15 to start the timer
            if to_init and not rtc.datetime()[5] % _mins:
                print("entered")
                logger.log(time(), readings)
                logging_timer.init(
                    period=(_mins * 60000),
                    callback=lambda t: logger.log(time(), readings),
                )
                to_init = False

            sleep_ms(500)
    except KeyboardInterrupt:
        logging_timer.deinit()
        server.Stop()
        logger.close()


main()
