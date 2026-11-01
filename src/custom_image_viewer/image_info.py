from __future__ import annotations

import datetime
import logging
import webbrowser
from pathlib import Path

import folium
import pyexiv2
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim

from .config import MAP_POPUP_TEXT, MAP_ZOOM_START, get_data_dir

logger = logging.getLogger(__name__)


def _parse_gps_component(value: str) -> float:
    tokens = str(value).split()
    if not tokens:
        raise ValueError("Empty GPS component")
    total = 0.0
    for index, token in enumerate(tokens):
        if "/" in token:
            numerator, denominator = token.split("/", 1)
            part = float(numerator) / float(denominator)
        else:
            part = float(token)
        total += part / (60**index)
    return total


def _parse_coordinate(value: str, ref: str | None) -> float | None:
    try:
        result = _parse_gps_component(value)
    except (ValueError, ZeroDivisionError):
        return None
    if ref in ("S", "W"):
        result = -result
    return round(result, 6)


class ImageInfo:
    def __init__(self, image_path: Path | None):
        self.image_path = Path(image_path) if image_path is not None else None
        self._metadata: dict | None = None

    def _read_exif_metadata(self) -> dict:
        if self.image_path is None or not self.image_path.exists():
            return {}
        try:
            with open(self.image_path, "rb") as handle:
                with pyexiv2.ImageData(handle.read()) as image_info:
                    return image_info.read_exif()
        except Exception as exc:
            logger.error(
                "Error reading EXIF metadata for %s: %s",
                self.image_path,
                exc,
            )
            return {}

    @property
    def metadata(self) -> dict:
        if self._metadata is None:
            self._metadata = self._read_exif_metadata()
        return self._metadata

    @property
    def device_model(self) -> str | None:
        return self.metadata.get("Exif.Image.Model")

    @property
    def device_make(self) -> str | None:
        return self.metadata.get("Exif.Image.Make")

    def _parse_datetime_info(self, datetime_info: str) -> datetime.datetime | None:
        try:
            if all(char.isdigit() for char in datetime_info):
                return datetime.datetime.fromtimestamp(int(datetime_info) / 1000)
            if any(char.isalpha() for char in datetime_info):
                return datetime.datetime.strptime(
                    datetime_info, "%b %d, %Y %H:%M:%S %p"
                )
            return datetime.datetime.strptime(datetime_info, "%Y:%m:%d %H:%M:%S")
        except (ValueError, OverflowError, OSError) as exc:
            logger.warning("Could not parse date %r: %s", datetime_info, exc)
            return None

    def get_datetime_info(self) -> str | None:
        for key in ("Exif.Image.DateTime", "Exif.Photo.DateTimeOriginal"):
            value = self.metadata.get(key)
            if value:
                return value
        if self.metadata:
            logger.error("No DateTime info extracted from %s.", self.image_path)
        return None

    @property
    def date(self) -> str | None:
        datetime_info = self.get_datetime_info()
        if not datetime_info:
            return None
        parsed = self._parse_datetime_info(datetime_info)
        return parsed.strftime("%B %d, %Y") if parsed else None

    @property
    def time(self) -> str | None:
        datetime_info = self.get_datetime_info()
        if not datetime_info:
            return None
        parsed = self._parse_datetime_info(datetime_info)
        return parsed.strftime("%I:%M %p") if parsed else None

    @property
    def coordinates(self) -> tuple[float, float] | None:
        latitude_info = self.metadata.get("Exif.GPSInfo.GPSLatitude")
        longitude_info = self.metadata.get("Exif.GPSInfo.GPSLongitude")
        if not latitude_info or not longitude_info:
            return None
        latitude = _parse_coordinate(
            latitude_info,
            self.metadata.get("Exif.GPSInfo.GPSLatitudeRef"),
        )
        longitude = _parse_coordinate(
            longitude_info,
            self.metadata.get("Exif.GPSInfo.GPSLongitudeRef"),
        )
        if latitude is None or longitude is None:
            return None
        return latitude, longitude

    @property
    def address(self) -> str | None:
        coordinates = self.coordinates
        if coordinates is None:
            return None
        latitude, longitude = coordinates
        geolocator = Nominatim(user_agent="image-viewer", timeout=5)
        try:
            location = geolocator.reverse((latitude, longitude), language="en")
        except (GeocoderTimedOut, GeocoderUnavailable) as exc:
            logger.error("Geocoding unavailable for %s: %s", self.image_path, exc)
            return None
        except Exception as exc:
            logger.error("Error during geocoding for %s: %s", self.image_path, exc)
            return None
        return location.address if location else None

    def view_location_on_map(self, output_dir: Path | None = None) -> Path | None:
        coordinates = self.coordinates
        if coordinates is None:
            return None
        latitude, longitude = coordinates
        map_location = folium.Map(
            location=[latitude, longitude], zoom_start=MAP_ZOOM_START
        )
        folium.Marker([latitude, longitude], popup=MAP_POPUP_TEXT).add_to(map_location)
        target_dir = output_dir or get_data_dir()
        stem = self.image_path.stem if self.image_path else "location"
        map_file = target_dir / f"{stem}_location.html"
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            map_location.save(str(map_file))
            webbrowser.open(str(map_file))
        except Exception as exc:
            logger.error("Could not write map for %s: %s", self.image_path, exc)
            return None
        return map_file
