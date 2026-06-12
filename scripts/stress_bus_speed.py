from machine import Pin, I2C
from time import sleep

MPU = 0x68

for freq in [10000, 50000, 100000, 200000, 400000]:
    print()
    print("Testing freq:", freq)

    for i in range(5):
        try:
            i2c = I2C(1, sda=Pin(6), scl=Pin(7), freq=freq)
            sleep(0.2)

            devices = i2c.scan()
            print("scan:", [hex(addr) for addr in devices])

            if MPU not in devices:
                print("MPU not found at this speed")
                continue

            whoami = i2c.readfrom_mem(MPU, 0x75, 1)[0]
            print("WHO_AM_I:", hex(whoami))

            data = i2c.readfrom_mem(MPU, 0x3B, 14)
            print("raw data read OK:", data)

        except OSError as e:
            print("I2C error:", e)
    sleep(1)

