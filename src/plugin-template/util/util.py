from ocelescope import OCEL
from ..resource import ProcessTree, LeafNode, OperationNode, Operator
from collections import defaultdict, Counter
from typing import List
from itertools import combinations
from .common_data import * 
from .interaction_patterns import *
from .tau_cases import * 
from .log_splitting import *
from .cut_detection import *
import pm4py
from pm4py.objects.ocel.obj import OCEL as PM4PYOCEL
from .fallthrough_detection import *


def apply_ocim(ocel:OCEL) -> ProcessTree:

    pm4py_ocel = PM4PYOCEL(
        events=ocel.events.df,
        objects=ocel.objects.df,
        relations=ocel.e2o.df,
    )

    input_log = pm4py_ocel.relations

    local_data = LocalData([input_log])
    global_data = GlobalData([input_log])

    result = object_centric_inductive_miner(local_data,global_data,)

    return ProcessTree(root=result)

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



def build_test_process_tree(ocel: OCEL) -> ProcessTree:

    root = OperationNode(
        operator=Operator.SEQUENCE,
        children=[

            LeafNode(
                activity="A",
                related={"order"},
                divergent=set(),
                convergent={"order"},
                deficient=set(),
            ),

            OperationNode(
                operator=Operator.XOR,
                children=[

                    LeafNode(
                        activity="B",
                        related={"order", "item"},
                        divergent={"item"},
                        convergent={"order"},
                        deficient=set(),
                    ),

                    LeafNode(
                        activity="C",
                        related={"order", "item"},
                        divergent={"item"},
                        convergent={"order"},
                        deficient=set(),
                    ),
                ],
            ),

            OperationNode(
                operator=Operator.PARALLEL,
                children=[

                    LeafNode(
                        activity="D",
                        related={"order", "employee"},
                        divergent={"employee"},
                        convergent={"order"},
                        deficient=set(),
                    ),

                    LeafNode(
                        activity="E",
                        related={"order", "employee"},
                        divergent={"employee"},
                        convergent={"order"},
                        deficient=set(),
                    ),
                ],
            ),

            LeafNode(
                activity="F",
                related={"order"},
                divergent=set(),
                convergent={"order"},
                deficient=set(),
            ),
        ],
    )

    return ProcessTree(root=root)



