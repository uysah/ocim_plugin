import networkx
from ..util.auxillary_methods import *
import pm4py



def get_transitive_closure_partition_relations(local_data, global_data, partition):
    partition_relation = get_partition_follows_relations(local_data, global_data, partition)
    return networkx.transitive_closure(networkx.DiGraph(partition_relation), reflexive=False).edges()



def get_partition_follows_relations(local_data, global_data, partition):
    return [(i,j) for i in range(len(partition))
            for j in range(len(partition)) if any([local_data.clos[ot].get((a,b),0) for a in partition[i] #changed from dfg to clos (bug?)
        for b in partition[j] for ot in get_non_divergent_types(a,b,partition[i]+partition[j],global_data)]) and i != j]



def get_transitive_closure_follows_relation(oc_log_list):

    result = {}
    object_types = set(sum([list(log["ocel:type"].unique()) for log in oc_log_list],[]))
    activities = list(set(sum([list(log["ocel:activity"].unique()) for log in oc_log_list],[])))

    for ot in object_types:
        sub_frames = [log[log["ocel:type"] == ot] for log in oc_log_list]
        dfgs = [pm4py.discover_directly_follows_graph(sub_frame, "ocel:activity", "ocel:timestamp", "ocel:oid") for sub_frame in sub_frames]
        dfg = {(a,b):sum([graph[0].get((a,b),0) for graph in dfgs]) for a in activities for b in activities}

        edges =[(activities.index(key[0]), activities.index(key[1])) for key, value in dfg.items() if value]
        closure_edges = networkx.transitive_closure( networkx.DiGraph(edges), reflexive=False).edges()
        result[ot] = {(activities[edge[0]],activities[edge[1]]): 1 for edge in closure_edges}

    return result


def get_cummulative_directly_follows_relation(oc_log_list):

    result = {}
    object_types = set(sum([list(log["ocel:type"].unique()) for log in oc_log_list],[]))
    activities = set(sum([list(log["ocel:activity"].unique()) for log in oc_log_list],[]))

    for ot in object_types:
        sub_frames = [log[log["ocel:type"] == ot] for log in oc_log_list]
        dfgs = [pm4py.discover_directly_follows_graph(sub_frame, "ocel:activity", "ocel:timestamp", "ocel:oid") for sub_frame in sub_frames]
        dfg = {(a,b):sum([graph[0].get((a,b),0) for graph in dfgs]) for a in activities for b in activities}
        start = {a:sum([graph[1].get(a,0) for graph in dfgs]) for a in activities}
        end = {a:sum([graph[2].get(a,0) for graph in dfgs]) for a in activities}
        result[ot] = dfg, start, end

    return result

def get_graph_structures(relations, div):

    object_type = relations["ocel:type"].unique()
    directly_follows_graph, divergence_free_graph, eventually_follows_graph = {}, {}, {}
    for ot in object_type:
        sub_log = relations[relations["ocel:type"] == ot]
        dfg = pm4py.discover_directly_follows_graph(sub_log,"ocel:activity","ocel:timestamp","ocel:oid")
        efg = pm4py.discover_eventually_follows_graph(sub_log,"ocel:activity","ocel:timestamp","ocel:oid")
        directly_follows_graph[ot] = dfg
        eventually_follows_graph[ot] = efg
        graph, start, end = dfg
        graph = {key:value for key,value in graph.items() if ot not in div[key[0]] or ot not in div[key[1]]}
        start = {key:value for key,value in start.items() if ot not in div[key]}
        end = {key:value for key,value in end.items() if ot not in div[key]}
        divergence_free_graph[ot] = (graph, start, end)

    alphabet = relations["ocel:activity"].unique()

    total_graph = {(a,b):sum([divergence_free_graph[ot][0].get((a,b),0) for ot in object_type]) for a in alphabet for b in alphabet}
    total_graph = {key:value for key,value in total_graph.items() if value}
    return directly_follows_graph, divergence_free_graph, eventually_follows_graph, total_graph
