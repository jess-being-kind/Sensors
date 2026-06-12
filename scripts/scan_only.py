from machine import Pin, I2C
from time import sleep

# Match your actual wiring
i2c = I2C(1, sda=Pin(6), scl=Pin(7), freq=100000)

while True:
    devices = i2c.scan()
    print("I2C devices:", [hex(addr) for addr in devices])
    sleep(1)
