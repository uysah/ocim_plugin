from typing import Annotated
from ocelescope import (
    OCEL,
    OCELAnnotation,
    Plugin,
    plugin_method,
)
from ocelescope.resource.default.petri_net import PetriNet
from .resource import ProcessTree
from .util.util import apply_ocim, convert_ocpn




class OCIM(Plugin):
    label = "Object-Centric Inductive Miner Plugin"
    description = "Discover Object-Centric Process Models with Inductive Miner"
    version = "1.0.1"

    @plugin_method(label="Object-Centric Process Tree", description="Discover Object-Centric Process Tree with Inductive Miner")
    def discover_ocpt(
        self,
        ocel: Annotated[OCEL,OCELAnnotation(label='Event Log')],
    ) -> ProcessTree:
        return apply_ocim(ocel)
    
    @plugin_method(label="Object-Centric Petri Net", description="Discover Object-Centric Petri Net with Inductive Miner")
    def discover_ocpn(
        self,
        ocel: Annotated[OCEL,OCELAnnotation(label='Event Log')],
    ) -> PetriNet:
        return convert_ocpn(ocel)
