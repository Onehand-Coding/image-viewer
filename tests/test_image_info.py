import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from custom_image_viewer import image_info
from custom_image_viewer.image_info import (
    ImageInfo,
    _parse_coordinate,
    _parse_gps_component,
)


def make_info(metadata):
    info = ImageInfo(Path("test.jpg"))
    info._metadata = metadata
    return info


def test_metadata_is_cached():
    info = ImageInfo(Path("test.jpg"))
    calls = []
    info._read_exif_metadata = lambda: calls.append(1) or {"Exif.Image.Model": "M"}
    assert info.metadata == {"Exif.Image.Model": "M"}
    assert info.metadata == {"Exif.Image.Model": "M"}
    assert len(calls) == 1


def test_device_properties():
    info = make_info({"Exif.Image.Make": "TestMake", "Exif.Image.Model": "TestModel"})
    assert info.device_make == "TestMake"
    assert info.device_model == "TestModel"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("2021:03:21 12:34:56", datetime.datetime(2021, 3, 21, 12, 34, 56)),
        ("Dec 8, 2018 8:14:03 AM", datetime.datetime(2018, 12, 8, 8, 14, 3)),
    ],
)
def test_parse_datetime_formats(raw, expected):
    assert make_info({})._parse_datetime_info(raw) == expected


def test_parse_datetime_epoch():
    parsed = make_info({})._parse_datetime_info("1616347542050")
    assert parsed is not None
    assert parsed.year == 2021


def test_parse_datetime_bad_returns_none():
    assert make_info({})._parse_datetime_info("not a date") is None


def test_date_and_time():
    info = make_info({"Exif.Image.DateTime": "2021:03:21 12:34:56"})
    assert info.date == "March 21, 2021"
    assert info.time == "12:34 PM"


def test_gps_component_parsing():
    assert _parse_gps_component("14/1 35/1 0/1") == pytest.approx(14.583333, abs=1e-6)
    assert _parse_gps_component("14 35 0") == pytest.approx(14.583333, abs=1e-6)


def test_coordinate_refs():
    assert _parse_coordinate("14/1 35/1 0/1", "N") == 14.583333
    assert _parse_coordinate("14/1 35/1 0/1", "S") == -14.583333
    assert _parse_coordinate("bad", "N") is None


def test_coordinates_north_east():
    info = make_info(
        {
            "Exif.GPSInfo.GPSLatitude": "14/1 35/1 0/1",
            "Exif.GPSInfo.GPSLatitudeRef": "N",
            "Exif.GPSInfo.GPSLongitude": "120/1 58/1 0/1",
            "Exif.GPSInfo.GPSLongitudeRef": "E",
        }
    )
    assert info.coordinates == (14.583333, 120.966667)


def test_coordinates_south_west():
    info = make_info(
        {
            "Exif.GPSInfo.GPSLatitude": "14/1 35/1 0/1",
            "Exif.GPSInfo.GPSLatitudeRef": "S",
            "Exif.GPSInfo.GPSLongitude": "120/1 58/1 0/1",
            "Exif.GPSInfo.GPSLongitudeRef": "W",
        }
    )
    assert info.coordinates == (-14.583333, -120.966667)


def test_coordinates_missing_or_bad():
    assert make_info({}).coordinates is None
    assert (
        make_info(
            {
                "Exif.GPSInfo.GPSLatitude": "bad",
                "Exif.GPSInfo.GPSLongitude": "bad",
            }
        ).coordinates
        is None
    )


def test_address_uses_geocoder(monkeypatch):
    info = make_info(
        {
            "Exif.GPSInfo.GPSLatitude": "14/1 35/1 0/1",
            "Exif.GPSInfo.GPSLatitudeRef": "N",
            "Exif.GPSInfo.GPSLongitude": "120/1 58/1 0/1",
            "Exif.GPSInfo.GPSLongitudeRef": "E",
        }
    )
    geocoder = MagicMock()
    geocoder.reverse.return_value.address = "Somewhere"
    monkeypatch.setattr(image_info, "Nominatim", lambda **kwargs: geocoder)

    assert info.address == "Somewhere"
    geocoder.reverse.assert_called_once_with((14.583333, 120.966667), language="en")


def test_address_failure_returns_none(monkeypatch):
    info = make_info(
        {
            "Exif.GPSInfo.GPSLatitude": "14/1 35/1 0/1",
            "Exif.GPSInfo.GPSLongitude": "120/1 58/1 0/1",
        }
    )
    geocoder = MagicMock()
    geocoder.reverse.side_effect = image_info.GeocoderUnavailable("down")
    monkeypatch.setattr(image_info, "Nominatim", lambda **kwargs: geocoder)

    assert info.address is None


def test_view_location_on_map_writes_file(tmp_path, monkeypatch):
    info = make_info(
        {
            "Exif.GPSInfo.GPSLatitude": "14/1 35/1 0/1",
            "Exif.GPSInfo.GPSLatitudeRef": "N",
            "Exif.GPSInfo.GPSLongitude": "120/1 58/1 0/1",
            "Exif.GPSInfo.GPSLongitudeRef": "E",
        }
    )
    opened = []
    monkeypatch.setattr(image_info.webbrowser, "open", lambda url: opened.append(url))

    map_file = info.view_location_on_map(tmp_path)

    assert map_file is not None
    assert map_file.exists()
    assert map_file.stat().st_size > 0
    assert opened == [str(map_file)]


def test_view_location_without_gps_returns_none(tmp_path, monkeypatch):
    info = make_info({})
    opened = []
    monkeypatch.setattr(image_info.webbrowser, "open", lambda url: opened.append(url))

    assert info.view_location_on_map(tmp_path) is None
    assert opened == []


def test_read_exif_missing_file_returns_empty():
    assert ImageInfo(Path("missing.jpg")).metadata == {}
