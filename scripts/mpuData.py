# Import Modules:
from machine import Pin, I2C, reset  # type: ignore
from time import sleep, ticks_ms
import functions  # type: ignore | Import the s16 function for converting raw data to signed integers

# Define variables and initialize I2C communication with MPU6050:
mpu6050 = 0x68  # Hex address for mpu6050

i2c = I2C(1, sda=Pin(6), scl=Pin(7), freq=400000)           # GP6 = SDA, GP7 = SCL
awake = i2c.scan()  # Check if MPU6050 is responding
calibrate = True   # Set to True to perform calibration

numsteps = 500     # Number of readings to average for calibration [ms]
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
while True: 

    timestamp = ticks_ms() / 1000  # Get current timestamp in seconds
    data = i2c.readfrom_mem(mpu6050, 0x3B, 14)  # Read 14 bytes of data starting from register 0x3B
    
    # Instantaneous raw values from MPU6050 converted to signed integers
    axI: float = functions.s16(data[0], data[1])
    ayI: float = functions.s16(data[2], data[3])
    azI: float = functions.s16(data[4], data[5])
    gxI: float = functions.s16(data[8], data[9])
    gyI: float = functions.s16(data[10], data[11])
    gzI: float = functions.s16(data[12], data[13])

    if calibrate:
        print("Calibrating... Please keep the sensor stationary and level.")
        for i in range(numsteps):                   # Take multiple readings to average for calibration
            
            # Accumulate raw values for averaging
            ax += axI
            ay += ayI
            az += azI
            gx += gxI
            gy += gyI
            gz += gzI

            sleep(0.01)  # Short delay between readings to avoid overwhelming the sensor

        # Average raw values to get offsets
        axO = (ax // numsteps) #// 16384  # Convert to g's for accelerometer
        ayO = (ay // numsteps) #// 16384
        azO = (az // numsteps) #// 16384
        gxO = (gx // numsteps) #// 131  # Convert to °/s for gyroscope
        gyO = (gy // numsteps) #// 131
        gzO = (gz // numsteps) #// 131

        print(f"Calibration complete. Offsets - Accel: ({axO}, {ayO}, {azO}), Gyro: ({gxO}, {gyO}, {gzO})")
        calibrate = False
        
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

    """ 
    print(
    f"{ticks_ms()},"
    f"{axC:.5f},{ayC:.5f},{azC:.5f},"
    f"{gxC:.5f},{gyC:.5f},{gzC:.5f},"
    f"{temp_c:.2f}"
) """
    sleep(.025)  # Delay to control the data output rate (40 Hz)
