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
from .util.util import build_test_process_tree, apply_ocim 



class OCIM(Plugin):
    label = "Object-Centric Inductive Miner"
    description = "Discover Object-Centric Process Models with Inductive Miner"
    version = "1.0"

    @plugin_method(label="Object-Centric Process Tree", description="Discover Object-Centric Process Tree with Inductive Miner")
    def example(
        self,
        ocel: Annotated[OCEL, OCELAnnotation(label="Event Log")],
    ) -> ProcessTree:
        return apply_ocim(ocel)
