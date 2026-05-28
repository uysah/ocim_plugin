from ocelescope import OCEL
import pm4py
from pm4py.objects.ocel.obj import OCEL as PM4PYOCEL
import networkx



def get_cummulative_directly_follows_relation(ocel:OCEL):
    result = {}
    activities = list(ocel.e2o.df["ocel:activity"].unique())
    object_types = list(ocel.e2o.df["ocel:type"].unique())

    pm4py_ocel = PM4PYOCEL(
        events=ocel.events.df,
        objects=ocel.objects.df,
        relations=ocel.e2o.df,
    )

    for ot in object_types:
        sub_frames = pm4py_ocel.relations[pm4py_ocel.relations["ocel:type"] == ot]
        dfg = pm4py.discover_directly_follows_graph(sub_frames, "ocel:activity", "ocel:timestamp", "ocel:oid")
        dfg_count = {(a, b): dfg[0].get((a, b), 0) for a in activities for b in activities}
        start = {a: sum(dfg_count.get((a, b), 0) for b in activities) for a in activities}
        end = {a: sum(dfg_count.get((b, a), 0) for b in activities) for a in activities}
        result[ot] = dfg, start, end

    return result


def get_transitive_closure_follows_relation(ocel:OCEL):
    result = {}
    activities = list(ocel.e2o.df["ocel:activity"].unique())
    object_types = list(ocel.e2o.df["ocel:type"].unique())

    pm4py_ocel = PM4PYOCEL(
        events=ocel.events.df,
        objects=ocel.objects.df,
        relations=ocel.e2o.df,
    )

    for ot in object_types:
        sub_frames = pm4py_ocel.relations[pm4py_ocel.relations["ocel:type"] == ot]
        dfg = pm4py.discover_directly_follows_graph(sub_frames, "ocel:activity", "ocel:timestamp", "ocel:oid")
        dfg_count = {(a, b): dfg[0].get((a, b), 0) for a in activities for b in activities}
        edges = [(activities.index(k[0]), activities.index(k[1])) for k, v in dfg_count.items() if v]
        closure_edges = networkx.transitive_closure( networkx.DiGraph(edges), reflexive=False).edges()
        result[ot] = {(activities[edge[0]],activities[edge[1]]): 1 for edge in closure_edges}

    return result