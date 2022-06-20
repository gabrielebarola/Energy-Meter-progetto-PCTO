from MicroWebSrv2 import MicroWebSrv2
from time import sleep_ms, time
from machine import Timer, RTC
from micropython import const
from src.database import Database
from src.logger import Logger
import json, gc

_mins = const(5)
_secs = const(5 * 60)
_diff = const(946684800)

db = Database("prova1db")
logger = Logger(freq=15, adc=32, en_i=19, en_v=21, en_p=22)
connected_sockets = []


def update_sockets():
    for socket in connected_sockets:
        socket.SendTextMessage(
            json.dumps({"type": "measures", "content": logger.readings})
        )


def OnWebSocketTextMessage(websocket, msg):
    if "chart-from-to" in msg:
        splitted = msg.split(":")
        from_timestamp = int(splitted[1]) - _diff
        to_timestamp = int(splitted[2]) - _diff
        websocket.SendTextMessage(json.dumps({"type": "chart-init"}))

        for i in range((to_timestamp - from_timestamp) // _secs):
            to_get = from_timestamp + ((i + 1) * _secs)
            data = db.get(str(to_get).encode())

            websocket.SendTextMessage(
                json.dumps(
                    {
                        "type": "chart-append",
                        "content": {"timestamp": to_get + _diff, "measures": data},
                    }
                )
            )

        websocket.SendTextMessage(json.dumps({"type": "chart-init-stop"}))


def OnWebSocketClosed(websocket):
    connected_sockets.remove(websocket)


def OnWebSocketAccepted(server, websocket):
    connected_sockets.append(websocket)
    websocket.OnTextMessage = OnWebSocketTextMessage
    websocket.OnClosed = OnWebSocketClosed


def log_data():
    t = time()
    db.log(t, logger.readings)

    for socket in connected_sockets:
        socket.SendTextMessage(
            json.dumps(
                {
                    "type": "chart-add",
                    "content": {
                        "timestamp": t + _diff,
                        "measures": logger.readings,
                    },
                }
            )
        )


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
            logger.read()
            update_sockets()

            # evaluates if minutes is multiple of 15 to start the timer
            if to_init and not rtc.datetime()[5] % _mins:
                log_data()

                logging_timer.init(
                    period=(_mins * 60000),
                    callback=lambda t: log_data(),
                )
                to_init = False

            gc.collect()

    except KeyboardInterrupt:
        logging_timer.deinit()
        server.Stop()
        db.close()


if __name__ == "__main__":
    main()
