from ocelescope import OCEL
import pm4py
from pm4py.objects.ocel.obj import OCEL as PM4PYOCEL


def detect_tau_cases(activities, relation,clos,object_types,dfg,divergence):
    for a in activities:
        for b in activities:
            for ot in get_non_divergent_types(a,b,activities,relation,divergence):
                if not clos[ot].get((a,b),0) or not clos[ot].get((b,a),0):
                    return None, None
    for ot in object_types:
        for a in activities:
            for b in activities:
                if dfg[ot][2].get(a,0) and dfg[ot][1].get(b,0) and not dfg[ot][0].get((a,b),0):
                    return None, None
    
    if not any(ot in relation[a] and ot not in divergence[a]
           for a in activities for ot in object_types):
        return None,None

    return [activities, []], "loop"

def get_non_divergent_types(a, b, context_activities, relation,divergence):
    return [ot for ot in relation[a] & relation[b] if
        not all(ot not in relation[c] or ot in divergence[c] for c in context_activities)]