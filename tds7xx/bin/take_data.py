from time import sleep
import datetime
import click
import os
from tds7xx import TDS7xxDevice
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


def setup_gpib(address, ip):
    device = TDS7xxDevice(address, ip, timeout=3)
    print(device.address)
    print(device.gpib.host)
    device.connect()
    device.setup();
    return device

@click.option('--ip', required=True, type=str, help='ip address')
@click.option('--name', type=str, required=True, help='file name')
@click.command()
def take_data(ip, name):
    address = 4
    device = setup_gpib(address, ip)
    device.set_data_range(0, 100000)
    preamble = device.read_preamble()
    data = device.read_data()
    fname = make_name(name)

    with open(fname+".dat", 'w') as f:
        f.write(f"# file_name: {name}\n")
        f.write(f"# date: {datetime.datetime.now().date()}\n")
        f.write(f"# time: {datetime.datetime.now().time()}\n")
        f.write(f"# wavfrm : {preamble}\n")
        f.write("\n".join([str(pt) for pt in data]))
    plot(fname)

if __name__ == "__main__":
    take_data()
