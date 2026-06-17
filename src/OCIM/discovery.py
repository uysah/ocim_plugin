from ocelescope.discovery.decorator import discovery_method
from ocelescope.resource.default.petri_net import PetriNet

from ocelescope import OCEL


from .resource import ProcessTree
from .util.util import apply_ocim, convert_ocpn

@discovery_method(
    name="Object-Centric Inductive Miner",
    description="Discover Object-Centric Process Tree with Inductive Miner",
)
def discover_ocpt(
    ocel:OCEL,
) -> ProcessTree:
    return apply_ocim(ocel)


@discovery_method(
    name="Object-Centric Inductive Miner",
    description="Discover Object-Centric Petri Net with Inductive Miner",
)
def discover_ocpn(
    ocel: OCEL,
) -> PetriNet:
    return convert_ocpn(ocel)
