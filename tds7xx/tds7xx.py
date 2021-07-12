import logging
from time import sleep
import numpy as np
from timeout_decorator import timeout
import timeout_decorator
import socket
"""
HP GPIB Device
-> 2 types of commands:
    1) Ethernet-GPIB bridge meta commands
    2) GPIB control commands
Bridge commands have different delimiters for lines, newlines and returns might be stripped? FIXME
GPIB commands that are passed through have a configurable line delimiter added by the bridge


"""

'''
File Format is line number !${command}
The first 3 lines are meta data
'''
MEASUREMENT_FINISH_SLEEP_TIME = 0
DATA_READ_SLEEP_TIME = 0
#MEASUREMENT_FINISH_SLEEP_TIME = 0.05
#DATA_READ_SLEEP_TIME = 0.1

def ParseHPCommandFile(fname):
    kMetaDataRows = 3
    lines = np.loadtxt(fname, skiprows=kMetaDataRows, delimiter="!", dtype=str, unpack=True)
    logging.getLogger().info(lines)
    return lines[1]

def ReadStatusCode(response):
    resp_str = response.decode("utf-8")
    resp_code = int(resp_str.split(',')[0])
    log = logging.getLogger()
    #log.info("Status Code %d, %s"%(resp_code, resp_str))
    return resp_code

from time import sleep
from timeout_decorator import timeout, TimeoutError
from plx_gpib_ethernet import PrologixGPIBEthernetDevice
_log = None
test=False

import time
class TDS7xxDevice(PrologixGPIBEthernetDevice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __enter__(self):
        print("Open Socket", time.time())
        self.connect()
        print("Socket Opened", time.time())
        return self

    def __exit__(self, *args, **kwargs):
        print("Close Socket", time.time())
        self.close()
        print("Socket Closed ", time.time())

    def get_error_code(cls, error):
        return int(str(error[:3]).strip(','))

    def reset(self):
        self.close()
        self.gpib = PrologixGPIBEthernet(self.gpib.host, self.gpib.timeout)
        self.connect()

    def write(self, *args, **kwargs):
        print(*args, **kwargs)
        super().write(*args, **kwargs)

    def query(self, *args, **kwargs):
        print(*args, **kwargs)
        return super().query(*args, **kwargs)

    def read_error_code(self):
        return self.get_error_code(self.read_errors())

    def set_source(self, channel):
        self.write("data:source ch%d"%channel)

    def read_errors(self):
        return self.query("SYST:ERR?\r\n").strip()

    def read_data(self):
        return self.query("CURVE?")

    def GetDataLength(self):
        return int(self.query("CALC:DATA:HEAD:POIN?"))

    def GetYUnits(self):
        #gpib.write("CALC:UNIT:AM?\r\n")
        return self.query("CALC:UNIT:POW?")

    def GetXUnits(self):
        return self.query("CALC:X:UNIT:FREQ?")

    def clear_errors(self):
        self.write("*CLS")

    def abort(self):
        #super().write("abor")
        while True:
            try:
                super().write("abor")
                break
            except socket.timeout:
                continue

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


    def get_operating_condition(self):
        resp = int(self.query("STAT:OPER:COND?"))
        return resp

    def GetReadDataPoints(self):
        return int(self.query("SENS:AVER:COUN:INT?"))

    def StartDataRead(self):
        self.write("curve?")

    def set_data_range(self, start, stop):
        assert(start < stop)
        self.write("Data:stop %d"%stop)
        self.write("Data:start %d"%start)

    def read_preamble(self):
        return self.query("WFMPre?")

    def read_data(self):
        data = []
        self.StartDataRead()
        for i in range(1):
            while True:
                try:
                    data.extend(self.read())
                    sleep(0.1)
                except Exception as e:
                    print(e, i)
                    break
        delim=','
        d = "".join(data).strip().strip(delim).split(delim)
        d[0] = d[0].split(" ")[-1]
        print(d)
        return [float(pt) for pt in d if len(pt.strip())]

    def ReadConfiguration(self):
        self.xunits = self.GetXUnits()
        self.yunits = self.GetYUnits()
        self.freq_center = self.GetXCenter()
        self.freq_span = self.GetXSpan()
        #self.data_length = self.GetDataLength()

