from typing import Annotated

from ocelescope import (
    OCEL,
    OCELAnnotation,
    Plugin,
    PluginInput,
    Resource,
    plugin_method,
)


from .resource import ProcessTree
from .util import discover_ocim,build_test_process_tree



class OCIM(Plugin):
    label = "Object-Centric Inductive Miner"
    description = "Discover Object-Centric Process Models with Inductive Miner"
    version = "1.0"

    @plugin_method(label="Object-Centric Process Tree", description="Discover Object-Centric Process Tree with Inductive Miner")
    def example(
        self,
        ocel: Annotated[OCEL, OCELAnnotation(label="Event Log")],
    ) -> ProcessTree:
        return build_test_process_tree(ocel)
