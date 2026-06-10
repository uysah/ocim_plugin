from ..util.fallthrough_definition import *
from ..resource import *

def evaluate_concurrent_fallthrough(local_data, global_data, part_one, part_two):

    precision_violation = 0
    precision_correct = 0

    for a in part_one:
        for b in part_two:
            for ot in global_data.related[a] & global_data.related[b]:
                if not local_data.dfgs[ot][0].get((a,b),0):
                    precision_violation += 1
                else:
                    precision_correct += 1
                if not local_data.dfgs[ot][0].get((b,a),0):
                    precision_violation += 1
                else:
                    precision_correct += 1

    try:
        return 1- (precision_violation / (precision_correct + precision_violation)), Operator.PARALLEL
    except:
        return 1, Operator.PARALLEL


def evaluate_xor_fallthrough(local_data, global_data, part_one, part_two):

    precision_violation = 0
    precision_correct = 0

    for a in part_one:
        for b in part_two:
            for ot in get_divergent_types(a,b,part_one+part_two,global_data):
                if not local_data.dfgs[ot][0].get((a, b), 0):
                    precision_violation += 1
                else:
                    precision_correct += 1
                if not local_data.dfgs[ot][0].get((b, a), 0):
                    precision_violation += 1
                else:
                    precision_correct += 1

    try:
        return 1- (precision_violation / (precision_correct + precision_violation)), Operator.XOR
    except:
        return 1, Operator.XOR


def evaluate_sequence_fallthrough(local_data, global_data, part_one, part_two):

    precision_violation = 0
    precision_correct = 0

    for a in part_one:
        for b in part_two:
            for ot in get_divergent_types(a,b,part_one+part_two,global_data):
                if not local_data.dfgs[ot][0].get((a, b), 0):
                    precision_violation += 1
                else:
                    precision_correct += 1
                if not local_data.dfgs[ot][0].get((b, a), 0):
                    precision_violation += 1
                else:
                    precision_correct += 1
            for ot in get_non_divergent_types(a,b,part_one+part_two,global_data):
                if not local_data.clos[ot].get((a, b), 0):
                    precision_violation += 1
                else:
                    precision_correct += 1

    try:
        return 1- (precision_violation / (precision_correct + precision_violation)), Operator.SEQUENCE
    except:
        return 1, Operator.SEQUENCE


def evaluate_loop_fallthrough(local_data, global_data, part_one, part_two):

    precision_violation = 0
    precision_correct = 0

    for a in part_one:
        for b in part_two:
            for ot in get_divergent_types(a,b,part_one+part_two,global_data):
                if not local_data.dfgs[ot][0].get((a, b), 0):
                    precision_violation += 1
                else:
                    precision_correct += 1
                if not local_data.dfgs[ot].get((b, a), 0):
                    precision_violation += 1
                else:
                    precision_correct += 1
    for a in part_one +part_two:
        for b in part_one + part_two:
            for ot in global_data.related[a] & global_data.related[b]:
                if not local_data.clos[ot].get((a, b), 0):
                    precision_violation += 1
                else:
                    precision_correct += 1

    try:
        return 1- (precision_violation / (precision_correct + precision_violation)), Operator.LOOP
    except:
        return 1, Operator.LOOP
