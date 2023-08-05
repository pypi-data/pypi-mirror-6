# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from construct import *
from io import BytesIO

__all__ = ["HexStringAdapter", "HexStringNibbleAdapter", "BaudrateAdapter"]

class HexStringAdapter(Adapter):
    __slots__ = ["inner_subcon", "capital"]

    def __init__(self, subcon, inner_subcon, capital = True):
        Adapter.__init__(self, subcon)
        self.inner_subcon = inner_subcon
        self.capital = capital
    def _encode(self, obj, context):
        f = "%02x"
        if self.capital:
            f = "%02X"

        stream = BytesIO()
        self.inner_subcon._build(obj, stream, context)

        return "".join([f % (ord(byte)) for byte in stream.getvalue()])

    def _decode(self, obj, context):
        data = "".join([chr(int(obj[i:i+2],16)) for i in range(0, len(obj), 2)])

        return self.inner_subcon._parse(BytesIO(data), context)

class HexStringNibbleAdapter(Adapter):
    __slots__ = ["capital", "inner_subcon"]

    def __init__(self, inner_subcon, capital = True):
        subcon = String("data", 1)
        Adapter.__init__(self, subcon)
        self.inner_subcon = inner_subcon
        self.capital = capital
    def _encode(self, obj, context):
        f = "%01x"
        if self.capital:
            f = "%01X"

        stream = BytesIO()
        self.inner_subcon._build(obj, stream, context)

        return f % (ord(stream.getvalue()[0]))
    def _decode(self, obj, context):
        data = chr(int(obj, 16))

        return self.inner_subcon._parse(BytesIO(data), context)

class BaudrateAdapter(Adapter):
    bps = {3: 1200, 4: 2400, 5: 4800, 6: 9600, 7: 19200, 8: 38400, 9: 57600, 10: 115200}
    bps_max = max([x for x in bps])
    def _decode(self, obj, ctx):
        return BaudrateAdapter.bps[obj]
    def _encode(self, obj, ctx):
        tmp = [i for (i,x) in BaudrateAdapter.bps.items() if x >= obj]
        if len(tmp):
            return tmp[0]
        return BaudrateAdapter.bps_max

