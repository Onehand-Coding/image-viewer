import pytest
from pathlib import Path
from custom_image_viewer.image_info import ImageInfo


@pytest.fixture
def image_info():
    return ImageInfo(Path("test_image.jpg"))


def test_image_info_init(image_info):
    assert isinstance(image_info.image_path, Path)
    assert str(image_info.image_path) == "test_image.jpg"


def test_metadata_property(image_info, mocker):
    mocker.patch.object(
        image_info,
        "_read_exif_metadata",
        return_value={"Exif.Image.Model": "TestCamera"},
    )
    assert image_info.metadata == {"Exif.Image.Model": "TestCamera"}


def test_device_model(image_info, mocker):
    mocker.patch.object(
        image_info,
        "_read_exif_metadata",
        return_value={"Exif.Image.Model": "TestCamera"},
    )
    assert image_info.device_model == "TestCamera"
