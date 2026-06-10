from pm4py.objects.process_tree.obj import ProcessTree,Operator
import pm4py
from ..resource import OperationNode,LeafNode


def project_ocpt(ocpt,object_type):

    if isinstance(ocpt,LeafNode):
        if ocpt.activity == "" or object_type not in ocpt.related:
            return ProcessTree()
        if object_type in ocpt.divergent:
            return ProcessTree(Operator.LOOP,children = [ProcessTree(),ProcessTree(label=ocpt.activity)])
        return ProcessTree(label=ocpt.activity)

    assert isinstance(ocpt,OperationNode)
    related_activities = set([a for a in ocpt.get_activities()
        if object_type in ocpt.get_type_information()[(a,"rel")] and a != ""])

    if not related_activities:
        return ProcessTree()

    if all(object_type in ocpt.get_type_information()[(a,"div")] for a in related_activities):
        return ProcessTree(operator=pm4py.objects.process_tree.obj.Operator.LOOP,
            children=[ProcessTree(),ProcessTree(operator=pm4py.objects.process_tree.obj.Operator.XOR,children=
            [ProcessTree(label=a) for a in related_activities])])

    else:
        if ocpt.operator == Operator.PARALLEL or ocpt.operator == Operator.LOOP:
            return ProcessTree(operator=ocpt.operator,children=[project_ocpt(sub,object_type) for sub in ocpt.children])

        diverging = [i for i in range(len(ocpt.children)) if ocpt.children[i].get_activities() & related_activities
            and all(object_type in ocpt.get_type_information()[(a,"div")]
                    for a in ocpt.children[i].get_activities() & related_activities)]
        non_diverging = [i for i in range(len(ocpt.children)) if ocpt.children[i].get_activities()
            & related_activities and i not in diverging]
        skipped = [i for i in range(0,len(ocpt.children)) if i not in diverging and i not in non_diverging]

        if ocpt.operator == Operator.SEQUENCE:

            children, index = [],0

            while index < len(ocpt.children):

                if index in diverging:

                    div_activities = ocpt.children[index].get_activities() & related_activities
                    while index+1 in diverging and index+1 < len(ocpt.children):
                        index += 1
                        if index not in skipped:
                            div_activities |= ocpt.children[index].get_activities() & related_activities

                    div_activities = {a for a in div_activities if a != ""}
                    div_subtree = ProcessTree(operator=pm4py.objects.process_tree.obj.Operator.LOOP,
                          children=[ProcessTree(),
                                    ProcessTree(
                                        operator=pm4py.objects.process_tree.obj.Operator.XOR,
                                        children=[ProcessTree(label=a) for a in div_activities])])
                    children.append(div_subtree)

                else:
                    children.append(project_ocpt(ocpt.children[index],object_type))
                index += 1
            return ProcessTree(operator=Operator.SEQUENCE,children=children)

        if ocpt.operator == Operator.XOR:

            div_activities = set(sum([list(ocpt.children[i].get_activities() & related_activities) for i in diverging],[]))
            div_activities = {a for a in div_activities if a != ""}
            optional = any([isinstance(sub,LeafNode) and sub.activity == "" and object_type in sub.related for sub in ocpt.children])

            if div_activities:
                div_subtree = ProcessTree(operator=pm4py.objects.process_tree.obj.Operator.LOOP,
                            children=[ProcessTree(),
                                      ProcessTree(operator=pm4py.objects.process_tree.obj.Operator.XOR, children=
                                      [ProcessTree(label=a) for a in div_activities])])

                return ProcessTree(operator=Operator.XOR,children=[div_subtree] +
                    [project_ocpt(ocpt.children[i],object_type) for i in non_diverging] + ([ProcessTree()] if optional else []))
            else:
                return ProcessTree(operator=Operator.XOR,children=
                    [project_ocpt(ocpt.children[i],object_type) for i in non_diverging] + ([ProcessTree()] if optional else []))
    
    raise RuntimeError(
    f"Unhandled operator {ocpt.operator} for object type {object_type}"
    )



def handle_deficiency(ocpt):

    if isinstance(ocpt,OperationNode):
        subresults = [handle_deficiency(sub) for sub in ocpt.children]
        return OperationNode(ocpt.operator,[sub[0] for sub in subresults]),sum([sub[1] for sub in subresults],[])
    elif ocpt.activity == "":
        return ocpt,[]
    else:
        from itertools import combinations, chain
        stable_types = ocpt.related - ocpt.deficient
        variable_types = ocpt.related & ocpt.deficient
        if variable_types:
            ot_sets =  [stable_types | {c for c in comb} for comb in chain.from_iterable(combinations(variable_types,n)
                                    for n in range(len(variable_types)+1))]

            children = [LeafNode(activity=ocpt.activity + "<|>"+str(sorted(list(ots))), related=ots, convergent=ocpt.convergent & ots,
                        deficient= set(), divergent= ocpt.divergent & ots) for ots in ot_sets]
            return OperationNode(operator=Operator.XOR,children=children), [ocpt.activity]
        else:
            return ocpt,[]