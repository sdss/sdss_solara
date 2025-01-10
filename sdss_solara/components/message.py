
import solara


@solara.component_vue('message.vue')
def Message(
    event_update: solara.Callable[[dict], None] = None):
    """ iframe post message component """
    pass


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


def set_initial_theme():
    router = solara.use_router()
    params = dict(i.split('=', 1) for i in router.search.split('&')) if router.search else {}
    theme = params.get('theme')
    check_theme(theme)