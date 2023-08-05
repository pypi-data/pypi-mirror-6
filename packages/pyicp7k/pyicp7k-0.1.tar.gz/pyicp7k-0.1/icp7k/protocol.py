from construct import *
from utils import *

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

__all__ = ["Command", "SetConfiguration", "ReadEncoder", "CaptureSyncEncoder", "Ping", "ReadModuleStatus", "ResetModuleStatus", "ReadWatchdogStatus", "EnableWatchdog", "ReadOEMName", "ReadConfiguration", "ReadResetStatus", "ResetPreset", "SetEncoderMode", "SetEncoderMode", "ReadFirmwareNumber", "ReadInitPin", "ReadName", "ReadEncoderStatus", "ReadSyncEncoder", "ReadPreset", "SetPreset"]

class Command(object):
    def __init__(self, request, response, **kwargs):
        self.request = request
        self.response = response
        self.kwargs = kwargs

    def encode(self, stream):
        return self.request.build_stream(Container(**(self.kwargs)), stream)

    def decode(self, stream):
        return self.response.parse_stream(stream)


hex_string_octet = HexStringAdapter(String("data",2), UBInt8("value"))
hex_string_int32 = HexStringAdapter(String("data",8), UBInt32("value"))

def make_request(delim, *args):
    args = list(args) + [Magic('\x0D')]
    return Struct("request",
        Magic(delim),
        Rename("addr", hex_string_octet),
        *args)


enable = [ HexStringAdapter(String("enable",2), ExprAdapter( BitStruct("enable",
        Padding(7-i),
        Flag("enable"),
        Padding(i)
    ), encoder = lambda obj,ctx: Container(enable=obj), decoder = lambda obj,ctx: bool(obj.enable))
) for i in range(0,7) ]

baud_rate = Rename("baud_rate", BaudrateAdapter(hex_string_octet))

no_resp = Struct("resp",Magic(''))
empty_resp = make_request('!')

input_range = Magic('53')

class SetConfiguration(Command):
    newaddr = Rename("newaddr", hex_string_octet)
    baud_rate = baud_rate
    checksum = Rename("checksum", enable[6])

    _req = make_request('%', newaddr, input_range, baud_rate, checksum)
    _resp = empty_resp
    def __init__(self, **kwargs):
        Command.__init__(self, SetConfiguration._req, SetConfiguration._resp, **kwargs)

encoder = Rename("encoder", ExprAdapter( HexStringNibbleAdapter( BitStruct("encoder",Padding(4),Nibble("encoder")) ),
    encoder = lambda obj, ctx: Container(encoder=obj),
    decoder = lambda obj, ctx: obj.encoder))
value = Rename("value",hex_string_int32)
data_resp = Struct("resp",Magic('>'),value,Magic('\x0D'))

class ReadEncoder(Command):
    _req = make_request('#', encoder)
    _resp = data_resp
    def __init__(self, **kwargs):
        Command.__init__(self, ReadEncoder._req, ReadEncoder._resp, **kwargs)

class CaptureSyncEncoder(Command):
    _req = Struct("resp",Magic("#**\x0D"))
    _resp = no_resp
    def __init__(self, **kwargs):
        Command.__init__(self, CaptureSyncEncoder._req, CaptureSyncEncoder._resp, **kwargs)

class Ping(Command):
    _req = Struct("resp",Magic("~**\x0D"))
    _resp = no_resp
    def __init__(self, **kwargs):
        Command.__init__(self, Ping._req, Ping._resp, **kwargs)

class ReadModuleStatus(Command):
    module_status = Rename("module_status", enable[2])
    _req = make_request('~', Magic('0'))
    _resp = make_request('!', module_status)
    def __init__(self, **kwargs):
        Command.__init__(self, ReadModuleStatus._req, ReadModuleStatus._resp, **kwargs)

class ResetModuleStatus(Command):
    _req = make_request('~', Magic('1'))
    _resp = empty_resp
    def __init__(self, **kwargs):
        Command.__init__(self, ResetModuleStatus._req, ResetModuleStatus._resp, **kwargs)

timer = Rename("timer", hex_string_octet)

class ReadWatchdogStatus(Command):
    _req = make_request('~', Magic('2'))
    _resp = make_request('!', timer)
    def __init__(self, **kwargs):
        Command.__init__(self, ReadWatchdogStatus._req, ReadWatchdogStatus._resp, **kwargs)

enable_nibble = Rename("enable", ExprAdapter( HexStringNibbleAdapter( BitStruct("enable",Padding(4),Nibble("enable")) ),
    encoder = lambda obj, ctx: Container(enable=obj),
    decoder = lambda obj, ctx: bool(obj.enable)))

class EnableWatchdog(Command):
    enable = enable_nibble
    _req = make_request('~', Magic('3'), enable, timer)
    _resp = empty_resp
    def __init__(self, **kwargs):
        Command.__init__(self, EnableWatchdog._req, EnableWatchdog._resp, **kwargs)

module_name = Struct("resp",Magic('!'),Rename("addr", hex_string_octet),CString("name",'\x0d'))

class ReadOEMName(Command):
    _req = make_request('~', Magic('M'))
    _resp = module_name
    def __init__(self, **kwargs):
        Command.__init__(self, ReadOEMName._req, ReadOEMName._resp, **kwargs)

class ReadConfiguration(Command):
    newaddr = Rename("newaddr", hex_string_octet)
    baud_rate = baud_rate
    checksum = Rename("checksum", enable[6])

    _req = make_request('$', Magic('2'))
    _resp = make_request('!', input_range, baud_rate, checksum)
    def __init__(self, **kwargs):
        Command.__init__(self, ReadConfiguration._req, ReadConfiguration._resp, **kwargs)

class ReadResetStatus(Command):
    reseted = Rename("reseted", enable_nibble)
    _req = make_request('$', Magic('5'))
    _resp = make_request('!', reseted)
    def __init__(self, **kwargs):
        Command.__init__(self, ReadResetStatus._req, ReadResetStatus._resp, **kwargs)

class ResetPreset(Command):
    _req = make_request('$', Magic('6'), encoder)
    _resp = empty_resp
    def __init__(self, **kwargs):
        Command.__init__(self, ResetPreset._req, ResetPreset._resp, **kwargs)

mode = Rename("mode", ExprAdapter( HexStringNibbleAdapter( BitStruct("mode",
    Padding(4),
    Flag("update_present"),
    Flag("XOR"),
    Enum(BitField("cc", 2),
        stop = 0,
        UD = 1,
        DP = 2,
        AB = 3,
    ),)),
    encoder = lambda obj,ctx: Container(**obj),
    decoder = lambda obj,ctx: dict(obj)
    ))

class SetEncoderMode(Command):
    _req = make_request('$', Magic('D'), encoder, mode)
    _resp = empty_resp
    def __init__(self, **kwargs):
        Command.__init__(self, SetEncoderMode._req, SetEncoderMode._resp, **kwargs)

class ReadFirmwareNumber(Command):
    firmware = CString("firmware",'\x0d')

    _req = make_request('$', Magic('F'))
    _resp = Struct("resp", Magic('!'), Rename("addr", hex_string_octet), firmware)
    def __init__(self, **kwargs):
        Command.__init__(self, ReadFirmwareNumber._req, ReadFirmwareNumber._resp, **kwargs)

class ReadInitPin(Command):
    open = Rename("open", enable_nibble)

    _req = make_request('$', Magic('I'))
    _resp = make_request('!', open)
    def __init__(self, **kwargs):
        Command.__init__(self, ReadInitPin._req, ReadInitPin._resp, **kwargs)

class ReadName(Command):
    _req = make_request('$', Magic('M'))
    _resp = module_name
    def __init__(self, **kwargs):
        Command.__init__(self, ReadName._req, ReadName._resp, **kwargs)

encoder_status = Rename("status", ExprAdapter( HexStringAdapter(String("data",2), BitStruct("mode",
    Flag("update_present"),
    Flag("XOR"),
    Enum(BitField("cc", 2),
        stop = 0,
        UD = 1,
        DP = 2,
        AB = 3,
    ),
    Padding(1),
    Flag("Z"),
    Flag("B"),
    Flag("A"),
    )),
    encoder = lambda obj,ctx: Container(**obj),
    decoder = lambda obj,ctx: dict(obj)
    ))

class ReadEncoderStatus(Command):
    _req = make_request('$', Magic('S'), encoder)
    _resp = make_request('!', encoder_status)
    def __init__(self, **kwargs):
        Command.__init__(self, ReadEncoderStatus._req, ReadEncoderStatus._resp, **kwargs)

class ReadSyncEncoder(Command):
    _req = make_request('$', Magic('Z'), encoder)
    _resp = data_resp
    def __init__(self, **kwargs):
        Command.__init__(self, ReadSyncEncoder._req, ReadSyncEncoder._resp, **kwargs)

class ReadPreset(Command):
    _req = make_request('@', Magic('G'), encoder)
    _resp = make_request('!', value)
    def __init__(self, **kwargs):
        Command.__init__(self, ReadPreset._req, ReadPreset._resp, **kwargs)

class SetPreset(Command):
    _req = make_request('@', Magic('P'), encoder, value)
    _resp = empty_resp
    def __init__(self, **kwargs):
        Command.__init__(self, SetPreset._req, SetPreset._resp, **kwargs)
