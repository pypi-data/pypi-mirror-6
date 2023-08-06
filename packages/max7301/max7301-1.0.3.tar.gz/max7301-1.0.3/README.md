max7301
==========

A python library to control a MAX7301.
It uses spidev to talk to the chip.

# Installation on Raspberry Pi
1. sudo pip install max7301
2. sudo py-max7301-rpi-spi-setup
3. reboot
4. PROFIT

# Example

```
import max7301
import time

device = max7301.MAX7301()

device.set_pin_as_output(30)
device.set_pin_as_input(31, pullup = False)

while 1:
    device.set_pin(30, 1)
    time.sleep(0.1)
    print "Pin 31 =", device.get_pin(31)
    device.set_pin(30, 0)
    time.sleep(0.1)
    print "Pin 31 =", device.get_pin(31)
```
