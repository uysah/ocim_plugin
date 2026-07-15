from ocelescope import OCEL
from ..resource import ProcessTree as OCProcessTree, LeafNode, OperationNode, Operator
from .common_data import * 
from .interaction_patterns import *
from .tau_cases import * 
from .log_splitting import *
from .cut_detection import *
from pm4py.objects.ocel.obj import OCEL as PM4PYOCEL
from .fallthrough_detection import *



# ============================================

#        Object-Centric Process Tree

# ============================================


def apply_ocim(ocel:OCEL) -> OCProcessTree:

    pm4py_ocel = PM4PYOCEL(
        events=ocel.events.df,
        objects=ocel.objects.df,
        relations=ocel.e2o.df,
    )

    input_log = pm4py_ocel.relations

    local_data = LocalData([input_log])
    global_data = GlobalData([input_log])

    result = object_centric_inductive_miner(local_data,global_data,)

    return OCProcessTree(root=result)

def object_centric_inductive_miner(local_data, global_data,brute_force = False, noise = False):
    partition, operator = detect_tau_cases(local_data,global_data)

    if operator:
        sublogs = split_log(local_data, partition,operator,global_data)
        subtrees = [object_centric_inductive_miner(sublogs[0], global_data, brute_force, noise),
            LeafNode(activity="",related=local_data.object_types,divergent=local_data.object_types,convergent=local_data.object_types,deficient=local_data.object_types,)]
        return OperationNode(operator=operator,children=subtrees,)

    if len(local_data.alphabet) == 1:

        sizes = {ot:[log[log["ocel:type"] == ot].groupby("ocel:oid").apply(lambda frame: frame.shape[0]).max() > 1 for log in
        local_data.oc_log_list if log[log["ocel:type"] == ot].shape[0]] for ot in global_data.related[local_data.alphabet[0]] }
        loops = {ot for ot in global_data.related[local_data.alphabet[0]] if any(sizes[ot])}
        loops = {ot for ot in loops if any([ot in global_data.related[a] and ot not in global_data.divergence[a]
                            for a in local_data.alphabet])}
        if loops:
            return OperationNode(operator = Operator.LOOP,children=[LeafNode(activity=local_data.alphabet[0], related = global_data.related[local_data.alphabet[0]],
                            divergent=(global_data.divergence[local_data.alphabet[0]]),
                            convergent=global_data.convergence[local_data.alphabet[0]],
                            deficient= global_data.deficiency[local_data.alphabet[0]]),
                LeafNode(activity="",related=local_data.object_types,divergent=local_data.object_types,convergent=local_data.object_types,deficient=local_data.object_types,)])
        else:
            return LeafNode(activity=local_data.alphabet[0], related = global_data.related[local_data.alphabet[0]],
                            divergent=(global_data.divergence[local_data.alphabet[0]]),
                            convergent=global_data.convergence[local_data.alphabet[0]],
                            deficient= global_data.deficiency[local_data.alphabet[0]])

    partition, operator = find_strict_cut(local_data, global_data)

    if operator is None:
        if not brute_force:
            partition, operator = detect_fallthrough_fitness_polynomial(local_data,global_data)
        else:
            partition, operator = detect_fallthrough_fitness_brute_force(local_data,global_data)

    sublogs = split_log(local_data,partition,operator,global_data)
    subtrees = [object_centric_inductive_miner(split_local_data, global_data,brute_force,noise) for split_local_data in sublogs]

    return OperationNode(operator=operator, children=subtrees)


# ============================================

#          Object-Centric Petri Net

# ============================================

from .ocpn_conversion import *
from pm4py.objects.conversion.process_tree import converter as pt_converter
from ocelescope.resource.default.petri_net import PetriNet,Place,Transition,Arc, ArcType


def convert_ocpn(ocel: OCEL) -> PetriNet:
    ocpt = apply_ocim(ocel)
    object_types = ocpt._collect_object_types(ocpt.root)

    conv_objects = ocpt.get_convergent_object_types_excluding_tau()
    ocpn = PetriNet()

    place_map = {}
    transition_map = {}

    for ot in object_types:
        pt = project_ocpt(ocpt.root, ot, ocel)
        net, im, fm = pt_converter.apply(pt)
        place_ids = {id(p) for p in net.places}

        #add places

        for place in net.places:
            oc_place = Place(
                name=f"{ot}_{place.name}",
                object_type=ot,
            )
            ocpn.add_place(oc_place)
            place_map[(ot, id(place))] = oc_place

        #add transitions

        for transition in net.transitions:
            if transition.label is None:
                key = ("tau", transition.name)
            else:
                key = transition.label

            if key not in transition_map:
                oc_transition = Transition(
                    name=str(key),
                    label=transition.label,
                )
                ocpn.add_transition(oc_transition)
                transition_map[key] = oc_transition

        #add arcs

        for arc in net.arcs:
            if id(arc.source) in place_ids:
                source = place_map[(ot, id(arc.source))]
            else:
                key = ("tau", arc.source.name) if arc.source.label is None else arc.source.label
                source = transition_map[key]

            if id(arc.target) in place_ids:
                target = place_map[(ot, id(arc.target))]
            else:
                key = ("tau", arc.target.name) if arc.target.label is None else arc.target.label
                target = transition_map[key]

            #get activity in preset or postset
            activity = None
            if id(arc.source) not in place_ids:
                activity = arc.source.label
            elif id(arc.target) not in place_ids:
                activity = arc.target.label

            is_variable = (activity is not None and (ot, activity) in conv_objects)
            if is_variable:
                oc_arc = Arc(source=source.name, target=target.name, type=ArcType.VARIABLE)
            else:
                oc_arc = Arc(source=source.name, target=target.name)

            ocpn.add_arc(oc_arc)
        #initial and final marking

        for place, tokens in im.items():
            oc_place = place_map[(ot, id(place))]
            ocpn.initial_marking[oc_place.name] = tokens

        for place, tokens in fm.items():
            oc_place = place_map[(ot, id(place))]
            ocpn.final_marking[oc_place.name] = tokens 

    return ocpn