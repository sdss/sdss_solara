
import solara

from sdss_solara.pages.jdaviz_embed import Page as Embed
from sdss_explorer.pages import Page as Dashboard, Layout as DashLayout

@solara.component
def Layout(children=[]):
    # there will only be 1 child, which is the Page()
    return children[0]


@solara.component
def Home():
    solara.Markdown("SDSS Solara Home")


routes = [
    solara.Route(path="/", component=Home, label="Home", layout=Layout),
    solara.Route(path="embed", component=Embed, label="Embed"),
    solara.Route(path="dashboard", layout=DashLayout, children=[
        solara.Route(path="/", component=Dashboard, label="Dashboard")
    ]),
]