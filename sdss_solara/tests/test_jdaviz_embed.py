import h5py
import numpy as np
import pytest
from astropy import units as u
from unittest.mock import Mock

from sdss_solara.components import message
from sdss_solara.pages import jdaviz_embed


@pytest.fixture(autouse=True)
def reset_reactive_state():
    """Fixture to reset the global reactive variables"""
    jdaviz_embed.new_files.value = []
    jdaviz_embed.filemap.value = {}
    jdaviz_embed.all_files.value = []
    jdaviz_embed.selected.value = []
    jdaviz_embed.params.value = {}
    jdaviz_embed.spec.value = None
    jdaviz_embed.apmadgics_input.value = {}
    message.new_files.value = []
    message.apmadgics_input.value = {}
    message.outmsg.value = {}
    yield


def test_get_madgic_spectrum(tmp_path, mocker):
    """Test we can get an apmadgics spectrum"""
    spectra = np.arange(2 * 8700, dtype=np.float32).reshape(2, 8700)
    spectrum_path = tmp_path / "spectra.h5"
    with h5py.File(spectrum_path, "w") as hdf5_file:
        hdf5_file.create_dataset("apVisit_v0", data=spectra)

    # mock the path access
    access = mocker.patch.object(jdaviz_embed, "Access")
    access.return_value.full.return_value = str(spectrum_path)

    # get the spectrum
    spectrum = jdaviz_embed.get_madgic_spectrum(
        magicid=2,
        star_prior="th",
        vers="vtest",
        release="DR19",
    )

    access.assert_called_once_with(release="DR19")
    access.return_value.full.assert_called_once_with(
        "apMADGICS_out_apVisit_v0",
        star_prior_type="th",
        vers="vtest",
    )
    np.testing.assert_array_equal(spectrum.flux.value, spectra[1])
    assert spectrum.spectral_axis.shape == (8700,)
    assert spectrum.spectral_axis.unit == u.Angstrom


def test_consume_new_files(mocker):
    """test we can response to incoming new files"""
    filepath = "/sas/spectro/astra/spectra/star/mwmStar-0.8.0-54459273.fits"
    app = Mock()
    check_file_exists = mocker.patch.object(jdaviz_embed, "check_file_exists", return_value=True)
    load_data = mocker.patch.object(jdaviz_embed, "load_data")
    jdaviz_embed.new_files.value = [filepath]
    jdaviz_embed.params.value = {"release": "DR19"}
    jdaviz_embed.spec.value = app

    jdaviz_embed.consume_new_files()

    check_file_exists.assert_called_once_with(filepath, "DR19")
    assert jdaviz_embed.filemap.value == {"mwmStar-0.8.0-54459273": filepath}
    assert jdaviz_embed.selected.value == ["mwmStar-0.8.0-54459273"]
    load_data.assert_called_once_with(app, filepath, resize=True)
    assert jdaviz_embed.new_files.value == []


def test_consume_apmadgics(mocker):
    """test we can respond to an incoming request for an apmadgics spectrum"""
    spectrum = object()
    app = Mock()
    loader = Mock()
    app.loaders = {"object": loader}
    get_spectrum = mocker.patch.object(jdaviz_embed, "get_madgic_spectrum", return_value=spectrum)
    jdaviz_embed.spec.value = app
    jdaviz_embed.apmadgics_input.value = {
        "sdssid": 12345,
        "idx": 8,
        "mjd": 59000,
        "plate": 100,
        "star_prior": "th",
    }

    jdaviz_embed.consume_apmadgics()

    get_spectrum.assert_called_once_with(magicid=8, star_prior="th")
    assert loader.object is spectrum
    assert loader.format == "1D Spectrum"
    assert loader.importer.data_label == "apMADGICS_th_visit_12345_59000"
    loader.load.assert_called_once_with()
    assert jdaviz_embed.apmadgics_input.value == {}


@pytest.mark.parametrize(
    ("data", "expected_files", "expected_input", "expected_message"),
    [
        (
            {"type": "updateFiles", "files": ["/sas/one.fits", "", "/sas/two.fits"]},
            ["/sas/one.fits", "", "/sas/two.fits"],
            {},
            {"type": "success", "message": "Files updated successfully"},
        ),
        (
            {
                "type": "loadApMadgics",
                "sdssid": 12345,
                "idx": 8,
                "mjd": 59000,
                "plate": 6000,
                "star_prior": "th",
            },
            [],
            {"sdssid": 12345, "idx": 8, "mjd": 59000, "plate": 6000, "star_prior": "th"},
            {"type": "success", "message": "ApMadgics request received"},
        ),
    ],
)
def test_event_handler(data, expected_files, expected_input, expected_message):
    """test the message event_handler"""
    message.event_handler(data)

    assert message.new_files.value == expected_files
    assert message.apmadgics_input.value == expected_input
    assert message.outmsg.value == expected_message
