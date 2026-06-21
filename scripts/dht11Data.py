## This is a script to collect temperature + humidity data from a connected DHT11 module

## Import needed modules/libraries
import gc
import sys
from machine import Pin, time_pulse_us
from time import sleep_ms, sleep_us

try:
    from run_config import samplesRecorded, collectData
except ImportError:
    samplesRecorded = 100

## Initialize Variables

frequencySamples = 1

# Define boolean config settings

print("humidity,temperatureF,checksumOK")

debug = False
calibrateThreshold = True

# Initialize hardware pin GC20

dataPin = Pin(20)

# Define integer config settings
handshakeLimit = 5
pulseThreshold = 45
humidityOffset = -13        # Measured delta w/ 2nd "true" sensor @ 50% RH
tempOffset = -0.7
period_ms = int(1000 / frequencySamples)

def dht11Start(handshakeFailed):
    bitDecode = []
    bytesOut = []
    readFail, readSuccess = ((0, 0))
    lowHeader = [0] * 40
    highPulse = [0] * 40

    dataPin.init(Pin.OUT, Pin.PULL_UP)
    gc.collect()
    gc.disable()  

    dataPin.value(0)
    sleep_ms(18)
    dataPin.value(1)
    sleep_us(20)

    dataPin.init(Pin.IN,Pin.PULL_UP)

    handshakeResponseA = time_pulse_us(dataPin, 0, 100)
    handshakeResponseB = time_pulse_us(dataPin, 1, 100)    
    
    if handshakeResponseA == -1 or handshakeResponseB == -1 :
        gc.enable()

        print("Handshake failed ", handshakeFailed + 1, "times, retrying ", handshakeLimit, "times")
    
        if handshakeFailed < 5:# and handshakeResponseA is None or handshakeResponseB is None:
            sleep_ms(1000)
            return dht11Start(handshakeFailed + 1)
        else:
            raise AssertionError("Failed DHT11 handshake ", handshakeFailed, "times")

    for i in range(40):
        lowHeader[i] = (time_pulse_us(dataPin, 0, 100))
        highPulse[i] = (time_pulse_us(dataPin, 1, 100))
    
    gc.enable()

    for i in range(40):
        if lowHeader[i] < 0 or highPulse[i] < 0:
            readFail += 1
        elif 1 < lowHeader[i] < 50:
            if highPulse[i] > pulseThreshold:
                bitDecode.append(1)
            else:
                bitDecode.append(0)
            readSuccess += 1

    for start in range(0, 40, 8):
        byte = 0
        for bit in bitDecode[start:start+8]:
            byte = (byte << 1) | bit
        bytesOut.append(byte)

    thresholdError = 100*(readFail / max(readSuccess, 1))

    if debug == True:
        print("Read threshold error (%): " , 100*thresholdError, "\n", "Bits read successfully: ", readSuccess, "\n", "Bits failed to read: ", readFail, "\n", sep="")

    return bytesOut

for sample in range(samplesRecorded):

    bytesOut = dht11Start(0)

    if len(bytesOut) != 5:
        print("bad_read,bad_read,False")
        sleep_ms(period_ms)
        continue

    checksumExpected = sum(bytesOut[:4]) & 0xFF
    checksumReceived = bytesOut[4]
    checksumOK = checksumExpected == checksumReceived

    humidity = float(int(bytesOut[0] + humidityOffset) + float(bytesOut[1]/100))
    tempF = int(9/5 * (bytesOut[2] + bytesOut[3]/10)) + 32

    print(
        f"{humidity},{tempF},{checksumOK}")

    sleep_ms(period_ms)