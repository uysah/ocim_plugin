import pm4py



def get_non_divergent_types(a, b, context_activities, global_data):
    return [ot for ot in global_data.related[a] & global_data.related[b] if
        not all(ot not in global_data.related[c] or ot in global_data.divergence[c] for c in context_activities)]


def get_divergent_types(a, b, context_activities, global_data):
    return [ot for ot in global_data.related[a] & global_data.related[b] if
        all(ot not in global_data.related[c] or ot in global_data.divergence[c] for c in context_activities)]


def get_projected_start(local_data, partition_part):
    filtered_frames = [log[log["ocel:activity"].isin(partition_part)] for log in local_data.oc_log_list]
    return {ot:sum([list(pm4py.get_start_activities(log[log["ocel:type"]==ot],activity_key="ocel:activity",case_id_key="ocel:oid",
        timestamp_key="ocel:timestamp").keys()) for log in filtered_frames
        if log[log["ocel:type"]==ot].shape[0]],[]) for ot in local_data.object_types}


def get_projected_end(local_data, partition_part):
    filtered_frames = [log[log["ocel:activity"].isin(partition_part)] for log in local_data.oc_log_list]
    return {ot:sum([list(pm4py.get_end_activities(log[log["ocel:type"]==ot],activity_key="ocel:activity",case_id_key="ocel:oid",
        timestamp_key="ocel:timestamp").keys()) for log in filtered_frames
        if log[log["ocel:type"]==ot].shape[0]],[]) for ot in local_data.object_types}

