#!/usr/bin/env python
import scipy
import scipy.fft
from scipy.signal import windows
import numpy as np
from tdsxx4a import get_adjusted_values
from python_utilities import ReadKeyValueDataFile
from matplotlib import pyplot as plt


def main(fname, window):
    d = ""
    with open(fname, "r") as f:
        d = f.read()

    header, data = ReadKeyValueDataFile(d, header_char="#", delim=":")
    header = dict(header)
    x, y = get_adjusted_values(header, data)
    sampling_rate = x[1] - x[0]

    window_obj = windows.get_window(window, len(x))
    x = np.array(x * window_obj)
    f = scipy.fft.fft(y)
    sp = scipy.fft.fftshift(f)

    freq = scipy.fft.fftshift(scipy.fft.fftfreq(len(x), sampling_rate))

    plt.plot(freq / 1e6, np.abs(sp))
    plt.xlabel("Frequency (MHz)")
    yunit = header["YUNIT"].strip("\"'")
    plt.ylabel("Amplitude ({})".format(yunit))
    plt.xlim([0, max(freq) / 1e6])
    plt.yscale("log")
    plt.show()


import click


@click.command()
@click.option(
    "--file", "-f", type=str, required=True, help="File name of TDS scope data"
)
@click.option("--window", "-w", type=str, default="boxcar", help="Window type")
def make_fft(file, window):
    main(file, window)


if __name__ == "__main__":
    make_fft()
