import unittest
from construct import *
from icp7k.utils import *

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

class HexStringAdapterTest(unittest.TestCase):
    def setUp(self):
        pass
    def test_encode_uint8(self):
        c = HexStringAdapter(String("data",2), UBInt8("value"))
        self.assertEqual(c.build(8),  "08")
        self.assertEqual(c.build(10), "0A")
        self.assertEqual(c.build(128),"80")
        self.assertEqual(c.build(255),"FF")
        c = HexStringAdapter(String("data",2), UBInt8("value"), capital = False)
        self.assertEqual(c.build(10), "0a")
        self.assertEqual(c.build(255),"ff")
    def test_encode_uint32(self):
        c = HexStringAdapter(String("data",8), UBInt32("value"))
        self.assertEqual(c.build(287454020), "11223344")
    def test_decode_uint8(self):
        c = HexStringAdapter(String("data",2), UBInt8("value"))
        self.assertEqual(8, c.parse("08"))
        self.assertEqual(10, c.parse("0A"))
        self.assertEqual(10, c.parse("0a"))
        self.assertEqual(128, c.parse("80"))
        self.assertEqual(255, c.parse("FF"))
        self.assertEqual(255, c.parse("ff"))
    def test_decode_uint32(self):
        c = HexStringAdapter(String("data",8), UBInt32("value"))
        self.assertEqual(287454020, c.parse("11223344"))

class HexStringNibbleAdapterTest(unittest.TestCase):
    def setUp(self):
        self.n = ExprAdapter( BitStruct("octet", Padding(4), Nibble("value")),
            encoder = lambda obj, ctx: Container(value=obj),
            decoder = lambda obj, ctx: obj.value)
    def test_encode(self):
        c = HexStringNibbleAdapter(self.n)
        for x in range(0,15):
            self.assertEqual(c.build(x),'%01X' % (x))
        c = HexStringNibbleAdapter(self.n, capital=False)
        for x in range(0,15):
            self.assertEqual(c.build(x),'%01x' % (x))
        self.assertEqual(c.build(0x1f),'f')
        self.assertEqual(c.build(0x0f),'f')
    def test_decode(self):
        c = HexStringNibbleAdapter(self.n)
        self.assertEqual(0, c.parse("0"))
        self.assertEqual(1, c.parse("1"))
        self.assertEqual(15, c.parse("f"))
        self.assertEqual(15, c.parse("F"))

class BaudrateAdapterTest(unittest.TestCase):
    def setUp(self):
        self.bps = {3: 1200, 4: 2400, 5: 4800, 6: 9600, 7: 19200, 8: 38400, 9: 57600, 10: 115200}
    def test_encode(self):
        c = BaudrateAdapter(UBInt8("value"))
        for (i,x) in self.bps.items():
            self.assertEqual(c.build(x), chr(i))
        self.assertEqual(c.build(100), '\x03')
        self.assertEqual(c.build(900000), '\x0a')
    def test_decoder(self):
        c = BaudrateAdapter(UBInt8("value"))
        for (i,x) in self.bps.items():
            self.assertEqual(c.parse(chr(i)), x)

if __name__ == '__main__':
    unittest.main(verbosity=2)

