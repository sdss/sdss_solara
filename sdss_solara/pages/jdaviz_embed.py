import fnmatch
import os
import pathlib
import urllib

import dotenv
import numpy as np
import requests
import solara
from jdaviz import Specviz
from jdaviz.app import Application
from sdss_access import Access
from specutils import Spectrum, SpectrumList
from ipypopout import PopoutButton

from sdss_solara.components.common import create_shared_widgets, css
from sdss_solara.components.message import (
    Message,
    event_handler,
    new_files,
    outmsg,
    set_initial_theme,
)


def local_check():
    """Check localality"""
    local = False
    if solara.lab.headers.value:
        hosts = solara.lab.headers.value.get("host")
        hosts = hosts[0] if hosts else ""
        local = "localhost" in hosts

    return local and params.value.get("test")


def load_test_data(release: str):
    """Load test data from the SAS"""

    if "IPL" in release.upper() and "-" not in release:
        release = release.upper().replace("IPL", "IPL-")
    sas = os.getenv("SAS_BASE_DIR")
    files = (pathlib.Path(sas) / release.lower()).rglob("*.fits")
    return ",".join((i.as_posix() for i in files))


def get_url():
    """get the valis api url"""
    url = os.getenv("VALIS_API_URL")
    if url:
        return url

    env = os.getenv("VALIS_ENV") or os.getenv("SOLARA_ENV") or "development"
    name = (
        ".env.dev"
        if env.startswith("dev")
        else ".env.test"
        if env.startswith("test")
        else ".env.prod"
    )
    dotenv.load_dotenv(dotenv.find_dotenv(name))
    return os.getenv("VALIS_API_URL") or "http://localhost:8000"


api_url = get_url()


def get_config():
    """create custom jdaviz configuration"""
    from jdaviz.core.config import get_configuration

    # get the default specviz config
    config = get_configuration("specviz")

    # set custom settings for embedding
    config["settings"]["viewer_spec"] = config["settings"].get(
        "configuration", "default"
    )
    config["settings"]["server_is_remote"] = True
    config["settings"]["remote_enable_importers"] = True
    config["toolbar"].remove("g-data-tools") if config["toolbar"].count(
        "g-data-tools"
    ) else None

    return config


def get_specformat(filepath: str) -> str:
    """Get the Spectrum1D format based on the filepath"""
    if fnmatch.fnmatch(filepath, "*apogee/*/dr17/visit*"):
        return "APOGEE apVisit"
    elif fnmatch.fnmatch(filepath, "*apogee/*/dr17/stars*"):
        return "APOGEE apStar"
    elif fnmatch.fnmatch(filepath, "*apogee/redux/1.*/stars*"):
        return "SDSS-V apStar"
    elif fnmatch.fnmatch(filepath, "*apogee/redux/1.*/visit*"):
        return "SDSS-V apVisit"
    elif fnmatch.fnmatch(filepath, "*dr17/eboss/spectro*"):
        return "SDSS-III/IV spec"
    elif fnmatch.fnmatch(filepath, "*dr17/sdss/spectro*"):
        return "SDSS-III/IV spec"
    elif fnmatch.fnmatch(filepath, "*boss/redux/v6*"):
        return "SDSS-V spec"
    elif fnmatch.fnmatch(filepath, "*astra/*/mwmStar*"):
        # loads all extensions
        return "SDSS-V mwm"
    elif fnmatch.fnmatch(filepath, "*astra/*/mwmVisit*"):
        # loads all extensions
        return "SDSS-V mwm"
    elif fnmatch.fnmatch(filepath, "*dr17/manga/*LOGCUBE*"):
        # loads all extensions
        return "MaNGA cube"
    elif fnmatch.fnmatch(filepath, "*dr17/manga/*LOGRSS*"):
        # loads all extensions
        return "MaNGA rss"
    else:
        return None


def sort_filemap(data: dict) -> dict:
    """Sort the filemap by file preference"""
    prefs = ["mwmStar", "spec", "apStar"]
    prior = dict(zip(prefs, range(len(prefs))))

    def get_prior(x):
        for i in prefs:
            if x.startswith(i):
                return prior[i]
        return float("inf")

    skeys = sorted(data.keys(), key=get_prior)
    return {key: data[key] for key in skeys}


# reactive variables
spec = solara.reactive(None)
selected = solara.reactive([])
all_files = solara.reactive([])
filemap = solara.reactive({})
params = solara.reactive({})


def get_spectrum(label: str):
    """Get the specutils Spectrum object"""
    lal = (
        True
        if label.startswith(("mwmVisit", "mwmStar"))
        or "apVisit" in label
        or "apStar" in label
        else False
    )
    spec_format = get_specformat(filemap.value[label])
    if lal:
        return SpectrumList.read(filemap.value[label], format=spec_format)
    return Spectrum.read(filemap.value[label], format=spec_format)


def make_label(filepath):
    """Make a data label that accounts for spec coadds"""
    stem = pathlib.Path(filepath).stem
    parts = stem.split("-", 1)
    if "spectra/daily" in filepath:
        parts.insert(1, "daily")
        return "-".join(parts)
    elif "spectra/epoch" in filepath:
        parts.insert(1, "epoch")
        return "-".join(parts)
    elif "spectra/lite" in filepath:
        parts.insert(1, "lite")
        return "-".join(parts)
    elif "spectra/full" in filepath:
        parts.insert(1, "full")
        return "-".join(parts)
    else:
        return stem


def sync_file_state():
    """Keep all_files and selected aligned with the current filemap."""
    all_files.value = list(filemap.value.keys())
    current_selected = [i for i in selected.value if i in filemap.value]
    selected.value = current_selected or ([all_files.value[0]] if all_files.value else [])


@solara.component
def DataSelect():
    """component for a dropdown select menu"""
    sdssid = params.value.get("sdssid", "")
    release = params.value.get("release", "IPL3")
    qp_files = params.value.get("files", "")
    # allowing test data
    if local_check():
        sdssid = 123456
        qp_files = load_test_data(release)

    def make_request():
        """make a valis request to get the spectral data files"""
        if not sdssid:
            return []

        resp = requests.get(
            api_url + f"/target/pipelines/{sdssid}", json={"release": release}
        )
        if not resp.ok:
            return []

        vals = {make_label(i): i for i in sum(resp.json()["files"].values(), [])}
        filemap.value = sort_filemap(vals) if not set(vals) == {""} else {}
        sync_file_state()
        return list(all_files.value)

    def get_files():
        """get the spectral data files"""
        if filemap.value:
            sync_file_state()
            return

        if sdssid and not qp_files:
            res = make_request()
            print("finished req", res)
        elif sdssid and qp_files:
            print("getting files", sdssid, qp_files)
            filemap.value = sort_filemap(
                {make_label(i): i for i in qp_files.split(",") if check_file_exists(i, release)}
            )
            sync_file_state()

    if not all_files.value:
        get_files()

    solara.SelectMultiple("Select Data Files", selected, all_files.value, dense=True)


def load_data(app: Application, filename: str, resize: bool = False):
    """Load the data into Jdaviz"""
    label = make_label(filename)
    lal = (
        True
        if label.startswith(("mwmVisit", "mwmStar"))
        or "apVisit" in label
        or "apStar" in label
        else False
    )

    if not os.path.exists(filename):
        print('File does not exist:', filename)
        return

    # 4.2.3
    app.load_data(
        filename, format=get_specformat(filename), load_as_list=lal, data_label=label
    )
    # obj = get_spectrum(label)
    # app.load_data(obj, format=get_specformat(filename), load_as_list=lal, data_label=label, sources='*')

    # resize the plot axes
    if resize:
        smart_resize(app)


@solara.component
def DataLoader():
    """component for data loading button"""

    def load():
        for f in selected.value:
            label = make_label(filemap.value[f])
            speclabels = set(
                i.split(" ", 1)[0] for i in spec.value.app.data_collection.labels
            )
            if label not in speclabels:
                load_data(spec.value, filemap.value[f])

    solara.Button("Load Data", color="primary", on_click=load)


def check_file_exists(filepath: str, release: str) -> bool:
    """ Add a file check existence """
    access = Access(release=release)
    return access.exists('', full=filepath)


def get_urls(files: list, release: str):
    """Get the access urls for the files"""
    access = Access(release=release)
    access.remote()
    sasdir = "sas" if access.access_mode == "curl" else ""
    return [access.url("", full=f, sasdir=sasdir) for f in files if f]


def smart_resize(specviz):
    """placeholder function to resize init data"""
    # get spectra
    ss = specviz.get_spectra()
    key = next(iter(ss))
    spec = ss[key]

    # skip smart resize if the outlier threshold is low
    threshold = np.abs(np.nanmax(spec.flux) / np.nanmedian(spec.flux)).value
    if threshold < 100:
        return

    # adjust plot y limits to 99th percentile
    scale = 1.5
    plot_options = specviz.plugins["Plot Options"]
    plot_options.y_min.value = np.nanpercentile(spec.flux, 1).value * scale
    plot_options.y_max.value = np.nanpercentile(spec.flux, 99).value * scale


def load_app():
    """Load the application and data"""
    config = get_config()
    app = Application(configuration=config)
    style_path = pathlib.Path(__file__).parent / "custom_jdaviz.vue"
    app._add_style(str(style_path))
    spec.value = Specviz(app)
    error = None
    if filemap.value:
        label = list(filemap.value.keys())[0]
        load_data(spec.value, filemap.value[label], resize=True)

    return app, error


def consume_new_files():
    """Consume new_files updates and clear the queue."""
    if not new_files.value:
        return

    files = new_files.value

    # make a new filemap with the new files
    release = params.value.get("release", "IPL3")
    incoming = {make_label(i): i for i in files if i and check_file_exists(i, release)}
    if not incoming:
        return

    # check if the filemap was previously empty
    empty_prior = not filemap.value

    # merge the two dictionaries
    merged = dict(filemap.value)
    merged.update(incoming)
    filemap.value = sort_filemap(merged)
    sync_file_state()

    # load the first data file if the viewer was empty before
    if empty_prior and selected.value:
        load_data(spec.value, filemap.value[selected.value[0]], resize=True)

    # reset the new files
    new_files.value = []


@solara.component
def Jdaviz():
    """component for displaying Jdaviz"""
    # prevents infinite recursion
    solara.use_memo(create_shared_widgets, [])
    app, error = solara.use_memo(load_app, [])

    children = []
    if error:
        children.append(solara.Alert(error, color="danger", dense=True))
    else:
        children.append(app)
    return solara.Column(children=children).meta(ref="jdaviz")


@solara.component
def Page():
    """main page component"""
    # extract query params
    router = solara.use_router()
    pp = urllib.parse.parse_qs(router.search)
    params.value = {k: v[0] if len(v) == 1 else v for k, v in pp.items()}

    print(params.value)

    # set the target popout model id
    target_model_id = solara.use_reactive("")

    # set initial theme
    set_initial_theme(params)

    solara.Style(css)
    with solara.Column() as control:
        solara.Title("Spectral Display")
        Message(event_update=event_handler, outgoing=outmsg.value)

        with solara.Columns([1, 0, 0], style="margin: 0 5px"):
            DataSelect()
            DataLoader()
            # Add the popout button to the toolbar
            if target_model_id.value:
                with solara.Tooltip("Pop out the spectral viewer into a new window."):
                    with solara.Column():
                        PopoutButton.element(target_model_id=target_model_id.value, window_features='popup,width=1200,height=800')

        Jdaviz()

    # refresh available files when parent sends updateFiles postMessage
    solara.use_effect(consume_new_files, [new_files.value])

    # with solara we have to use use_effect + get_widget to get the widget id
    solara.use_effect(lambda: target_model_id.set(solara.get_widget(control)._model_id), [])

Page()
