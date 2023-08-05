# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import unittest
from construct import *
from icp7k.protocol import *
from io import *

class ProtocolTest(unittest.TestCase):
    def t(self, class_name, output_string, input_string, output_dict, input_dict):
        i = BytesIO(input_string)
        o = BytesIO()
        r = class_name(**output_dict)
        r.encode(o)
        self.assertEqual(o.getvalue(), output_string)
        resp = r.decode(i)
        for x in input_dict.keys():
            self.assertEqual(getattr(resp,x), input_dict[x])

    def setUp(self):
	pass
    def test_SetConfiguration(self):
        self.t(SetConfiguration, '%0101530600\r', '!01\r', dict(addr = 1, newaddr = 1, baud_rate = 9600, checksum = 0), dict(addr = 1))
        self.t(SetConfiguration, '%0101530640\r', '!01\r', dict(addr = 1, newaddr = 1, baud_rate = 9600, checksum = 1), dict(addr = 1))
        self.t(SetConfiguration, '%0101530A00\r', '!01\r', dict(addr = 1, newaddr = 1, baud_rate = 115200, checksum = 0), dict(addr = 1))
        self.t(SetConfiguration, '%0102530A40\r', '!02\r', dict(addr = 1, newaddr = 2, baud_rate = 115200, checksum = 1), dict(addr = 2))
        self.t(SetConfiguration, '%0202530600\r', '!02\r', dict(addr = 2, newaddr = 2, baud_rate = 9600, checksum = 0), dict(addr = 2))
        self.t(SetConfiguration, '%0201530640\r', '!01\r', dict(addr = 2, newaddr = 1, baud_rate = 9600, checksum = 1), dict(addr = 1))
    def test_ReadEncoder(self):
        self.t(ReadEncoder, '#010\r', '>0000001E\r', dict(addr = 1, encoder = 0), dict(value = 0x1E))
        self.t(ReadEncoder, '#011\r', '>0000001E\r', dict(addr = 1, encoder = 1), dict(value = 0x1E))
        self.t(ReadEncoder, '#012\r', '>0000001E\r', dict(addr = 1, encoder = 2), dict(value = 0x1E))
        self.t(ReadEncoder, '#010\r', '>0000901E\r', dict(addr = 1, encoder = 0), dict(value = 0x901E))
        self.t(ReadEncoder, '#011\r', '>0000901E\r', dict(addr = 1, encoder = 1), dict(value = 0x901E))
        self.t(ReadEncoder, '#012\r', '>0000901E\r', dict(addr = 1, encoder = 2), dict(value = 0x901E))
    def test_CaptureSyncEncoder(self):
        self.t(CaptureSyncEncoder, '#**\r', '', dict(), dict())
    def test_Ping(self):
        self.t(Ping, '~**\r', '', dict(), dict())
    def test_ReadModuleStatus(self):
        self.t(ReadModuleStatus, '~010\r', '!0100\r', dict(addr = 1), dict(addr = 1, module_status = False))
        self.t(ReadModuleStatus, '~010\r', '!0104\r', dict(addr = 1), dict(addr = 1, module_status = True))
        self.t(ReadModuleStatus, '~020\r', '!0200\r', dict(addr = 2), dict(addr = 2, module_status = False))
        self.t(ReadModuleStatus, '~020\r', '!0204\r', dict(addr = 2), dict(addr = 2, module_status = True))
    def test_ResetModuleStatus(self):
        self.t(ResetModuleStatus, '~011\r', '!01\r', dict(addr = 1), dict(addr = 1))
        self.t(ResetModuleStatus, '~021\r', '!02\r', dict(addr = 2), dict(addr = 2))
    def test_ReadWatchdogStatus(self):
        self.t(ReadWatchdogStatus, '~012\r', '!0100\r', dict(addr = 1), dict(addr = 1, timer=0))
        self.t(ReadWatchdogStatus, '~022\r', '!0200\r', dict(addr = 2), dict(addr = 2, timer=0))
        self.t(ReadWatchdogStatus, '~012\r', '!0181\r', dict(addr = 1), dict(addr = 1, timer=129))
        self.t(ReadWatchdogStatus, '~022\r', '!0281\r', dict(addr = 2), dict(addr = 2, timer=129))
    def test_EnableWatchdog(self):
        self.t(EnableWatchdog, '~013001\r', '!01\r', dict(addr = 1, timer = 1, enable = False), dict(addr = 1))
        self.t(EnableWatchdog, '~023001\r', '!02\r', dict(addr = 2, timer = 1, enable = False), dict(addr = 2))
        self.t(EnableWatchdog, '~013101\r', '!01\r', dict(addr = 1, timer = 1, enable = True), dict(addr = 1))
        self.t(EnableWatchdog, '~023101\r', '!02\r', dict(addr = 2, timer = 1, enable = True), dict(addr = 2))
    def test_ReadOEMName(self):
        self.t(ReadOEMName, '~01M\r', '!0100007083\r', dict(addr = 1), dict(addr = 1, name = "00007083"))
        self.t(ReadOEMName, '~02M\r', '!0200007083\r', dict(addr = 2), dict(addr = 2, name = "00007083"))
        self.t(ReadOEMName, '~01M\r', '!0100007083D\r', dict(addr = 1), dict(addr = 1, name = "00007083D"))
        self.t(ReadOEMName, '~02M\r', '!0200007083D\r', dict(addr = 2), dict(addr = 2, name = "00007083D"))
    def test_ReadConfiguration(self):
        self.t(ReadConfiguration, '$012\r', '!01530600\r', dict(addr = 1), dict(addr = 1, baud_rate = 9600, checksum = 0))
        self.t(ReadConfiguration, '$012\r', '!01530700\r', dict(addr = 1), dict(addr = 1, baud_rate = 19200, checksum = 0))
        self.t(ReadConfiguration, '$012\r', '!01530640\r', dict(addr = 1), dict(addr = 1, baud_rate = 9600, checksum = 1))
        self.t(ReadConfiguration, '$022\r', '!02530600\r', dict(addr = 2), dict(addr = 2, baud_rate = 9600, checksum = 0))
        self.t(ReadConfiguration, '$022\r', '!02530700\r', dict(addr = 2), dict(addr = 2, baud_rate = 19200, checksum = 0))
        self.t(ReadConfiguration, '$022\r', '!02530640\r', dict(addr = 2), dict(addr = 2, baud_rate = 9600, checksum = 1))
    def test_ReadResetStatus(self):
        self.t(ReadResetStatus, '$015\r', '!010\r', dict(addr = 1), dict(addr = 1, reseted=False))
        self.t(ReadResetStatus, '$025\r', '!020\r', dict(addr = 2), dict(addr = 2, reseted=False))
        self.t(ReadResetStatus, '$015\r', '!011\r', dict(addr = 1), dict(addr = 1, reseted=True))
        self.t(ReadResetStatus, '$025\r', '!021\r', dict(addr = 2), dict(addr = 2, reseted=True))
    def test_ResetPreset(self):
        self.t(ResetPreset, '$0160\r', '!01\r', dict(addr = 1, encoder=0), dict(addr = 1))
        self.t(ResetPreset, '$0260\r', '!02\r', dict(addr = 2, encoder=0), dict(addr = 2))
        self.t(ResetPreset, '$0161\r', '!01\r', dict(addr = 1, encoder=1), dict(addr = 1))
        self.t(ResetPreset, '$0261\r', '!02\r', dict(addr = 2, encoder=1), dict(addr = 2))
    def test_SetEncoderMode(self):
        self.t(SetEncoderMode, '$01D05\r', '!01\r', dict(addr = 1, encoder=0, mode=dict(update_present=False,XOR=True,cc="UD")), dict(addr = 1))
        self.t(SetEncoderMode, '$02D05\r', '!02\r', dict(addr = 2, encoder=0, mode=dict(update_present=False,XOR=True,cc="UD")), dict(addr = 2))
        self.t(SetEncoderMode, '$01D1B\r', '!01\r', dict(addr = 1, encoder=1, mode=dict(update_present=True,XOR=False,cc="AB")), dict(addr = 1))
        self.t(SetEncoderMode, '$02D1B\r', '!02\r', dict(addr = 2, encoder=1, mode=dict(update_present=True,XOR=False,cc="AB")), dict(addr = 2))
    def test_ReadFirmwareNumber(self):
        self.t(ReadFirmwareNumber, '$01F\r', '!01A2.0\r', dict(addr = 1), dict(addr = 1, firmware = "A2.0"))
        self.t(ReadFirmwareNumber, '$02F\r', '!02A2.0\r', dict(addr = 2), dict(addr = 2, firmware = "A2.0"))
        self.t(ReadFirmwareNumber, '$01F\r', '!01A3.0\r', dict(addr = 1), dict(addr = 1, firmware = "A3.0"))
        self.t(ReadFirmwareNumber, '$02F\r', '!02A3.0\r', dict(addr = 2), dict(addr = 2, firmware = "A3.0"))
    def test_ReadInitPin(self):
        self.t(ReadInitPin, '$01I\r', '!010\r', dict(addr = 1), dict(addr = 1, open = False))
        self.t(ReadInitPin, '$02I\r', '!020\r', dict(addr = 2), dict(addr = 2, open = False))
        self.t(ReadInitPin, '$01I\r', '!011\r', dict(addr = 1), dict(addr = 1, open = True))
        self.t(ReadInitPin, '$02I\r', '!021\r', dict(addr = 2), dict(addr = 2, open = True))
    def test_ReadName(self):
        self.t(ReadName, '$01M\r', '!017083\r', dict(addr = 1), dict(addr = 1, name = "7083"))
        self.t(ReadName, '$02M\r', '!027083\r', dict(addr = 2), dict(addr = 2, name = "7083"))
        self.t(ReadName, '$01M\r', '!017083D\r', dict(addr = 1), dict(addr = 1, name = "7083D"))
        self.t(ReadName, '$02M\r', '!027083D\r', dict(addr = 2), dict(addr = 2, name = "7083D"))
    def test_ReadEncoderStatus(self):
        self.t(ReadEncoderStatus, '$01S0\r', '!0150\r', dict(addr = 1, encoder = 0), dict(addr = 1, status=dict(XOR=True, cc="UD", update_present=False, A=False, B=False, Z=False)))
    def test_ReadSyncEncoder(self):
        self.t(ReadSyncEncoder, '$01Z0\r', '>0000001E\r', dict(addr = 1, encoder = 0), dict(value = 0x1E))
        self.t(ReadSyncEncoder, '$01Z1\r', '>0000001E\r', dict(addr = 1, encoder = 1), dict(value = 0x1E))
        self.t(ReadSyncEncoder, '$01Z2\r', '>0000001E\r', dict(addr = 1, encoder = 2), dict(value = 0x1E))
        self.t(ReadSyncEncoder, '$01Z0\r', '>0000901E\r', dict(addr = 1, encoder = 0), dict(value = 0x901E))
        self.t(ReadSyncEncoder, '$01Z1\r', '>0000901E\r', dict(addr = 1, encoder = 1), dict(value = 0x901E))
        self.t(ReadSyncEncoder, '$01Z2\r', '>0000901E\r', dict(addr = 1, encoder = 2), dict(value = 0x901E))
    def test_ReadPreset(self):
        self.t(ReadPreset, '@01G0\r', '!0100000000\r', dict(addr = 1, encoder = 0), dict(addr = 1, value = 0x0))
        self.t(ReadPreset, '@01G1\r', '!0100000000\r', dict(addr = 1, encoder = 1), dict(addr = 1, value = 0x0))
        self.t(ReadPreset, '@02G2\r', '!0200000800\r', dict(addr = 2, encoder = 2), dict(addr = 2, value = 0x800))
        self.t(ReadPreset, '@02G2\r', '!0200000800\r', dict(addr = 2, encoder = 2), dict(addr = 2, value = 0x800))
    def test_SetPreset(self):
        self.t(SetPreset, '@01P000000000\r', '!01\r', dict(addr = 1, encoder = 0, value=0), dict(addr = 1))
        self.t(SetPreset, '@01P100000000\r', '!01\r', dict(addr = 1, encoder = 1, value=0), dict(addr = 1))
        self.t(SetPreset, '@02P200000800\r', '!02\r', dict(addr = 2, encoder = 2, value=0x800), dict(addr = 2))
        self.t(SetPreset, '@02P200000800\r', '!02\r', dict(addr = 2, encoder = 2, value=0x800), dict(addr = 2))

if __name__ == '__main__':
    unittest.main(verbosity=2)

