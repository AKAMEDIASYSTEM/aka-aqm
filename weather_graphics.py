"""Graphics class."""
from datetime import datetime
import json
import random
from PIL import Image, ImageDraw, ImageFont
from adafruit_epd.epd import Adafruit_EPD
import statistics

small_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16
)
medium_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
large_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24
)
icon_font = ImageFont.truetype("/usr/share/fonts/truetype/meteocons/meteocons.ttf", 48)

# Map the OpenWeatherMap icon code to the appropriate font character
# See http://www.alessioatzeni.com/meteocons/ for icons
ICON_MAP = {
    "01d": "B",
    "01n": "C",
    "02d": "H",
    "02n": "I",
    "03d": "N",
    "03n": "N",
    "04d": "Y",
    "04n": "Y",
    "09d": "Q",
    "09n": "Q",
    "10d": "R",
    "10n": "R",
    "11d": "Z",
    "11n": "Z",
    "13d": "W",
    "13n": "W",
    "50d": "J",
    "50n": "K",
}

# RGB Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Weather_Graphics:
    """GFX Class."""

    def __init__(self, display, *, am_pm=True, celsius=True):
        """Init, innit."""
        self.am_pm = am_pm
        self.celsius = celsius

        self.small_font = small_font
        self.medium_font = medium_font
        self.large_font = large_font

        self.display = display
        self.gheight = round(self.display.height / 4)

        self._weather_icon = None
        self._city_name = None
        self._main_text = None
        self._temperature = None
        self._description = None
        self._time_text = None
        # AKA added these two to come from local AHT20 qwiic module
        self._thum = None
        self._ttmp = None
        self._aqiA = None
        self._aqiB = None
        self._pm25A = None
        self._pm25B = None
        self._pm4A = None
        self._pm4B = None

    def display_weather(self, weather):
        """Display all the weather, not just time."""
        weather = json.loads(weather)
        # print(weather)
        # AKA added values from AHT20 as thum and ttmp
        # AKA added values from dual HPM particulate sensor
        self._thum = weather['thum']
        if self.celsius:
            self._ttmp = float(weather['ttmp'])
        else:
            self._ttmp = (float(weather['ttmp']) * 9 / 5 + 32)
        self._aqiA = weather['aqiA'][-1]
        self._aqiB = weather['aqiB'][-1]
        self._pm25A = weather['pm25A'][-1]
        self._pm25B = weather['pm25B'][-1]
        self._pm4A = weather['pm4A'][-1]
        self._pm4B = weather['pm4B'][-1]
        # experiment in showing all of timeseries
        self._aA = weather['aqiA']
        # set the icon/background
        self._weather_icon = ICON_MAP[weather["weather"][0]["icon"]]

        city_name = weather["name"] + ", " + weather["sys"]["country"]
        # print(city_name)
        self._city_name = city_name

        main = weather["weather"][0]["main"]
        # print(main)
        self._main_text = main

        temperature = weather["main"]["temp"] - 273.15  # its...in kelvin
        # print(temperature)
        if self.celsius:
            self._temperature = "%d °C" % temperature
        else:
            self._temperature = "%d °F" % ((temperature * 9 / 5) + 32)

        description = weather["weather"][0]["description"]
        description = description[0].upper() + description[1:]
        # print(description)
        self._description = description
        # "thunderstorm with heavy drizzle"

        self.update_time()

    def update_time(self):
        """Display updates just time."""
        now = datetime.now()
        self._time_text = now.strftime("%I:%M %p").lstrip("0").replace(" 0", " ")
        self.update_display()

    def update_display(self):
        """Display all the stuff, not just time."""
        self.display.fill(Adafruit_EPD.WHITE)
        image = Image.new("RGB", (self.display.width, self.display.height), color=WHITE)
        draw = ImageDraw.Draw(image)

        # Draw the Icon
        (font_width, font_height) = icon_font.getsize(self._weather_icon)
        draw.text(
            (
                self.display.width // 2 - font_width // 2,
                # self.display.height // 2 - font_height // 2 - 5,
                5,
            ),
            self._weather_icon,
            font=icon_font,
            fill=BLACK,
        )

        # Draw the time
        (font_width, font_height) = medium_font.getsize(self._time_text)
        draw.text(
            (5, 5),
            self._time_text,
            font=self.medium_font,
            fill=BLACK,
        )

        # Draw the Description, big
        # (font_width, font_height) = small_font.getsize(self._description)
        # draw.text(
        #     (self.display.width - font_width - 5, self.display.height - font_height * 2),
        #     self._description,
        #     font=self.small_font,
        #     fill=BLACK,
        # )

        # AKA added this to display local AHT20 values
        draw.text(
            (self.display.width - 85, 5), "{:.01f}".format(self._ttmp) + "ºF", font=self.medium_font, fill=BLACK,
        )
        # AKA added this to display local AHT20 values
        draw.text(
            (self.display.width - 85, 25), self._thum + "%h", font=self.medium_font, fill=BLACK,
        )

        # Draw the AQI and average PPMs
        aqi_str = "AQI: {}".format(int(statistics.mean([self._aqiA, self._aqiB])))
        (font_width, font_height) = small_font.getsize(aqi_str)
        draw.text(
            (
                # self.display.width - font_width - 5,
                5,
                font_height * 2,
            ),
            aqi_str,
            font=self.small_font,
            fill=BLACK,
        )
        # Draw the ppm averages
        ppm4_str = "ppm4: {}".format(int(statistics.mean([self._pm4A, self._pm4B])))
        (font_width, font_height) = small_font.getsize(ppm4_str)
        draw.text(
            (
                # self.display.width - font_width - 5,
                5,
                font_height * 3,
            ),
            ppm4_str,
            font=self.small_font,
            fill=BLACK,
        )

        ppm25_str = "ppm25 {}".format(int(statistics.mean([self._pm25A, self._pm25B])))
        (font_width, font_height) = small_font.getsize(ppm25_str)
        draw.text(
            (
                # self.display.width - font_width - 5,
                5,
                font_height * 4,
            ),
            ppm25_str,
            font=self.small_font,
            fill=BLACK,
        )
        print(self._aA)
        ra = max(self._aA) - min(self._aA)
        # bb = random.sample(range(rangee), self.display.width - 1)
        sc = (self.gheight / ra)
        for i, j in enumerate(self._aA):
            # [x1, y1, x2, y2]
            draw.line([i, self.display.height, i, round(self.display.height - (j * sc))], fill=BLACK)

        self.display.image(image)
        self.display.display()
