import serial
from serial.tools import list_ports

print('pyserial version:', getattr(serial, '__version__', 'unknown'))
ports = list(list_ports.comports())
print('COM ports found:', ports)
