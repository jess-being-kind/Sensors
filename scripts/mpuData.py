# Import Modules:
from machine import Pin, I2C, reset  # type: ignore
from time import sleep, ticks_ms, sleep_ms
import functions  # type: ignore | Import the s16 function for converting raw data to signed integers
import os, sys

print("mpuData.py executing: YES")

if "run_config" in sys.modules:
    print("Found run_config.py")
    del sys.modules["run_config"]
try:
    from run_config import collectData, samplesRecorded, frequencySamples
except ImportError as e:
    print("ERROR: could not import run_config")
    print(e)
    import os, sys
    print("cwd:", os.getcwd())
    print("files:", os.listdir())
    print("sys.path:", sys.path)
    raise

print("CONFIG:", collectData, samplesRecorded, frequencySamples)

if frequencySamples < 50:
    print("Minimum sample frequency: 50Hz")
    frequencySamples = 50

# Define variables and initialize I2C communication with MPU6050:
mpu6050 = 0x68  # Hex address for mpu6050

i2c = I2C(1, sda=Pin(6), scl=Pin(7), freq=100000)           # GP6 = SDA, GP7 = SCL
awake = i2c.scan()  # Check if MPU6050 is responding
calibrate = True   # Set to True to perform calibration

calSamples = 100     # Number of readings to average for calibration [ms]
scaleAccel = 16384  # Scale factor for accelerometer (assuming ±2g range)
scaleGyro = 131    # Scale factor for gyroscope (assuming ±250°/s range)

ax = ay = az = gx = gy = gz = 0  # Initialize accumulators for raw values

if hex(mpu6050) in [hex(addr) for addr in awake]:
    print("MPU6050 found at address:", hex(mpu6050))
else:
    print("MPU6050 not found. Check connections.")
    raise Exception("MPU6050 not found")

i2c.writeto_mem(mpu6050, 0x6B, b'\x00')  # Set MPU6050 to wake mode by writing 0 to the power management register (0x6B)

# Main loop to read and calibrate MPU6050 data
for sample in range(samplesRecorded+calSamples):
    timestamp = ticks_ms() / 1000  # Get current timestamp in seconds
    data = i2c.readfrom_mem(mpu6050, 0x3B, 14)  # Read 14 bytes of data starting from register 0x3B
    
    # Instantaneous raw values from MPU6050 converted to signed integers
    axI: float = functions.s16(data[0], data[1])
    ayI: float = functions.s16(data[2], data[3])
    azI: float = functions.s16(data[4], data[5])
    gxI: float = functions.s16(data[8], data[9])
    gyI: float = functions.s16(data[10], data[11])
    gzI: float = functions.s16(data[12], data[13])

    if sample < calSamples:
        if sample == 1:
            print("Calibrating... Please keep the sensor stationary and level.")
 
        # Accumulate raw values for averaging
        ax += axI
        ay += ayI
        az += azI
        gx += gxI
        gy += gyI
        gz += gzI
        
        sleep(0.01)  # Short delay between readings to avoid overwhelming the sensor
    else:
        if sample == calSamples:
            # Average raw values to get offsets
            axO = (ax // calSamples) #// 16384  # Convert to g's for accelerometer
            ayO = (ay // calSamples) #// 16384
            azO = (az // calSamples) #// 16384
            gxO = (gx // calSamples) #// 131  # Convert to °/s for gyroscope
            gyO = (gy // calSamples) #// 131
            gzO = (gz // calSamples) #// 131

            print(f"Calibration complete. Offsets - Accel: ({axO}, {ayO}, {azO}), Gyro: ({gxO}, {gyO}, {gzO})")
            print("Samples collected: ", sample)

        axC = (axI - axO) / scaleAccel  # Convert to g's for accelerometer
        ayC = (ayI - ayO) / scaleAccel
        azC = (azI - azO) / scaleAccel
        
        if azI - azO < 0:
            sensorHIGH = -1*scaleAccel
        else:
            sensorHIGH = 1*scaleAccel

        azC = ((azI - azO) - sensorHIGH) / sensorHIGH # Subtract 1g from Z-axis to account for gravity
        
        gxC = (gxI - gxO) / scaleGyro # Convert to °/s for gyroscope
        gyC = (gyI - gyO) / scaleGyro
        gzC = (gzI - gzO) / scaleGyro

        raw_temp = functions.s16(data[6], data[7])
        temp_c = raw_temp / 340 + 36.53

        print(
        f"{ticks_ms()},"
        f"{axC:.5f},{ayC:.5f},{azC:.5f},"
        f"{gxC:.5f},{gyC:.5f},{gzC:.5f},"
        f"{temp_c*(9/5) + 27:.2f}"
        )

    sleep(1/frequencySamples)  # Delay to control the data output rate (40 Hz)
