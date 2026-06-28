# sensorData

A Raspberry Pi Pico 2W sensor logging project for collecting, validating, and analyzing hardware sensor data from a small embedded test bench.

This project is designed around an operator-engineer workflow: wire the sensor, verify the interface, collect clean logs, and turn those logs into useful engineering evidence.

## Project Goals

- Collect repeatable sensor data from a Raspberry Pi Pico 2W
- Validate sensor interfaces such as I2C and single-wire digital protocols
- Export timestamped CSV logs for analysis in Python, MATLAB, or spreadsheet tools
- Build reusable tooling for future bench experiments
- Practice embedded debugging, test automation, and hardware/software integration

## Current Hardware

### Microcontroller

- Raspberry Pi Pico 2W
- MicroPython firmware
- Connected over USB serial using `mpremote`

### Sensors

| Sensor | Interface | Status | Notes |
|---|---:|---:|---|
| MPU6050 IMU | I2C | Working | Accelerometer + gyroscope data |
| DHT11 | Single-wire digital | In progress | Pulse timing/decode work |
| BME280 | I2C/SPI | Planned | Temperature, pressure, humidity |
| Thermistor | ADC | Planned | Analog temperature characterization |
| HC-SR04 / SR04 | Digital pulse timing | Planned | Ultrasonic distance sensing |

## Current Pinout

### MPU6050

| Pico Pin | Function | MPU6050 Pin |
|---|---|---|
| GP6 | SDA | SDA |
| GP7 | SCL | SCL |
| 3V3 | Power | VCC |
| GND | Ground | GND |

I2C bus:

```python
I2C(1, sda=Pin(6), scl=Pin(7), freq=100000)
```

The MPU6050 typically appears at address:

```text
0x68
```

### DHT11

| Pico Pin | Function | DHT11 Pin |
|---|---|---|
| GP20 | Data | DATA |
| 3V3 | Power | VCC |
| GND | Ground | GND |

Current DHT11 work focuses on handshake timing, pulse capture, and threshold-based bit decoding.

## Repository Structure

```text
sensorData/
├── README.md
├── logCollector.sh
├── run_config.py
├── src/
│   ├── mpuData.py
│   ├── dht11Data.py
│   └── mpu6050.py
├── logs/
│   ├── mpu_YYYYMMDD_HHMMSS.csv
│   └── dht11_YYYYMMDD_HHMMSS.csv
├── analysis/
│   ├── matlab/
│   └── python/
└── docs/
    ├── wiring.md
    └── troubleshooting.md
```

If your scripts currently live at repo root, that is fine. This structure is a future cleanup target.

## Software Requirements

### Host Machine

- Linux
- Python 3
- `mpremote`
- Bash

Install `mpremote`:

```bash
python3 -m pip install mpremote
```

Verify the Pico is visible:

```bash
mpremote connect list
```

Typical serial device:

```text
/dev/ttyACM0
```

### Pico

- MicroPython installed
- Sensor scripts copied or run through `mpremote`

## Quick Start

From the repo root:

```bash
./logCollector.sh -i mpu -s 100 -f 10
```

Example meaning:

| Flag | Meaning |
|---|---|
| `-i mpu` | Sensor/script target |
| `-s 100` | Number of samples |
| `-f 10` | Sampling frequency in Hz |

Enable debug output:

```bash
./logCollector.sh -i mpu -s 100 -f 10 -d
```

Run DHT11 collection:

```bash
./logCollector.sh -i dht11 -s 20 -f 1
```

## Data Collection Workflow

The intended workflow is:

1. Wire the sensor
2. Confirm power and ground continuity
3. Confirm the bus/interface is visible
4. Run a short debug collection
5. Inspect output for obvious bad data
6. Run a longer collection
7. Save logs with timestamped filenames
8. Analyze trends, noise, timing, and failure modes

For I2C sensors, first confirm the device address appears before trusting sensor output.

Example I2C scan:

```python
from machine import Pin, I2C

i2c = I2C(1, sda=Pin(6), scl=Pin(7), freq=100000)
print(i2c.scan())
```

Expected MPU6050 result:

```text
[104]
```

`104` decimal is `0x68` hex.

## Output Logs

Logs are written as CSV files in the `logs/` directory.

Example filename:

```text
logs/mpu_20260628_143522.csv
```

Example MPU6050 CSV format:

```csv
timestamp_ms,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,temp
0,0.01,-0.03,0.98,0.12,-0.05,0.03,24.8
100,0.01,-0.02,0.99,0.11,-0.04,0.02,24.8
```

Exact columns may change as the project develops. When adding a new sensor, include a header row and keep units explicit wherever possible.

Recommended naming pattern:

```text
<sensor>_<YYYYMMDD>_<HHMMSS>.csv
```

## Script Overview

### `logCollector.sh`

Host-side collection wrapper.

Responsibilities:

- Parse collection parameters
- Generate/update `run_config.py`
- Copy configuration to the Pico
- Run the selected sensor script
- Pipe output to a timestamped CSV log
- Optionally show debug information

Example:

```bash
./logCollector.sh -i mpu -s 200 -f 20 -d
```

### `run_config.py`

Temporary or generated configuration file used by the Pico scripts.

Example:

```python
collectData = True
samplesRecorded = 100
frequencySamples = 10
```

### `mpuData.py`

Collects MPU6050 accelerometer, gyroscope, and temperature data.

Core responsibilities:

- Initialize I2C
- Wake the MPU6050
- Read raw registers
- Convert signed 16-bit values
- Output CSV rows

Important helper:

```python
def s16(value):
    return value - 65536 if value > 32767 else value
```

### `mpu6050.py`

Reusable MPU6050 driver/helper module.

Expected responsibilities:

- Register reads
- Raw data conversion
- Sensor scaling
- Calibration support

### `dht11Data.py`

Captures and decodes DHT11 pulse timing.

Current focus:

- Start signal generation
- Response pulse capture
- Bit thresholding
- Timeout handling
- Data validation/checksum work

## Known Issues / Lessons Learned

### Breadboard Power Rails

Some breadboards split their power rails. If a sensor works when directly wired but fails on the breadboard, check whether the power rail is continuous across the whole board.

### I2C Frequency

The MPU6050 was more stable at:

```python
freq=100000
```

rather than higher speeds during early testing.

### Pico Serial Lockups

If VSCode or another REPL is holding the serial port, `mpremote` may fail. Close other serial sessions or identify the process using:

```bash
lsof /dev/ttyACM0
```

Then stop the blocking process if needed.

### DHT11 Timing

DHT11 decoding is sensitive to pulse timing. Current debugging has shown captured pulses, but timeout behavior can occur near the end of the message. This is likely a timing/threshold/edge-capture issue rather than necessarily a wiring issue.

## Troubleshooting

### Pico not detected

```bash
mpremote connect list
```

If no device appears:

- Unplug/replug the Pico
- Check USB cable supports data, not just charging
- Confirm `/dev/ttyACM0` or equivalent exists
- Close other serial monitors

### I2C sensor not found

Run an I2C scan. If no address appears:

- Check SDA/SCL are on the correct pins
- Check power and ground
- Lower I2C frequency
- Check breadboard rail continuity
- Try direct jumper wiring
- Confirm sensor voltage compatibility

### CSV file is empty

Check:

- The Pico script actually prints CSV rows
- `logCollector.sh` is piping output correctly
- The selected sensor name maps to the correct script
- The script is not exiting early due to import/config errors

### Bad or noisy data

Check:

- Loose wiring
- Shared ground
- Sensor orientation
- Sampling frequency
- Power stability
- Whether the sensor needs calibration

## Engineering Notes

This project treats sensor collection as a test and integration problem, not just a coding exercise.

For each sensor, the useful debug questions are:

- Is the interface alive?
- Is the data plausible?
- Is the timing stable?
- Is the failure electrical, protocol-level, software-level, or physical?
- Can the result be reproduced?
- Can the log explain what happened after the fact?

## Roadmap

### Near-Term

- Clean up repo structure
- Stabilize DHT11 decoding
- Add sensor-specific README notes
- Add calibration routine for MPU6050
- Add automatic I2C scan utility
- Add better log metadata headers
- Add Python plotting scripts

### Medium-Term

- Add BME280 support
- Add thermistor ADC support
- Add SR04 distance measurement
- Add MATLAB import/analysis templates
- Add sensor health checks
- Add simple test harness for each sensor script

### Long-Term

- Build a reusable embedded data collection framework
- Support multi-sensor synchronized logging
- Add structured experiment configs
- Create repeatable thermal, motion, and environmental test setups
- Use the project as a portfolio artifact for test/integration engineering

## Example Commands

Collect 100 MPU samples at 10 Hz:

```bash
./logCollector.sh -i mpu -s 100 -f 10
```

Collect 300 MPU samples at 20 Hz with debug:

```bash
./logCollector.sh -i mpu -s 300 -f 20 -d
```

Collect DHT11 data:

```bash
./logCollector.sh -i dht11 -s 20 -f 1
```

List connected Pico devices:

```bash
mpremote connect list
```

Open a Pico REPL:

```bash
mpremote repl
```

Copy a file to the Pico:

```bash
mpremote cp src/mpuData.py :mpuData.py
```

Run a file on the Pico:

```bash
mpremote run src/mpuData.py
```

## Design Philosophy

Observe directly. 
Validate physically. 
Debug iteratively.

The goal is not just to make sensors print numbers. The goal is to build a bench workflow where hardware behavior can be captured, trusted, analyzed, and improved.
