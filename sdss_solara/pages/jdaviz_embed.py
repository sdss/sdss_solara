import fnmatch
import os
import pathlib

import dotenv
import nbformat as nbf
import numpy as np
import requests
import solara

from sdss_access import Access
from sdss_solara.components.message import Message, event_handler, set_initial_theme


def get_url():
    """ get the valis api url """
    url = os.getenv("VALIS_API_URL")
    if url:
        return url

    env = os.getenv("VALIS_ENV") or os.getenv("SOLARA_ENV") or ''
    name = '.env.dev' if env.startswith("dev") else '.env.test' if env.startswith('test') else '.env.prod'
    dotenv.load_dotenv(dotenv.find_dotenv(name))
    return os.getenv("VALIS_API_URL")


api_url = get_url()


def get_config():
    """ create custom jdaviz configuration """
    from jdaviz.core.config import get_configuration

    # get the default specviz config
    config = get_configuration('specviz')

    # set custom settings for embedding
    config['settings']['viewer_spec'] = config['settings'].get('configuration', 'default')
    config['settings']['server_is_remote'] = True
    config['toolbar'].remove('g-data-tools') if config['toolbar'].count('g-data-tools') else None

    return config


def get_specformat(filepath: str) -> str:
    """ Get the Spectrum1D format based on the filepath """
    if fnmatch.fnmatch(filepath, '*apogee/*/dr17/visit*'):
        return 'APOGEE apVisit'
    elif fnmatch.fnmatch(filepath, '*apogee/*/dr17/stars*'):
        return 'APOGEE apStar'
    elif fnmatch.fnmatch(filepath, '*dr17/eboss/spectro*'):
        return 'SDSS-III/IV spec'
    elif fnmatch.fnmatch(filepath, '*astra/*/mwmStar*'):
        # loads all extensions
        return 'SDSS-V mwm'
    elif fnmatch.fnmatch(filepath, '*astra/*/mwmVisit*'):
        # loads all extensions
        return 'SDSS-V mwm'
    else:
        return None


def sort_filemap(data: dict) -> dict:
    """ Sort the filemap by file preference """
    prefs = ['mwmStar', 'spec', 'apStar']
    prior = dict(zip(prefs, range(len(prefs))))

    def get_prior(x):
        for i in prefs:
            if x.startswith(i):
                return prior[i]
        return float('inf')

    skeys = sorted(data.keys(), key=get_prior)
    return {key: data[key] for key in skeys}


# reactive variables
spec = solara.reactive(None)
selected = solara.reactive([])
filemap = solara.reactive({})
params = solara.reactive({})


@solara.component
def DataSelect():
    """ component for a dropdown select menu """
    all_files = solara.use_reactive([])

    sdssid = params.value.get('sdssid', '')
    release = params.value.get('release', 'IPL3')
    qp_files = params.value.get('files', '')

    def make_request():
        """ make a valis request to get the spectral data files """
        if not sdssid:
            return []

        resp = requests.get(api_url + f'/target/pipelines/{sdssid}',
                            json={'release': release})
        if not resp.ok:
            return []

        vals = {pathlib.Path(i).name: i for i in resp.json()['files'].values()}
        filemap.value = sort_filemap(vals) if not set(vals) == {''} else {}
        return list(filemap.value.keys())

    def get_files():
        """ get the spectral data files """
        if filemap.value:
            all_files.value = list(filemap.value.keys())
            selected.value = [all_files.value[0]] if all_files.value else []
            return

        if sdssid and not qp_files:
            res = make_request()
            print('finished req', res)
            all_files.value = res or []
            selected.value = [all_files.value[0]] if all_files.value else []
        elif sdssid and qp_files:
            print('getting files', sdssid, qp_files)
            filemap.value = sort_filemap({pathlib.Path(i).name: i for i in qp_files.split(',')})
            all_files.value = list(filemap.value.keys())
            selected.value = [all_files.value[0]] if all_files.value else []

    if not all_files.value:
        get_files()

    solara.SelectMultiple("Select Data Files", selected, all_files.value, dense=True)


@solara.component
def DataLoader():
    """ component for data loading button """
    def load():
        for f in selected.value:
            label = f'{pathlib.Path(f).stem}'
            speclabels = set(i.split(' ', 1)[0] for i in spec.value.app.data_collection.labels)
            lal = True if 'mwmVisit' in label or 'apVisit' in label else False
            if label not in speclabels:
                spec.value.load_data(filemap.value[f], format=get_specformat(filemap.value[f]), load_as_list=lal)

    solara.Button('Load Data', color='primary', on_click=load)


def get_urls(files, release):
    access = Access(release=release)
    access.remote()
    sasdir = 'sas' if access.access_mode == 'curl' else ''
    return [access.url('', full=f, sasdir=sasdir) for f in files if f]


def get_nb(files, release, sdssid):

    # get the urls to render
    urls = get_urls(files, release)

    nb = nbf.v4.new_notebook()

    # intro cell
    text = f"""\
# Jdaviz notebook
This is an auto-generated notebook to access SDSS data, for target {sdssid}, using the [jdaviz](https://jdaviz.readthedocs.io/en/latest/) Python package.  It is recommended to run this in a Python virtual environment, e.g. **pyenv** or **miniconda**.  If you don't have the packages already installed, please run:
```
pip install -U sdss_access
pip install -U jdaviz
```

This notebook attempts to download SDSS data using [sdss_access](https://sdss-access.readthedocs.io/en/latest).  If the data are not public, you will need to setup your [SDSS authentication](https://sdss-access.readthedocs.io/en/latest/auth.html).  If you should have access but do not have credentials, please see the [SDSS Data Access Wiki](https://wiki.sdss.org/display/DATA/Get+Started+with+SDSS+Data), or contact the [SDSS Helpdesk](mailto:helpdesk@sdss.org).
    """

    # code import cell
    code = """\
import os
from sdss_access import Access
from jdaviz import Specviz
    """

    # code cell for data access
    code2 = f"""\
# set up sdss-access and download files
access = Access(release="{release}")
access.remote()

# set the local filepaths
urls = {urls}
for url in urls:
    access.add_file(url, input_type='url')

# set the files in the stream; get the filepaths to load
access.set_stream()
files = access.get_paths()

# download the files
access.commit()
    """

    # code cell for loading data into Jdaviz
    code3 = """\
# load the data into Specviz
spec = Specviz()
for file in files:
    spec.load_data(file)

# display Specviz
spec.show()
    """

    # add the cells
    nb['cells'] = [nbf.v4.new_markdown_cell(text),
                   nbf.v4.new_code_cell(code),
                   nbf.v4.new_code_cell(code2),
                   nbf.v4.new_code_cell(code3),
                   ]

    return nbf.writes(nb)


@solara.component
def Notebook():
    """ component for download a Jupyter notebook """
    files = list(filemap.value.values())
    sdssid = params.value.get('sdssid')
    nbobj = get_nb(files, params.value.get('release'), sdssid)
    with solara.FileDownload(nbobj, f"sdss_jdaviz_notebook_{sdssid}.ipynb", mime_type="application/x-ipynb+json"):
        with solara.Tooltip("Download a Jdaviz Jupyter notebook for these data"):
            solara.Button(label='Download Jupyter notebook', color='primary')


def smart_resize(specviz):
    """ placeholder function to resize init data """
    # get spectra
    ss = specviz.get_spectra()
    key = next(iter(ss))
    spec = ss[key]

    # skip smart resize if the outlier threshold is low
    threshold = np.abs(np.nanmax(spec.flux)/np.nanmedian(spec.flux)).value
    if threshold < 100:
        return

    # adjust plot y limits to 99th percentile
    scale = 1.5
    plot_options = specviz.plugins['Plot Options']
    plot_options.y_min.value = np.nanpercentile(spec.flux, 1).value * scale
    plot_options.y_max.value = np.nanpercentile(spec.flux, 99).value * scale


@solara.component
def Jdaviz():
    """ component for displaying Jdaviz """
    from IPython.display import display
    import jdaviz
    from jdaviz import Specviz, Application
    import ipysplitpanes
    import ipygoldenlayout
    import ipyvue
    import os
    from jdaviz.app import custom_components

    ipysplitpanes.SplitPanes()
    ipygoldenlayout.GoldenLayout()
    for name, path in custom_components.items():
        ipyvue.register_component_from_file(None, name, os.path.join(os.path.dirname(jdaviz.__file__), path))

    ipyvue.register_component_from_file('g-viewer-tab', "container.vue", jdaviz.__file__)

    css = """
    main.v-content.solara-content-main {
        padding: 0px !important;
    }

    .widget-output {
        margin: 0;
    }

    .jdaviz {
        height: 100vh !important;
    }

    .v-content.jdaviz__content--not-in-notebook {
        height: 100vh !important;
        max-height: 100vh
    }
    """

    solara.Style(css)
    with solara.Column():

        config = get_config()
        app = Application(configuration=config)
        style_path = pathlib.Path(__file__).parent / 'custom_jdaviz.vue'
        app._add_style(str(style_path))
        spec.value = Specviz(app)

        if filemap.value:
            label = list(filemap.value.keys())[0]
            val = filemap.value[label]
            lal = True if 'mwmVisit' in label or 'apVisit' in label else False
            spec.value.load_data(val, format=get_specformat(val), load_as_list=lal)
            smart_resize(spec.value)

        display(spec.value.app)


@solara.component
def Page():
    """ main page component """
    router = solara.use_router()
    params.value = dict(i.split('=') for i in router.search.split('&')) if router.search else {}

    print(params.value)

    # set initial theme
    set_initial_theme()

    with solara.Column():
        solara.Title("Spectral Display")
        Message(event_update=event_handler)

        with solara.Columns([1, 0, 0], style='margin: 0 5px'):
            DataSelect()
            DataLoader()
            Notebook()

        Jdaviz()

Page()