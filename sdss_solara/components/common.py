import os

import ipygoldenlayout
import ipysplitpanes
import ipyvue
import jdaviz
from jdaviz.app import custom_components


def create_shared_widgets():
    """Create shared widgets

    Necessary fix to display jdaviz with solara properly
    """
    ipysplitpanes.SplitPanes()
    ipygoldenlayout.GoldenLayout()
    for name, path in custom_components.items():
        ipyvue.register_component_from_file(
            None, name, os.path.join(os.path.dirname(jdaviz.__file__), path)
        )

    ipyvue.register_component_from_file(
        "g-viewer-tab", "container.vue", jdaviz.__file__
    )


# custom css to fix jdaviz height display when embedding
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
