import gc
import sys
from machine import Pin, I2C, time_pulse_us
from time import sleep_ms, sleep_us

try:
    from run_config import samplesRecorded as dataPoints, frequencySamples, collectData
except ImportError:
    samplesRecorded = 100
    frequencySamples = 2
    collectData = True

## Initialize Variables

i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=100000)           # GP6 = SDA, GP7 = SCL
awake = i2c.scan()  # Check if MPU6050 is responding
print(awake)
sleep_ms(10000)
calibrate = True   # Set to True to perform calibration

#if collectData:
