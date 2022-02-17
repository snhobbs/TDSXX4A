import datetime
import os
import logging
import socket
import time
from time import sleep
import numpy as np
import timeout_decorator
from timeout_decorator import timeout, TimeoutError


from plx_gpib_ethernet import PrologixGPIBEthernetDevice
_log = None

def parse_preamble(preamble):
    entries = dict()
    split = preamble.strip().strip("#").split(";")
    for entry in split:
        pt_space_divide = entry.split(" ")
        key = pt_space_divide[0]
        value = " ".join([pt.strip() for pt in pt_space_divide[1:]])
        entries[key] = value
    return entries


def get_times(incriment, zero, points):
    return [pt*incriment - zero for pt in range(int(points))]


def transform_y_values(ymult, yoffset, yzero, yvalues):
    return [(pt - yoffset)*ymult - yzero for pt in yvalues]


def get_adjusted_values(header, values):
    '''
    Translate metadata and values into normal x, y values
    '''
    x_incriment = float(entries["XINCR"])
    x_offset = float(entries["XZERO"])
    n_points = int(entries["NR_PT"])
    times = get_times(x_incriment, x_offset, n_points)

    y_multiplier = float(entries["YMULT"])
    y_offset = float(entries["YOFF"])
    y_zero = float(entries["YZERO"])
    adj_values = transform_y_values(y_multiplier, y_offset, y_zero, values)
    return times, adj_values


class TDSXX4ADevice(PrologixGPIBEthernetDevice):
    def __init__(self, *args, **kwargs):
        self._header = dict()
        super().__init__(*args, **kwargs)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def setup(self):
        self.clear_errors()
        # read until eoi is recieved
        # no eoi signal at last character
        self.write("++eoi 1")
        # append to end of command, 0 = CR+LF, 1=CR, 2=LF, 3=None
        self.write("++eos 0")
        # no user defined character after transmit
        self.write("++eot_enable 1")
        # not used
        self.write("++eot_char %d"%ord("\n"))
        #eot_char = ++eot_char 42
        # disable front panel during operation
        #llo = ++llo
        # enable front panel
        #loc = ++loc
        # timeout in ms, only used when using timeout read
        self.write("++read_tmo_ms 1000")


    @property
    def header(self):
        '''
        Return dict of all setup and status data.
        Reloads header everytime
        '''
        preamble = self._read_preamble()
        preamble_dict = parse_preamble(preamble)
        self._header.update(preamble_dict)
        return self._header

    def set_data_range(self, start, stop):
        '''
        Programming Manual Page 53
        "The DATa:STARt
        and DATa:STOP commands let you specify the first and last data points of the
        waveform record. ...
        Setting DATa:STARt to 1 and DATa:STOP to the record length will always return the entire waveform."
        '''
        assert(start < stop)
        self.write("Data:stop %d"%stop)
        self.write("Data:start %d"%start)


    def setup_fft(self, channel, source, window, unit, suppression):
        '''
        Page 189
        "MATH1:DEFINE "FFT( CH1, HAMM, LINEARRMS, 20 )" takes an FFT from channel 1, using the HAMMING algorithm, with linear rms
        scaling, and 20 dB phase suppression. The result is stored in MATH1"
        '''
        self.write(f"{channel}:DEFINE \"FFT( {source}, {window}, {unit}, {suppression} )\"")

    def start_data_read(self):
        self.write("curve?")

    def read_data(self):
        data = []
        self.start_data_read()
        for i in range(1):
            while True:
                try:
                    data.extend(self.read())
                    sleep(0.1)
                except Exception as e:  # FIXME
                    print(e, i)
                    break
        delim=','
        d = "".join(data).strip().strip(delim).split(delim)
        d[0] = d[0].split(" ")[-1]
        print(d)
        return [float(pt) for pt in d if len(pt.strip())]


    def _read_preamble(self):
        '''
        Built in command returning all settings.
        Access through "header"
        '''
        return self.query("WFMPre?")

