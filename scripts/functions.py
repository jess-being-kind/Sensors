# functions.py
# Pure logic can be used on Pico and Linux machine

def s16(high_byte, low_byte):
    """Convert two bytes into a signed 16-bit integer."""
    value = (high_byte << 8) | low_byte

    if value & 0x8000:
        value -= 0x10000

    return value