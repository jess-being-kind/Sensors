from machine import Pin, I2C
from time import sleep

MPU = 0x68

i2c = I2C(1, sda=Pin(6), scl=Pin(7), freq=10000)

print("scan:", [hex(addr) for addr in i2c.scan()])

whoami = i2c.readfrom_mem(MPU, 0x75, 1)[0]
print("WHO_AM_I:", hex(whoami))

i2c.writeto_mem(MPU, 0x6B, b'\x00')
sleep(0.1)

data = i2c.readfrom_mem(MPU, 0x3B, 14)
print("raw bytes:", data)
