import os
import pathlib

import dotenv
import nbformat as nbf
import requests
import solara

from sdss_access import Access


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


# temp local files
data = {'spec-015078-59187-4291570940.fits': '/Users/Brian/Work/sdss/sas/sdsswork/bhm/boss/spectro/redux/v6_0_6/spectra/lite/017057/59631/spec-017057-59631-27021598108289694.fits',
        'spec-101077-59845-27021603187129892.fits': '/Users/Brian/Work/sdss/sas/ipl-3/spectro/boss/redux/v6_1_1/spectra/lite/101077/59845/spec-101077-59845-27021603187129892.fits',
        'spec-017057-59629-27021598108289694.fits': '/Users/Brian/Work/sdss/sas/ipl-3/spectro/boss/redux/v6_1_1/spectra/lite/017057/59629/spec-017057-59629-27021598108289694.fits',
        'spec-017057-59611-27021598108289694.fits': '/Users/Brian/Work/sdss/sas/ipl-3/spectro/boss/redux/v6_1_1/spectra/lite/017057/59611/spec-017057-59611-27021598108289694.fits'
        }

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
        filemap.value = vals if not set(vals) == {''} else {}
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
            filemap.value = {pathlib.Path(i).name: i for i in qp_files.split(',')}
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
            label = f'{pathlib.Path(f).stem} 0'
            if label not in spec.value.app.data_collection.labels:
                spec.value.load_data(data[f], format='SDSS-V spec multi')

    solara.Button('Load Data', color='primary', on_click=load)


def get_urls(files, release):
    access = Access(release=release)
    access.remote()
    sasdir = 'sas' if access.access_mode == 'curl' else ''
    return [access.url('', full=f, sasdir=sasdir) for f in files]


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
pip install specutils@git+https://github.com/rileythai/specutils-sdss-loaders.git#egg=sdss-v-loaders
```
Note: this notebook currently requires a custom fork of the `specutils` package.  This should be temporary and included in a new package release soon.  This notebook requires `sdss_access > 3.0.4`, `jdaviz >= 3.8`, and `specutils > 1.12`.

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
    spec.load_data(file, format='SDSS-V spec multi')

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

    .jdaviz {
        height: 50vh !important;
    }

    """

    solara.Style(css)
    with solara.Column():

        config = get_config()
        app = Application(configuration=config)
        spec.value = Specviz(app)

        if filemap.value:
            spec.value.load_data(data[list(filemap.value.keys())[0]], format='SDSS-V spec multi')

        display(spec.value.app)


@solara.component
def Page():
    """ main page component """
    router = solara.use_router()
    params.value = dict(i.split('=') for i in router.search.split('&')) if router.search else {}

    print(params.value)

    with solara.Column():
        solara.Title("Spectral Display")

        with solara.Columns([1, 0, 0], style='margin: 0 5px'):
            DataSelect()
            DataLoader()
            Notebook()

        Jdaviz()
