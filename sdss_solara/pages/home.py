import solara

from sdss_solara.pages.jdaviz_embed import Page as Embed
from sdss_explorer.dashboard import Page as Dashboard, Layout as DashLayout
from sdss_solara.components.message import Message, event_handler, set_initial_theme


@solara.component
def Layout(children=[]):
    # there will only be 1 child, which is the Page()
    return children[0]


@solara.component
def Home():
    solara.Markdown("SDSS Solara Home")
    Message(event_update=event_handler)


@solara.component
def NewDash():
    """hack to insert the iframe message event handler into the dashboard"""
    set_initial_theme()
    with solara.Column():
        Message(event_update=event_handler)
        Dashboard()


routes = [
    solara.Route(path="/", component=Home, label="Home", layout=Layout),
    solara.Route(path="embed", component=Embed, label="Embed"),
    solara.Route(
        path="dashboard",
        layout=DashLayout,
        children=[
            solara.Route(path="/", component=NewDash, label="Dashboard")
        ],
    ),
]

