#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from optparse import OptionParser, OptionGroup
from icp7k.client import *
from icp7k.protocol import *
from datetime import *
from time import *

usleep = lambda x: sleep(x/1000000.0)

parser = OptionParser()
parser.add_option("-d", "--device", dest="device", metavar="FILE", help="tty device to communicate", default="/dev/ttyS0")
parser.add_option("-r", "--baudrate", dest="rate", metavar="RATE", help="baudrate for device", default=9600, type="int")
parser.add_option("-q", "--quite", dest="quite", default=False, help="don't print output", action="store_true")
parser.add_option("-i", "--info", dest="info", default=False, help="read and show device info", action="store_true")
parser.add_option("--set-encoder", dest="set_encoder", default=False, help="set encoder mode", action="store_true")
parser.add_option("--set-module", dest="set_module", default=False, help="set module mode", action="store_true")
parser.add_option("-p", "--poll", dest="poll", default=False, help="poll encoder values", action="store_true")
parser.add_option("-w", "--interval", dest="interval", default=1000, metavar="INTERVAL", help="polling interval in usec", type="int")

encoder_group = OptionGroup(parser, "Encoder Options")
encoder_group.add_option("-e", "--encoder", dest="encoder", metavar="ENCODER", default=0, help="encoder address", type="int")
encoder_group.add_option("--enable-xor", dest="xor", help="enable XOR control bit", action="store_true")
encoder_group.add_option("--disable-xor", dest="xor", help="disable XOR control bit", action="store_false")
encoder_group.add_option("--enable-update", dest="update_preset", help="enable update the preset value before power is off",action="store_true")
encoder_group.add_option("--disable-update", dest="update_preset", help="disable update the preset value before power is off",action="store_false")
encoder_group.add_option("-c", "--cc", dest="cc", metavar="stop|UD|DP|AB", help="encoder mode", type="string")
parser.add_option_group(encoder_group)

module_group = OptionGroup(parser, "Module Options")
module_group.add_option("-a", "--addr", dest="addr", metavar="ADDR", default=1, help="module address", type="int")
module_group.add_option("--new-baudrate", dest="newrate", metavar="RATE", help="set new baudrate for device", type="int")
module_group.add_option("--new-addr", dest="newaddr", metavar="ADDR", help="set new module address for device", type="int")
parser.add_option_group(module_group)

(options, args) = parser.parse_args()

c = Client(port = options.device, baudrate = options.rate, timeout = 5)

def encoder_info(x):
    preset = c(ReadPreset(addr=options.addr, encoder=x))
    value = c(ReadEncoder(addr=options.addr, encoder=x))
    status = c(ReadEncoderStatus(addr=options.addr, encoder=x)).status
    values = c(ReadSyncEncoder(addr=options.addr, encoder=x))
    fmt = """Encoder #%d:
    Preset: %d
    Value:  %d [%d (sync)]
    XOR:    %d
    Mode:   %s
    Update: %d
    A: %d B: %d Z: %d
"""
    print fmt % (x, preset.value, value.value, values.value, status['XOR'], status['cc'], status['update_present'], status['A'], status['B'], status['Z'])

def module_info():
    name = c(ReadName(addr=options.addr))
    oem_name = c(ReadOEMName(addr=options.addr))
    firmware = c(ReadFirmwareNumber(addr=options.addr))
    conf = c(ReadConfiguration(addr=options.addr))
    fmt = """
Module name:     %s
Module OEM name: %s
Module firmware: %s

Configuration:
    Baudrate:  %d
    Checksum:  %d
"""
    print fmt % (name.name, oem_name.name, firmware.firmware, conf.baud_rate, conf.checksum)

if options.info:
    if not options.quite:
        module_info()
	for x in range(0,3):
            encoder_info(x)
    exit(0)

if options.set_encoder:
    opts = dict(addr = options.addr, encoder=options.encoder, mode=dict(update_present=options.update_preset,XOR=options.xor,cc=options.cc))
    c(SetEncoderMode(**opts))
    if not options.quite:
        encoder_info(options.encoder)
    exit(0)

if options.set_module:
    conf = c(ReadConfiguration(addr=options.addr))
    opts = dict(addr = options.addr, newaddr = options.addr, baud_rate = options.rate, checksum = False)
    if options.newrate:
        opts["baud_rate"] = options.newrate
    if options.newaddr:
        opts["newaddr"] = options.newaddr
    resp = c(SetConfiguration(**opts))
    options.addr = resp.addr
    if not options.quite:
        module_info()    
    exit(0)

if options.poll:
    while True:
        c(ReadName(addr = options.addr))
        c(CaptureSyncEncoder(addr = options.addr))
        ts = datetime.now()
        usleep( options.interval )
        value = [c(ReadSyncEncoder(addr = options.addr, encoder = x)).value for x in range(0,3)]
        print ts, "\t".join(map(str,value))

