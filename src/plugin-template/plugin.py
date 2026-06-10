from typing import Annotated


from ocelescope import (
    OCEL,
    OCELAnnotation,
    Plugin,
    PluginInput,
    plugin_method,
)
from ocelescope.discovery.decorator import discovery_method

from ocelescope.resource.default.petri_net import PetriNet
from .resource import ProcessTree
from .util.util import build_test_process_tree, apply_ocim, convert_ocpn




class OCIM(Plugin):
    label = "Object-Centric Inductive Miner"
    description = "Discover Object-Centric Process Models with Inductive Miner"
    version = "1.0"

    @plugin_method(label="Object-Centric Process Tree", description="Discover Object-Centric Process Tree with Inductive Miner")
    def discover_ocpt(
        self,
        ocel: Annotated[OCEL, OCELAnnotation(label="Event Log")],
    ) -> ProcessTree:
        return apply_ocim(ocel)
    
    @plugin_method(label="Object-Centric Petri Net", description="Discover Object-Centric Petri Net with Inductive Miner")
    def discover_ocpn(
        self,
        ocel: Annotated[OCEL, OCELAnnotation(label="Event Log")],
    ) -> PetriNet:
        return convert_ocpn(ocel)
