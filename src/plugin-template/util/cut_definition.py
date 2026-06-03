from ..util.auxillary_methods import *
import itertools

""" Methods to check if a cut is strictly valid. This code is not optimized in any way but rather a 1:1 reflection 
of the formulas for the cut definition from Section 3.1 of the paper. If needed in any time-critical setting, please
refer to the planned optimized RUST implementation from the DOCBP project of RWTH Aachen & Celonis. """


def is_concurrent_cut_valid(local_data,global_data, partition_list):
    if set(sum(partition_list, [])) != set(local_data.alphabet):
        return False
    #check for the bidrectional connection between activities in different partition parts (Section 3.1, Equation 17)
    for (i,j) in itertools.combinations(range(len(partition_list)), 2):
        for a in partition_list[i]:
            for b in partition_list[j]:
                for ot in global_data.related[a] & global_data.related[b]:
                    if not local_data.dfgs[ot][0].get((a,b),0) or not local_data.dfgs[ot][0].get((b,a),0):
                        return False

    #check for the correct propagation of projected start activities (Section 3.1 , Equation 18)
    for i in range(len(partition_list)):
        for a in partition_list[i]:
            for ot in global_data.related[a]:
                if a in get_projected_start(local_data, partition_list[i])[ot] and not local_data.dfgs[ot][1].get(a,0):
                    return False

    # check for the correct propagation of projected end activities (Section 3.1 , Equation 19)
    for i in range(len(partition_list)):
        for a in partition_list[i]:
            for ot in global_data.related[a]:
                if a in get_projected_end(local_data, partition_list[i])[ot] and not local_data.dfgs[ot][2].get(a,0):
                    return False

    return True


def is_exclusive_cut_valid(local_data, global_data, partition_list):
    if set(sum(partition_list, [])) != set(local_data.alphabet):
        return False
    #check for the correct propagation of projected start activities (Section 3.1 , Equation 18)
    for i in range(len(partition_list)):
        for a in partition_list[i]:
            for ot in global_data.related[a]:
                if a in get_projected_start(local_data, partition_list[i]) and not local_data.dfgs[ot][1].get(a,0):
                    return False

    # check for the correct propagation of projected start activities (Section 3.1 , Equation 19)
    for i in range(len(partition_list)):
        for a in partition_list[i]:
            for ot in global_data.related[a]:
                if a in get_projected_end(local_data, partition_list[i]) and not local_data.dfgs[ot][2].get(a,0):
                    return False


    # check for the absence of any connection between activities in different partition parts
    # for object types that are not fully divergent on the two partition parts (Section 3.1, Equation 20)
    for (i, j) in itertools.combinations(range(len(partition_list)), 2):
        for a in partition_list[i]:
            for b in partition_list[j]:
                for ot in get_non_divergent_types(a,b,partition_list[i]+partition_list[j],global_data):
                    if local_data.dfgs[ot][0].get((a, b), 0) or local_data.dfgs[ot][0].get((b, a), 0):
                        return False

    # check for the bidrectional connection between activities in different partition parts
    # for object types that are fully divergent on the two partition parts (Section 3.1, Equation 21)
    for (i, j) in itertools.combinations(range(len(partition_list)), 2):
        for a in partition_list[i]:
            for b in partition_list[j]:
                for ot in get_divergent_types(a,b,partition_list[i]+partition_list[j],global_data):
                    if not local_data.dfgs[ot][0].get((a, b), 0) or not local_data.dfgs[ot][0].get((b, a), 0):
                        return False

    # check if there is at least one non diverging object type between any two
    # partition parts (Section 3.1., Equation 22)
    for (i, j) in itertools.combinations(range(len(partition_list)), 2):
        if not any(get_non_divergent_types(a,b,partition_list[i]+partition_list[j], global_data)
               for a in partition_list[i] for b in partition_list[j]):
            return False

    return True


def is_sequence_cut_valid(local_data, global_data, partition_list):

    if set(sum(partition_list, [])) != set(local_data.alphabet):
        return False

    for (i, j) in itertools.combinations(range(len(partition_list)), 2):
        if i > j: i,j = j,i
        for a in partition_list[i]:
            for b in partition_list[j]:

                # check for the bidrectional connection between activities in different partition parts
                # for object types that are fully (sequencially) divergent (Section 3.1, Equation 23)
                for ot in get_divergent_types(a,b,sum([partition_list[k] for k in range(i,j+1)],[]),global_data):
                    if not local_data.dfgs[ot][0].get((a, b), 0) or not local_data.dfgs[ot][0].get((b, a), 0):
                        return False

                # check for the one directional transitive connection between activities in different partition parts
                # for object types that are not fully (sequencially) divergent (Section 3.1, Equation 24)
                for ot in get_non_divergent_types(a,b,sum([partition_list[k] for k in range(i,j+1)],[]),global_data):
                    if not local_data.clos[ot].get((a, b), 0) or local_data.clos[ot].get((b, a), 0):
                        return False

    #check if there is at least one non diverging object type between any two
    #partition parts that follow each other (Section 3.1., Equation 25)
    for i in range(0,len(partition_list)-1):
        j = i+1
        if not any(get_non_divergent_types(a,b,partition_list[i]+partition_list[j], global_data)
               for a in partition_list[i] for b in partition_list[j]):
            return False

    return True



def is_loop_cut_valid(local_data, global_data, partition_list):
    if set(sum(partition_list, [])) != set(local_data.alphabet):
        return False
    # check if there is at least one non diverging object type between the two
    # partition parts (Section 3.1., Equation 26)

    if not any(get_non_divergent_types(a, b, partition_list[0] + partition_list[1], global_data)
               for a in partition_list[0] for b in partition_list[1]):
        return False

    # check for the bidrectional connection between activities in different partition parts
    # for object types that are fully divergent on the two partition parts (Section 3.1, Equation 27)
    for a in partition_list[0]:
        for b in partition_list[1]:
            for ot in get_divergent_types(a,b,partition_list[0]+partition_list[1],global_data):
                if not local_data.dfgs[ot][0].get((a,b),0) or not local_data.dfgs[ot][0].get((b,a),0):
                    return False

    # check for the bidrectional transitive connection between activities in different partition parts
    # for object types that are not fully divergent on the two partition parts (Section 3.1, Equation 28)
    for a in partition_list[0] + partition_list[1]:
        for b in partition_list[0] + partition_list[1]:
            for ot in get_non_divergent_types(a,b,partition_list[0]+partition_list[1],global_data):
                if not local_data.clos[ot].get((a,b),0) or not local_data.clos[ot].get((b,a),0):
                    return False


    relevant_type = sum([get_non_divergent_types(a, b, partition_list[0] + partition_list[1], global_data)
               for a in partition_list[0] for b in partition_list[1]],[])

    #check for the relevant types if the propagation of start activities is correctly distributed
    #into the body part of the loop (Section 3.1, Equation 29)
    for ot in relevant_type:
        if not all(a in partition_list[0] for a,value in local_data.dfgs[ot][1].items() if value and a in partition_list[0] + partition_list[1]):
            return False


    #check for the relevant types if the propagation of end activities is correctly distributed
    #into the body part of the loop (Section 3.1, Equation 30)
    for ot in relevant_type:
        if not all(a in partition_list[0] for a,value in local_data.dfgs[ot][2].items() if value and a in partition_list[0] + partition_list[1]):
            return False

    #check if all crossings from the body to the redo part of the loop are from end activities in the body
    #part of the loop (Section 3.1, Equation 31)
    for a in partition_list[0]:
        for b in partition_list[1]:
            for ot in get_non_divergent_types(a,b,partition_list[0]+partition_list[1],global_data):
                if local_data.dfgs[ot][0].get((a,b),0) and not local_data.dfgs[ot][2].get(a,0):
                    return False

    #check if all crossings from the redo to the body part of the loop go to start activities in the body
    #part of the loop (Section 3.1, Equation 32)
    for a in partition_list[1]:
        for b in partition_list[0]:
            for ot in get_non_divergent_types(a,b,partition_list[0]+partition_list[1],global_data):
                if local_data.dfgs[ot][0].get((a,b),0) and not local_data.dfgs[ot][1].get(b,0):
                    return False

    return True