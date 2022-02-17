from time import sleep
import datetime
import click
import os
from tdsxx4a import TDSXX4ADevice
import socket
import logging
#duration = 0.5
#freq = 2000

def make_name(name):
    time_stamp = datetime.datetime.now().isoformat().replace(".", ":")
    return f"{name}_{time_stamp}"


def plot(name):
    from matplotlib import pyplot as plt
    with open(name + ".dat") as f:
        d = f.read().strip().split("\n")
        plt.plot([float(pt) for pt in d if len(pt.strip()) and "#" not in pt])
    plt.show()

CONTEXT_SETTINGS = dict(
    default_map={
        "ip":"10.231.231.129",
        "name":"TDSXX4A",
        "address":4,
        "timeout":3
    }
)

@click.option('--ip', required=True, type=str, help='ip address')
@click.option('--name', type=str, required=True, help='file name')
@click.option('--address', type=int, default=4, help='GPIB Address')
@click.option('--timeout', type=int, default=4, help='Socket Timeout')
@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def cli(ctx, ip, name, address, timeout):
    ctx.obj = dict(
        ip=ip,
        name=name,
        address=address,
        timeout=timeout
    )
    pass


@click.option('--sources', type=str, multiple=True, default=["CH1"], help='Input channel')
@click.option('--record_length', type=int, default=int(15e3), help='Sample Points')
@click.option('--hscale', type=float, default=1e-6, help='Time scale per division')
@cli.command()
@click.pass_context
def take_data(ctx, sources, record_length, hscale):
    device = TDSXX4ADevice(ctx.obj["address"], ctx.obj["ip"], ctx.obj["timeout"])
    stop = record_length+1
    device.connect()
    device.setup();

    device.set_horizontal_scale(hscale)
    sleep(1)
    device.set_sources(sources)
    device.update_header()

    device.set_record_length(record_length)
    sleep_time = 3e-4*record_length
    logging.getLogger().info("Sleep Time: %0.1f", sleep_time)
    sleep(sleep_time)

    device.set_data_range(0, stop)
    sleep(1)
    device.update_header()

    data = device.read_data()
    name = ctx.obj["name"]
    fname = make_name(name)

    with open(fname+".dat", 'w') as f:
        f.write(f"# file_name: {name}\n")
        f.write(f"# date: {datetime.datetime.now().date()}\n")
        f.write(f"# time: {datetime.datetime.now().time()}\n")
        for key, value in device.header.items():
            f.write(f"# {key} : {value}\n")
        f.write("\n".join([str(pt) for pt in data]))
    plot(fname)

@click.option('--channel', type=str, default="MATH1", help='Math Channel')
@click.option('--source', type=str, default="CH1", help='Input channel')
@click.option('--window', type=str, default="HAMM", help='FFT Window')
@click.option('--units', type=str, default="LINEARRMS", help='Units')
@click.option('--suppression', type=str, default="-100", help='Suppress values less than this (dB)')
@cli.command()
@click.pass_context
def take_fft(ctx, channel, source, window, units, suppression):
    device = TDSXX4ADevice(ctx.obj["address"], ctx.obj["ip"], ctx.obj["timeout"])
    device.connect()
    device.setup();

    # device.set_data_range(0, 100000)
    device.setup_fft(channel, source, window, units, suppression)
    device.set_source(channel)

    sleep(5)
    device.update_header()
    data = device.read_data()
    name = ctx.obj["name"]
    fname = make_name(name)

    with open(fname+".dat", 'w') as f:
        f.write(f"# file_name: {name}\n")
        f.write(f"# date: {datetime.datetime.now().date()}\n")
        f.write(f"# time: {datetime.datetime.now().time()}\n")
        for key, value in device.header.items():
            f.write(f"# {key} : {value}\n")
        f.write("\n".join([str(pt) for pt in data]))
    plot(fname)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    cli()
