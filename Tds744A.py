import click, logging, sys
import LabAuto
import numpy as np
from time import sleep
from timeout_decorator import timeout, TimeoutError
_log = None

"""
HP GPIB Device
-> 2 types of commands:
    1) Ethernet-GPIB bridge meta commands
    2) GPIB control commands
Bridge commands have different delimiters for lines, newlines and returns might be stripped? FIXME
GPIB commands that are passed through have a configurable line delimiter added by the bridge


"""

class HP89400:
    def __init__(self, bridge, gpib_address):
        self.bridge = bridge
        self.bridge.Flush()
        self.bridge.SetGpibAddress(gpib_address)

    def Read(self):
        return self.bridge.TimeoutRead()

    def Write(self, arg):
        return self.bridge.Write(arg)

    def RunCommands(self, commands):
        for line, command in enumerate(commands):
            logging.getLogger().info("%d: %s"%(line, command))
            self.Write(command + "\n")
            sleep(0.05)
            if '?' in command:
                _log.info(self.Read())

            if(test):
                self.Write("SYST:ERR?\r\n")
                resp = (self.Read())
                assert(b'0' in resp[:3])

    @timeout(2)
    def SendGpibCommand(self, command):
        log = logging.getLogger()
        assert("?" not in command)
        log.info(command)
        while(True):
            self.ClearDataBuffer()
            sleep(0.1)
            self.Write(command + "\r\n")
            sleep(0.1)
            status_response = self.ReadGpibState()
            log.info("%s\tResponse: %s"%(command, status_response))
            try:
                if ReadGpibStatusCode(status_response) == 0:
                    break
            except (TypeError, ValueError) as e:
                log.warn("Gpib Send Command Error {}".format(e))
                self.ClearGpibErrors()
                continue

    @timeout(2)
    def ClearDataBuffer(self):
        log = logging.getLogger()
        while True:
            discard = self.Read()
            if discard is None:
                break
            else:
                log.info("Data in buffer: %s"%discard)

    @timeout(2)
    def SendGpibQuery(self, command):
        log = logging.getLogger()
        log.info(command)
        assert("?" in command)
        while(True):
            self.ClearDataBuffer()
            sleep(0.1)
            self.Write(command + "\r\n")
            sleep(0.1)
            response = self.Read("eoi")
            sleep(0.1)
            status_response = self.ReadGpibState()
            log.info("%s\t%s\tstatus: %s"%(command, response, status_response))
            try:
                if self.ReadGpibStatusCode(status_response) == 0:
                    break
            except (TypeError, ValueError) as e:
                log.warn(e)
                self.ClearGpibErrors()
        return response

    @timeout(5)
    def ReadGpibState(self):
        while(True):
            self.ClearDataBuffer()
            self.Write("syst:err?\r\n")
            sleep(0.1)
            response = self.Read()
            if response is not None:
                break
        return response

    def ReadGpibStatusCode(self, response):
        resp_str = response.decode("utf-8")
        resp_code = int(resp_str.split(',')[0])
        log = logging.getLogger()
        log.info("Status Code %d, %s"%(resp_code, resp_str))
        return resp_code

    @timeout(5)
    def ClearGpibErrors(self):
        no_errors = False
        while(not no_errors):
            try:
                resp = self.ReadGpibState()
                code = self.ReadGpibStatusCode(resp)
                if(code == 0):
                    no_errors = True
            except (ValueError, TimeoutError):
                pass


@click.group()
@click.option('--config', multiple = True, type=str, required=True, help='Config files, multiple accepted')
@click.pass_context
def gr1(ctx, config):
    ctx.ensure_object(dict)
    ctx.obj['config'] = LabAuto.ParseConfigFiles(config)

@gr1.command()
@click.option('--command_file', '-c', type=str, default='', help='GPIB Command List')
@click.option('--test', '-t', is_flag=True, help='GPIB Command List')
@click.pass_context
def LoadSetup(ctx, command_file, test):
    commands = LabAuto.ParseHPCommandFile(command_file)

    config = ctx.obj['config']
    with LabAuto.EthernetGPIBBridge(config['tcpip']['hostname'], config['tcpip']['port']) as bridge:
        hp_device = HP89400(bridge, gpib_port = int(config['gpib']['port']))
        setup_commands = [pt[1] for pt in config['prologix_commands'].items()]

        _log.info(bridge.GetVersion())
        _log.info(hp_device.SendGpibQuery("*IDN?"))
        hp_device.SendGpibCommand("*CLS")
        _log.info(hp_device.SendGpibQuery("FORM?"))
        _log.info(hp_device.SendGpibQuery("FORM:DATA?"))

        _log.info("#"*50)
        _log.info("\t\tSetup Device")
        _log.info("#"*50)
        hp_device.Setup(setup_commands)

        '''
        bridge.Write("INP1:IMP 50\r\n")
        bridge.Write("INP1:IMP 50\r\n")
        bridge.Write("SENS:AVER:STAT OFF\r\n")
        #bridge.Write("SENS:AVER:TYPE COMP\r\n")
        bridge.Write("SENS:BAND:MODE:ARB on\r\n")
        bridge.Write("SENS:BAND:RES 100 khz\r\n")
        bridge.Write("SENS:BAND:AUTO off\r\n")
        bridge.Write("SENS:BAND:RES:AUTO:OFFS off\r\n")
        #bridge.Write("SENS:DDEM:ADAP off\r\n")
        bridge.Write("SENS:FREQ:BAS on\r\n")
        bridge.Write("SENS:FREQ:CENT 1 mhz\r\n")
        bridge.Write("SENS:FREQ:MAN 1 mhz\r\n")
        bridge.Write("SENS:FREQ:SPAN 1 mhz\r\n")
        #bridge.Write("SENS:FREQ:SPAN:FULL\r\n")
        bridge.Write("SENS:FREQ:STAR 1 mhz\r\n")
        bridge.Write("SENS:FREQ:STOP 2 mhz\r\n")
        bridge.Write("SENS:FREQ:STEP:AUTO off\r\n")
        bridge.Write("SYST:ERR?\r\n")
        print(bridge.Read(mode = "eoi"))
        '''
@gr1.command()
@click.pass_context
@click.option('--filename', '-f', type=str, default='gpib_data.tiff', help='filename to save image to')
def SaveTiff(ctx, filename):
    config = ctx.obj['config']
    with LabAuto.EthernetGPIBBridge(config['tcpip']['hostname'], config['tcpip']['port']) as bridge:
        hp_device = HP89400(bridge, gpib_port = int(config['gpib']['port']))
        hp_device.SendGpibCommand("HCOP:DEV:LANG tiff")
        bridge.Write("HCOP:DATA?\r\n")
        tiff = (bridge.ReadBlob())[2:]#FIXME bad first 2 bytes
        with open(filename, "+wb") as f:
            f.write(tiff)

@gr1.command()
@click.pass_context
@click.option('--filename', '-f', type=str, default='gpib_data.csv', help='filename to save data to')
def SaveData(ctx, filename):
    config = ctx.obj['config']
    with LabAuto.EthernetGPIBBridge(config['tcpip']['hostname'], config['tcpip']['port']) as bridge:
        bridge.Write("CALC:DATA?\r\n")
        data = (bridge.ReadBlob())
        with open(filename, "+wb") as f:
            f.write(data)

def Run():
    global _log
    #logging.basicConfig()
    _log = logging.getLogger()
    _log.setLevel(logging.DEBUG)
    _log.addHandler(logging.StreamHandler(sys.stdout))
    assert(_log == logging.getLogger())
    try:
        gr1()
    except Exception as e:
        raise

if __name__ == "__main__":
    Run()

