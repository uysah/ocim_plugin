import random
from ..util.fallthrough_evaluation import *
from ..util.follows_relations import *
from ..resource import *
import numpy
import networkx
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
import sys
import more_itertools as mit
from sklearn.cluster import KMeans



def detect_distance_concurrent(local_data, global_data, a, b):
    if a == b: return 0.0
    total = sum([2 for ot in global_data.related[a] & global_data.related[b]])
    correct = sum([1 if local_data.dfgs[ot][0].get((a,b),0) else 0 for ot in global_data.related[a] & global_data.related[b]])
    correct += sum([1 if local_data.dfgs[ot][0].get((b,a),0) else 0 for ot in global_data.related[a] & global_data.related[b]])
    try:
        return correct / total
    except:
        return 1


def detect_fallthrough_concurrent(local_data, global_data):

    distances = [[detect_distance_concurrent(local_data,global_data,a,b) for a in local_data.alphabet] for b in local_data.alphabet]
    kmeans = KMeans(n_clusters=2, random_state=0).fit(numpy.array(distances))
    if len(set(kmeans.labels_)) == 1:
        part_one = [local_data.alphabet[random.randint(0,len(local_data.alphabet)-1)]]
        part_two = [a for a in local_data.alphabet if a not in part_one]
    else:
        part_one = [local_data.alphabet[i] for i in range(0,len(local_data.alphabet)) if kmeans.labels_[i] == 0]
        part_two = [local_data.alphabet[i] for i in range(0,len(local_data.alphabet)) if kmeans.labels_[i] == 1]
    return evaluate_concurrent_fallthrough(local_data,global_data,part_one,part_two)[0],[part_one, part_two], Operator.PARALLEL



def detect_distance_exclusive(local_data, global_data, part_one,part_two):
    if part_one == part_two: return 0.0
    total = sum([2 for a in part_one for b in part_two for ot in get_divergent_types(a,b,part_one+part_two,global_data)])
    correct = sum([1 if local_data.dfgs[ot][0].get((a,b),0) else 0 for a in part_one for b in part_two for ot in get_divergent_types(a,b,part_one+part_two,global_data) ])
    correct += sum([1 if local_data.dfgs[ot][0].get((b,a),0) else 0 for a in part_one for b in part_two for ot in get_divergent_types(a,b,part_one+part_two,global_data)])
    return correct / total if total else 1.0


def detect_fallthrough_exclusive(local_data, global_data):

    edges = [[1 if a==b or any(local_data.dfgs[ot][0].get((a,b),0) or local_data.dfgs[ot][0].get((b,a),0)
            for ot in get_non_divergent_types(a,b,local_data.alphabet,global_data))
            else 0 for a in local_data.alphabet] for b in local_data.alphabet]
    n_components, labels = connected_components(csgraph=csr_matrix(edges), directed=False, return_labels=True)
    if n_components == 1:
        return -1, None, None
    partition = [[local_data.alphabet[i] for i in range(0,len(local_data.alphabet)) if labels[i] == n] for n in range(0,n_components)]
    distances = [[detect_distance_exclusive(local_data, global_data, p1,p2) for p1 in partition] for p2 in partition]

    kmeans = KMeans(n_clusters=2, random_state=0).fit(numpy.array(distances))
    if len(set(kmeans.labels_)) == 1:
        return -1, None,None

    else:
        part_one = sum([partition[i] for i in range(0,len(partition)) if kmeans.labels_[i] == 0],[])
        part_two = sum([partition[i] for i in range(0,len(partition)) if kmeans.labels_[i] == 1],[])

    if set(sum(partition, [])) != set(local_data.alphabet):
        return -1,None,None

    return evaluate_xor_fallthrough(local_data,global_data,part_one,part_two)[0],[part_one, part_two], Operator.XOR



def detect_fallthrough_sequence(local_data, global_data):

    edges = [[1 if a==b or any((local_data.clos[ot].get((a,b),0) and local_data.clos[ot].get((b,a),0))
            for ot in get_non_divergent_types(a,b,local_data.alphabet,global_data))
            else 0 for a in local_data.alphabet] for b in local_data.alphabet]
    n_components, labels = connected_components(csgraph=csr_matrix(edges), directed=False, return_labels=True)
    if n_components == 1:
        return -1, None, None

    partition = [[local_data.alphabet[i] for i in range(0,len(local_data.alphabet)) if labels[i] == n] for n in range(0,n_components)]
    partition_follows = get_transitive_closure_partition_relations(local_data,global_data,partition)
    edges = [[1 if a==b or edges[local_data.alphabet.index(b)][local_data.alphabet.index(a)] or any([(i,j) in partition_follows and (j,i) in partition_follows
            for i in range(0,len(partition)) for j in range(0,len(partition)) if a in partition[i] and b in partition[j]])
            else 0 for a in local_data.alphabet] for b in local_data.alphabet]
    n_components, labels = connected_components(csgraph=csr_matrix(edges), directed=False, return_labels=True)
    if n_components == 1:
        return -1, None, None

    partition = [[local_data.alphabet[i] for i in range(0,len(local_data.alphabet)) if labels[i] == n] for n in range(0,n_components)]
    partition = [partition[i] for i in networkx.topological_sort(networkx.DiGraph(get_partition_follows_relations(local_data,global_data,partition)))]
    best_score, best_partition = -1, None

    for i in range(1, len(partition)-1):
        part_one = sum([partition[j] for j in range(0,i)],[])
        part_two = sum([partition[j] for j in range(i,len(partition))],[])
        score, operator = evaluate_sequence_fallthrough(local_data,global_data,part_one,part_two)
        if score >= best_score:
            best_score = score
            best_partition = [part_one,part_two]

    if set(sum(partition, [])) != set(local_data.alphabet):
        return -1,None,None

    return best_score,best_partition, Operator.SEQUENCE


def detect_loop_pair(local_data, global_data, a, b):


    for ot in global_data.divergence[a] & global_data.divergence[b]:
        if (local_data.dfgs[ot][1].get(a,0) or local_data.dfgs[ot][2].get(a,0)) and (local_data.dfgs[ot][1].get(b,0) or local_data.dfgs[ot][2].get(b,0)):
            return True
        if (local_data.dfgs[ot][0].get((a, b), 0) and not local_data.dfgs[ot][2].get(a,0) and not local_data.dfgs[ot][1].get(b,0)
            and ot not in get_divergent_types(a, b, local_data.alphabet, global_data)):
            return True

    return False


def detect_fallthrough_loop(local_data, global_data):

    edges = [[1 if a==b or detect_loop_pair(local_data, global_data, a, b)
            else 0 for a in local_data.alphabet] for b in local_data.alphabet]
    n_components, labels = connected_components(csgraph=csr_matrix(edges), directed=False, return_labels=True)
    if n_components == 1:
        return -1, None, None

    best_partition, best_score = None, -1
    body,redo = set(), set()

    partition = [[local_data.alphabet[i] for i in range(0,len(local_data.alphabet)) if labels[i] == n] for n in range(0,n_components)]
    for ot in local_data.object_types:
        if not any(ot in global_data.related[a] and ot not in global_data.divergence[a] for a in local_data.alphabet):
            continue

        i = 0
        for i in range(0,n_components):
            if any(local_data.dfgs[ot][1].get(a,0) or local_data.dfgs[ot][2].get(a,0) for a in partition[i]):
                body = partition[i]
                break

        for j in range(0,n_components):
            if i != j and any([ot in global_data.related[a] for a in partition[j]]):
                redo = sum([partition[k] for k in range(0,n_components) if k != i],[])

                if is_loop_fallthrough_valid(local_data,global_data,[body,redo]) and body and redo:
                    if evaluate_loop_fallthrough(local_data,global_data,body,redo)[0] > best_score:
                        best_score, operator = evaluate_loop_fallthrough(local_data,global_data,body,redo)
                        best_partition = [body,redo]

    if set(sum(partition, [])) != set(local_data.alphabet):
        return -1,None,None

    return best_score, best_partition, Operator.LOOP



def detect_fallthrough_fitness_polynomial(local_data, global_data):

    best_score,best_partition, best_operator = 0.00, None, None

    for check in [detect_fallthrough_loop, detect_fallthrough_exclusive, detect_fallthrough_concurrent, detect_fallthrough_sequence]:
        score, partition, operator = check(local_data, global_data)
        if score >= best_score:
            best_score, best_partition, best_operator = score, partition, operator

    global_data.quality_info["fallthroughs"].append((best_partition, best_operator,best_score))
    return best_partition, best_operator



def detect_fallthrough_fitness_brute_force(local_data, global_data):

    best_score,best_partition, best_operator = 0.00, None, None

    for partition in mit.set_partitions(local_data.alphabet, 2):

        for check in [evaluate_xor_fallthrough, evaluate_concurrent_fallthrough]:

            if check == evaluate_xor_fallthrough and not is_exclusive_fallthrough_valid(local_data,global_data, partition):
                continue
            if check == evaluate_concurrent_fallthrough and not is_concurrent_fallthrough_valid(local_data,global_data, partition):
                continue

            score, operator = check(local_data,global_data,partition[0],partition[1])
            if score >= best_score:
                best_score, best_partition, best_operator = score, partition, operator


        for check in [evaluate_sequence_fallthrough, evaluate_loop_fallthrough]:

            if check == evaluate_sequence_fallthrough and not is_sequence_fallthrough_valid(local_data,global_data, partition):
                continue
            if check == evaluate_loop_fallthrough and not is_loop_fallthrough_valid(local_data,global_data, partition):
                continue

            score, operator = check(local_data,global_data,partition[0],partition[1])
            if score >= best_score:
                best_score, best_partition, best_operator = score, partition, operator

        partition = list(reversed(partition))
        for check in [evaluate_sequence_fallthrough, evaluate_loop_fallthrough]:

                if check == evaluate_sequence_fallthrough and not is_sequence_fallthrough_valid(local_data,global_data, partition):
                    continue
                if check == evaluate_loop_fallthrough and not is_loop_fallthrough_valid(local_data,global_data, partition):
                    continue

                score, operator = check(local_data, global_data, partition[0], partition[1])
                if score >= best_score:
                    best_score, best_partition, best_operator = score, partition, operator

    return best_partition,best_operator






