from pathlib import Path

rootFolder = Path.home() / "Engineering/Python/VSCode/sensorData/logs"

print("Log directory:", rootFolder )
print("Exists:", rootFolder.exists())

# 

logMatch = sorted(rootFolder.glob("*.csv"), key=lambda p: p.stat().st_mtime)

if not logMatch:
    raise FileNotFoundError("No .csv logs found")

latest = logMatch[-1]

print("Latest .csv log file:", latest)

