from ..util.common_data import *
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
from ..resource import *


def split_log(local_data, partition, operator, global_data):

    if operator in [Operator.SEQUENCE,Operator.PARALLEL]:
        result = [LocalData([log[log["ocel:activity"].isin(part)] for log in local_data.oc_log_list], expected_objects=local_data.expected_objects) for part in partition if part]
        return result
    if operator == Operator.XOR:
        result = [LocalData([log[log["ocel:activity"].isin(part)] for log in local_data.oc_log_list],
            expected_objects=list(set(sum([list(log[log["ocel:activity"].isin(part)]["ocel:oid"].unique())
                for log in local_data.oc_log_list],[])))) for part in partition if part]
        return result

    result = [[] for part in partition]
    for log in local_data.oc_log_list:
        look_up_activity = log.drop_duplicates("ocel:eid", inplace =False).set_index("ocel:eid", inplace = False)
        look_up_type = log.drop_duplicates("ocel:oid", inplace =False).set_index("ocel:oid", inplace = False)
        edges = log.groupby("ocel:oid").apply(lambda frame:[edge for edge in zip((["start"] + frame["ocel:eid"].to_list()),(list(frame["ocel:eid"])+ ["end"]))
            if edge[0] != "start" and edge[1] != "end" and
                look_up_activity.loc[edge[0]]["ocel:activity"] in partition[0] == look_up_activity.loc[edge[1]][ "ocel:activity"] in partition[0] and
                not (local_data.dfgs[look_up_type.loc[frame.name]["ocel:type"]][2].get(look_up_activity.loc[edge[0]]["ocel:activity"],0) and
                local_data.dfgs[look_up_type.loc[frame.name]["ocel:type"]][1].get(look_up_activity.loc[edge[1]]["ocel:activity"],0)) and
                not look_up_type.loc[frame.name]["ocel:type"] in get_divergent_types(look_up_activity.loc[edge[0]]["ocel:activity"],
                                                    look_up_activity.loc[edge[1]]["ocel:activity"],local_data.alphabet,global_data)])

        edges = set(sum([value for value in edges.values], []))
        matrix = [[1 if (eid1,eid2) in edges or (eid2,eid1) in edges else 0 for eid1 in look_up_activity.index] for eid2 in look_up_activity.index]
        n_components, labels = connected_components(csgraph=csr_matrix(matrix), directed=False, return_labels=True)
        seperation = [[look_up_activity.index[i] for i in range(0,len(look_up_activity.index)) if labels[i] == n] for n in range(0,n_components)]

        sublogs = [log[log["ocel:eid"].isin(part)] for part in seperation]
        for sublog in sublogs:
            for i in range(0,len(partition)):
                if any (a in sublog["ocel:activity"].unique() for a in partition[i]):
                    result[i].append(sublog)

        return [LocalData(oc_log_list, expected_objects=local_data.expected_objects) for oc_log_list in result]