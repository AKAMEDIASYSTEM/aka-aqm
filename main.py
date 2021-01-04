#! /usr/bin/python3
"""
Query Open Weather API and AHT20 qwiic sensor.
Display results on eInk bonnet.
Based off of https://learn.adafruit.com/raspberry-pi-e-ink-weather-station-using-python/weather-station-code
AKA 2020
"""

import time
import urllib.request
import urllib.parse
import digitalio
import busio
import smbus
import board
from adafruit_epd.ssd1675 import Adafruit_SSD1675
from weather_graphics import Weather_Graphics
import adafruit_ahtx0
import json
from akakeysreal import ak


spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
ecs = digitalio.DigitalInOut(board.CE0)
dc = digitalio.DigitalInOut(board.D22)
rst = digitalio.DigitalInOut(board.D27)
busy = digitalio.DigitalInOut(board.D17)

bus = smbus.SMBus(1)
i2c = busio.I2C(board.SCL, board.SDA)
aht20 = adafruit_ahtx0.AHTx0(i2c)

teensy_msg_len = 29  # our teensy code always sends fixed-len response
teensy_address = 0x77

if ak["OPEN_WEATHER_TOKEN"] == "DUMMY_VALUE":
    raise RuntimeError(
        "You need to set your token first. If you don't already have one, you can register for a free account at https://home.openweathermap.org/users/sign_up"
    )

# Set up where we'll be fetching data from
params = {"q": ak["LOCATION"], "appid": ak["OPEN_WEATHER_TOKEN"]}
data_source = ak["DATA_SOURCE_URL"] + "?" + urllib.parse.urlencode(params)

# Initialize the Display
display = Adafruit_SSD1675(
    122, 250, spi, cs_pin=ecs, dc_pin=dc, sramcs_pin=None, rst_pin=rst, busy_pin=busy,
)

display.rotation = 1

gfx = Weather_Graphics(display, am_pm=True, celsius=False)
weather_refresh = None
reading = {}
tomp = {}
SAMPLE_DEPTH = 250  # number of minutes of data to retain, here we choose 250mins, width of eink display


def init_readings():
    """Fill sample buffer with zeroes."""
    reading['aqiA'] = [0] * SAMPLE_DEPTH
    reading['aqiB'] = [0] * SAMPLE_DEPTH
    reading['pm25A'] = [0] * SAMPLE_DEPTH
    reading['pm25B'] = [0] * SAMPLE_DEPTH
    reading['pm4A'] = [0] * SAMPLE_DEPTH
    reading['pm4B'] = [0] * SAMPLE_DEPTH


def get_reading():
    """Test function."""
    # Write out I2C command: address, reg_write_dac, msg[0], msg[1]
    # msg = random.getrandbits(8)
    # bus.write_byte_data(address, reg_write_datareq, msg)

    # payload = bus.read_i2c_block_data(address, 0, msg_len)
    payload = bytearray(teensy_msg_len)
    i2c.readfrom_into(teensy_address, payload)
    for i in reading:
        reading[i].pop(0)
    reading['aqiA'].append(collapse(payload[0:4]))
    reading['aqiB'].append(collapse(payload[5:9]))
    reading['pm25A'].append(collapse(payload[10:14]))
    reading['pm25B'].append(collapse(payload[15:19]))
    reading['pm4A'].append(collapse(payload[20:24]))
    reading['pm4B'].append(collapse(payload[25:29]))


def collapse(intlist):
    """Collapse a list of int values of chars into the int they represent."""
    f = ''
    for i in intlist:
        f += chr(i)
    return int(f)


init_readings()
while True:
    get_reading()
    # only query the weather every 10 minutes (and on first run)
    if (not weather_refresh) or (time.monotonic() - weather_refresh) > ak["REFRESH_INTERVAL"]:
        response = urllib.request.urlopen(data_source)
        if response.getcode() == 200:
            value = response.read()
            tomp = json.loads(value)
            tomp['ttmp'] = "{:.01f}".format(aht20.temperature)
            tomp['thum'] = "{:.0f}".format(aht20.relative_humidity)
            tomp['aqiA'] = reading['aqiA']
            tomp['aqiB'] = reading['aqiB']
            tomp['pm25A'] = reading['pm25A']
            tomp['pm25B'] = reading['pm25B']
            tomp['pm4A'] = reading['pm4A']
            tomp['pm4B'] = reading['pm4B']
            if ak["VERBOSE"]:
                print("Response is", tomp)
            gfx.display_weather(json.dumps(tomp))
            weather_refresh = time.monotonic()
        else:
            print("Unable to retrieve data at {}".format(data_source))
    else:
        tomp['ttmp'] = "{:.01f}".format(aht20.temperature)
        tomp['thum'] = "{:.01f}".format(aht20.relative_humidity)
        tomp['aqiA'] = reading['aqiA']
        tomp['aqiB'] = reading['aqiB']
        tomp['pm25A'] = reading['pm25A']
        tomp['pm25B'] = reading['pm25B']
        tomp['pm4A'] = reading['pm4A']
        tomp['pm4B'] = reading['pm4B']
        if ak["VERBOSE"]:
            print("Response is", tomp)
    gfx.display_weather(json.dumps(tomp))
    time.sleep(60)  # wait 1+ minute before updating anything again, so the minutes-digit is sure to update
