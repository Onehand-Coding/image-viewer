import logging
import datetime
import webbrowser

import folium
import pyexiv2
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

from .config import DATA_FOLDER, MAP_ZOOM_START, MAP_POPUP_TEXT

logger = logging.getLogger(__name__)


class ImageInfo:
    def __init__(self, image_path):
        self.image_path = image_path

    def _read_exif_metadata(self):
        try:
            with open(self.image_path, "rb") as f:
                with pyexiv2.ImageData(f.read()) as image_info:
                    return image_info.read_exif()
        except Exception as e:
            logger.error(f"Error reading EXIF metadata for {self.image_path}: {e}")
            return {}

    @property
    def metadata(self):
        return self._read_exif_metadata()

    @property
    def device_model(self):
        return self.metadata.get("Exif.Image.Model")

    @property
    def device_make(self):
        return self.metadata.get("Exif.Image.Make")

    @property
    def date(self):
        datetime_info = self.get_datetime_info()
        return (
            self._parse_datetime_info(datetime_info).strftime("%B %d, %Y")
            if datetime_info
            else None
        )

    @property
    def time(self):
        datetime_info = self.get_datetime_info()
        return (
            self._parse_datetime_info(datetime_info).strftime("%I:%M %p")
            if datetime_info
            else None
        )

    def _parse_datetime_info(self, datetime_info):
        # parse from format like this: '1616347542050'
        if all(char.isdigit() for char in datetime_info):
            date_and_time = int(datetime_info) / 1000
            return datetime.datetime.fromtimestamp(date_and_time)

        # parse from format like this: 'Dec 8, 2018 8:14:03 AM'
        if any(char.isalpha() for char in datetime_info):
            return datetime.datetime.strptime(datetime_info, "%b %d, %Y %H:%M:%S %p")
        else:
            # parse from format like this: '2017:04:01 18:57:18'
            return datetime.datetime.strptime(datetime_info, "%Y:%m:%d %H:%M:%S")

    def get_datetime_info(self):
        exif_datetime_keys = ("Exif.Image.DateTime", "Exif.Photo.DateTimeOriginal")
        datetime_info = [
            self.metadata.get(key)
            for key in exif_datetime_keys
            if self.metadata.get(key)
        ]

        datetime_info = datetime_info[0] if datetime_info else None
        if datetime_info is None:
            if self.metadata:
                logger.error(f"No DateTime info extracted from {self.image_path}.")
            else:
                logger.error(f"No metadata available for {self.image_path}.")

        return datetime_info

    @property
    def coordinates(self):
        latitude_info = self.metadata.get("Exif.GPSInfo.GPSLatitude")
        longitude_info = self.metadata.get("Exif.GPSInfo.GPSLongitude")

        if latitude_info and longitude_info:
            latitude = sum(
                (value / 60**i)
                for i, value in enumerate(map(eval, latitude_info.split()))
            )
            longitude = sum(
                (value / 60**i)
                for i, value in enumerate(map(eval, longitude_info.split()))
            )

            return round(latitude, 6), round(longitude, 6)

    @property
    def address(self):
        if self.coordinates:
            latitude, longitude = self.coordinates
            geolocator = Nominatim(user_agent="image_locator")
            try:
                location = geolocator.reverse((latitude, longitude), language="en")
                return location.address
            except (GeocoderTimedOut, GeocoderUnavailable) as e:
                logger.error(f"Error during geocoding for {self.image_path}: {e}")
            except Exception as e:
                logger.error(f"Error during geocoding for {self.image_path}: {e}")
        return None

    def view_location_on_map(self):
        latitude, longitude = self.coordinates

        map_location = folium.Map(
            location=[latitude, longitude], zoom_start=MAP_ZOOM_START
        )
        folium.Marker([latitude, longitude], popup=MAP_POPUP_TEXT).add_to(map_location)
        map_file = DATA_FOLDER / "location.html"
        map_location.save(map_file)
        webbrowser.open(str(map_file))
