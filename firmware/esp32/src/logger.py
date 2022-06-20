from machine import Pin, ADC, time_pulse_us
from micropython import const
import time


_ref = const(2450000)
_ref_v = const(250)
_ref_i = const(25)

_offset = const(142000)  # misurato su ingresso adc collegato a massa 142000


class Logger:
    def __init__(self, freq, adc, en_i, en_v, en_p):

        self.freq = Pin(freq, Pin.IN)
        self.adc = ADC(Pin(adc, Pin.IN), atten=ADC.ATTN_11DB)

        self.en_i = Pin(en_i, Pin.OUT)
        self.en_v = Pin(en_v, Pin.OUT)
        self.en_p = Pin(en_p, Pin.OUT)

        self.readings = [0.0, 0.0, 0.0, 0.0]
        self._reset_en()

    def _reset_en(self):
        self.en_i.off()
        self.en_v.off()
        self.en_p.off()

    def read_freq(self):
        _, half = time_pulse_us(self.freq, 1), time_pulse_us(self.freq, 1)
        period = 2 * half
        freq = 1e6 / (period)
        return round(freq, 1)

    def _read_samples(self, samples):
        l = []
        time.sleep_ms(600)  # da datasheet ad536

        for i in range(samples):

            time.sleep_us(15)
            val = self.adc.read_uv()
            l.append(val)

        return (sum(l) / len(l)) - _offset

    def read_v(self, samples=50):
        self._reset_en()
        self.en_v.on()
        mean = self._read_samples(samples)

        return (mean / _ref) * _ref_v

    def read_i(self, samples=50):
        self._reset_en()
        self.en_i.on()
        mean = self._read_samples(samples)

        return (mean / _ref) * _ref_i

    def read_p(self, samples=50):
        self._reset_en()
        self.en_p.on()
        mean = self._read_samples(samples)  # valore efficace

        dc = (mean / _ref) ** 2  # duty cycle

        phase = dc * 180

        return int(phase)

    def read(self):
        self.readings[0] = self.read_v()
        self.readings[1] = self.read_i()
        self.readings[2] = self.read_freq()
        self.readings[3] = self.read_p()
