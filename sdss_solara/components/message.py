
import urllib

import solara

# variable for storing outgoing messages to the parent
outmsg = solara.Reactive[dict]({})
# variable for storing incoming file updates from the parent
new_files = solara.Reactive[list]([])
# variable for storing incoming apmadgics request info
apmadgics_input = solara.Reactive[dict]({})


@solara.component_vue('message.vue')
def Message(
    event_update: solara.Callable[[dict], None] | None = None,
    outgoing: dict | None = None,
    ):
    """ iframe post message component """


def check_theme(theme: str = None):
    print('check_theme', theme)
    if theme:
        solara.lab.theme.dark = theme == 'dark'
    else:
        solara.lab.theme.dark = solara.lab.theme.dark_effective



def event_handler(data: dict):
    """ postMessage event handler """

    print('event data', data)
    event_type = data.get('type')
    if event_type == 'themeChange':
        check_theme(data.get('theme'))
    elif event_type == 'updateFiles':
        new_files.value = data.get('files') or []
        outmsg.value = {'type': 'success', 'message': 'Files updated successfully'}
    elif event_type == 'loadApMadgics':
        apmadgics_input.value = {'sdssid': data.get("sdssid"),
                                 'idx': data.get("idx"),
                                 'mjd': data.get("mjd"),
                                 "plate": data.get("plate"),
                                 "star_prior": data.get("star_prior"),}
        outmsg.value = {"type": "success", "message": "ApMadgics request received"}


def set_initial_theme(params: solara.Reactive[dict] = None):
    """set the initial theme"""
    if params is None:
        params = solara.use_reactive({})
        router = solara.use_router()
        pp = urllib.parse.parse_qs(router.search)
        params.value = {k: v[0] if len(v) == 1 else v for k, v in pp.items()}

    theme = params.value.get("theme", None)
    check_theme(theme)