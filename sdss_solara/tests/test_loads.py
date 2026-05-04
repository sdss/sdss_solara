import pytest

from sdss_solara.pages.jdaviz_embed import get_specformat, make_label, sort_filemap


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
    """test we can get the correct specutils format"""
    assert get_specformat(filepath) == expected


@pytest.mark.parametrize(
    "filepath, expected",
    [
        (
            "spectro/boss/redux/v6_2_1/spectra/daily/lite/100XXX/100129/59805/spec-100129-59805-27021597855027663.fits",
            "spec-daily-100129-59805-27021597855027663",
        ),
        (
            "spectro/boss/redux/v6_2_1/spectra/epoch/lite/112XXX/112360/60287/spec-112360-60287-27021603143302004.fits",
            "spec-epoch-112360-60287-27021603143302004",
        ),
        (
            "spectro/boss/redux/v6_2_1/spectra/allepoch/lite/allepoch/allepoch_apo/59373/spec-allepoch_apo-59373-4351657527.fits",
            "spec-allepoch_apo-59373-4351657527",
        ),
        (
            "dr17/sdss/spectro/redux/26/spectra/lite/2895/spec-2895-54567-0346.fits",
            "spec-lite-2895-54567-0346",
        ),
        (
            "dr17/sdss/spectro/redux/26/spectra/full/2895/spec-2895-54567-0346.fits",
            "spec-full-2895-54567-0346",
        ),
        (
            "spectro/apogee/redux/1.5/stars/apo25m/11/11410/apStar-1.5-apo25m-2M00490869+6205128.fits",
            "apStar-1.5-apo25m-2M00490869+6205128",
        ),
    ],
    ids=["daily", "epoch", "allepoch", "lite", "full", "star"],
)
def test_make_label(filepath, expected):
    """test we can make a correct label"""
    assert make_label(filepath) == expected


filemap = {
    "spec-epoch-100129-60624-63050394785558224": "/Users/brian/Work/sdss/sas/ipl-4/spectro/boss/redux/v6_2_1/spectra/epoch/lite/100XXX/100129/60624/spec-100129-60624-63050394785558224.fits",
    "mwmVisit-0.8.0-54459273": "/Users/brian/Work/sdss/sas/ipl-4/spectro/astra/spectra/visit/92/73/mwmVisit-0.8.0-54459273.fits",
    "apVisit-1.5-apo25m-16442-60595-211": "/Users/brian/Work/sdss/sas/ipl-4/spectro/apogee/redux/1.5/visit/apo25m/100129/16442/60595/apVisit-1.5-apo25m-16442-60595-211.fits",
    "apStar-1.5-apo25m-2M08003732+3644436": "/Users/brian/Work/sdss/sas/ipl-4/spectro/apogee/redux/1.5/stars/apo25m/39/39339/apStar-1.5-apo25m-2M08003732+3644436.fits",
    "spec-daily-100129-59805-27021597855027663": "/Users/brian/Work/sdss/sas/ipl-4/spectro/boss/redux/v6_2_1/spectra/daily/lite/100XXX/100129/59805/spec-100129-59805-27021597855027663.fits",
    "mwmStar-0.8.0-54459273": "/Users/brian/Work/sdss/sas/ipl-4/spectro/astra/spectra/star/92/73/mwmStar-0.8.0-54459273.fits",
}


def test_sort_filemap():
    """test we can sort the data dict"""
    new = sort_filemap(filemap)
    assert list(new.keys()) == ["mwmStar-0.8.0-54459273",
                                "spec-epoch-100129-60624-63050394785558224",
                                "spec-daily-100129-59805-27021597855027663",
                                "apStar-1.5-apo25m-2M08003732+3644436",
                                "mwmVisit-0.8.0-54459273",
                                "apVisit-1.5-apo25m-16442-60595-211",
                                ]