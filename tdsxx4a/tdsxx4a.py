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

    # Remove preamble label
    preamble = preamble.lstrip("WFMPRE:")

    split = preamble.strip().strip("#").split(";")
    for entry in split:
        pt_space_divide = entry.split(" ")

        key = pt_space_divide[0]
        # Strip white space of all subsequent fields, join by single space
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
    values = np.array(values, dtype=float)
    x_incriment = float(header["XINCR"])
    x_offset = float(header["XZERO"])
    n_points = int(header["NR_PT"])
    times = get_times(x_incriment, x_offset, n_points)

    y_multiplier = float(header["YMULT"])
    y_offset = float(header["YOFF"])
    y_zero = float(header["YZERO"])
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

    def update_header(self):
        preamble = self._read_preamble()
        preamble_dict = parse_preamble(preamble)
        self._header.update(preamble_dict)

    @property
    def header(self):
        '''
        Return dict of all setup and status data.
        update_header must be called first
        '''
        return self._header

    def clear_errors(self):
        self.write("*CLS")

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

    def set_record_length(self, length):
        '''
        Page 174
        "Sets the number of data points that are acquired for each record. This is

        equivalent to setting Record Length in the Horizontal menu."

        Supports:
            500, 1000, 2500, 5000, 15000, 50000
            possibly higher with 1M attachment
        '''
        self.write(f"HORizontal:RECOrdlength {length}")

    def set_sources(self, sources):
        '''
        Page 112
        "
        DATA:SOURCE REF2, CH2, MATH1, CH1
        specifies that four waveforms will be transferred in the next CURVE? query.
        The order that the data will be transferred is CH1, CH2, MATH1, and then REF2.
        "
        '''
        line = ",".join(sources)
        self.write(f"DATA:SOURCE {line}")

    def set_source(self, source):
        '''
        See set_sources
        '''
        self.set_sources([source])

    def set_horizontal_scale(self, scale: float):
        '''
        Page 172
        "HORIZONTAL:MAIN:SCALE 2E-6" set the main scale to 2us per division
        '''
        self.write(f"HORIZONTAL:MAIN:SCALE {scale}")

    def set_vertical_scale(self, source: str, scale: float):
        '''
        Page 88
        " "CH1:SCALE 100E-3" sets the channel 4 gain to 100 mV per division"
        '''
        self.write(f"{source}:SCALE {scale}")

    def read_data(self):
        data = []
        self.start_data_read()
        for i in range(1):
            sleep(0.1)
            while True:
                try:
                    data.extend(self.read())
                    sleep(0.1)

                except socket.timeout as e:
                    break

                except Exception as e:
                    print(e, i)
                    break

        delim=','
        d = "".join(data).strip().strip(delim).split(delim)
        d[0] = d[0].split(" ")[-1]
        return [float(pt) for pt in d if len(pt.strip())]


    def _read_preamble(self):
        '''
        Built in command returning all settings.
        Access through "header"
        '''
        return self.query("WFMPre?")

