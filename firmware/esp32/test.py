from machine import Pin, SPI

adc = SPI(1, 10000000)

cs = Pin(25, Pin.OUT)
