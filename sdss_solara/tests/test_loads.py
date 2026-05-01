import pytest

from sdss_solara.pages.jdaviz_embed import get_specformat


TEST_FILES = [
    (
        "spectro/boss/redux/v6_2_1/spectra/epoch/lite/112XXX/112360/60287/spec-112360-60287-27021603143302004.fits",
        "SDSS-V spec",
    ),
    (
        "spectro/boss/redux/v6_2_1/spectra/epoch/lite/100XXX/100129/60624/spec-100129-60624-63050394785558224.fits",
        "SDSS-V spec",
    ),
    (
        "spectro/boss/redux/v6_2_1/spectra/allepoch/lite/allepoch/allepoch_apo/59373/spec-allepoch_apo-59373-4351657527.fits",
        "SDSS-V spec",
    ),
    (
        "dr17/sdss/spectro/redux/26/spectra/lite/2895/spec-2895-54567-0346.fits",
        "SDSS-III/IV spec",
    ),
    (
        "dr17/manga/spectro/redux/v3_1_1/8485/stack/manga-8485-1901-LOGCUBE.fits.gz",
        "MaNGA cube",
    ),
    (
        "dr17/manga/spectro/redux/v3_1_1/8485/stack/manga-8485-1901-LOGRSS.fits.gz",
        "MaNGA rss",
    ),
    (
        "apogee/spectro/redux/dr17/stars/apo25m/293+62_btx/apStar-dr17-2M12305537+0034282.fits",
        "APOGEE apStar",
    ),
    (
        "apogee/spectro/redux/dr17/visit/apo25m/100129/16442/60595/apVisit-1.5-apo25m-16442-60595-211.fits",
        "APOGEE apVisit",
    ),
    (
        "dr17/eboss/spectro/redux/v5_13_2/spectra/lite/10235/spec-10235-58127-0006.fits",
        "SDSS-III/IV spec",
    ),
    (
        "spectro/boss/redux/v6_2_1/spectra/epoch/lite/112XXX/112360/60287/spec-112360-60287-27021603143302004.fits",
        "SDSS-V spec",
    ),
    (
        "spectro/boss/redux/v6_2_1/spectra/allepoch/lite/allepoch/allepoch_apo/59373/spec-allepoch_apo-59373-4351657527.fits",
        "SDSS-V spec",
    ),
    (
        "spectro/boss/redux/v6_2_1/spectra/daily/lite/100XXX/100129/59805/spec-100129-59805-27021597855027663.fits",
        "SDSS-V spec",
    ),
    (
        "spectro/apogee/redux/1.5/stars/apo25m/11/11410/apStar-1.5-apo25m-2M00490869+6205128.fits",
        "SDSS-V apStar",
    ),
    (
        "spectro/apogee/redux/1.5/visit/apo25m/100129/16442/60595/apVisit-1.5-apo25m-16442-60595-211.fits",
        "SDSS-V apVisit",
    ),
    ("spectro/astra/spectra/star/92/73/mwmStar-0.8.0-54459273.fits", "SDSS-V mwm"),
    ("spectro/astra/spectra/visit/92/73/mwmVisit-0.8.0-54459273.fits", "SDSS-V mwm"),
]


@pytest.mark.parametrize("filepath, expected", TEST_FILES)
def test_get_specformat(filepath, expected):
    assert get_specformat(filepath) == expected
