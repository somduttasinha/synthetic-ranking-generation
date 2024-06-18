import math
import numpy as np
import random


def jaccard_similarity(set1, set2):
    """
    Compute the Jaccard similarity between two sets.

    set1: first set
    set2: second set
    """
    intersection = set1.intersection(set2)
    union = set1.union(set2)

    return len(intersection) / len(union)


def generate_domains(a, b, jaccard_similarity):
    """
    Generate two sets of size n that have a Jaccard similarity of jac_value.

    n: size of the sets
    jac_value: Jaccard similarity between the two sets
    """

    intersection_size = math.floor((jaccard_similarity * (a + b)) / (1 + jaccard_similarity))

    set_a = set()
    set_b = set()

    for i in range(intersection_size):
        item_label = "i" + str(i)
        set_a.add(item_label)
        set_b.add(item_label)

    a_rem = a - intersection_size
    b_rem = b - intersection_size

    for i in range(a_rem):
        set_a.add("a" + str(i))

    for i in range(b_rem):
        set_b.add("b" + str(i))

    return set_a, set_b


def _ensure_two_separation(xs, n):
    """
    Ensure that the elements in xs are at least 2 apart. This is done so that the tied groups have at least 2 elements in them.

    xs: list containing the tied items start indices
    n: number of elements in the domain
    """

    xs.sort()

    altered_list = False

    for i in range(1, len(xs)):
        if (xs[i] - xs[i - 1]) < 2 or (xs[i] == n - 1):
            altered_list = True
            new = (xs[i] + 1) % n
            xs[i] = new

    # check again
    if altered_list:
        xs = _ensure_two_separation(xs, n)

    return xs


def add_ties(X, frac_ties, num_groups, probabilities):
    """
    Add ties to a list of items

    X: list of items
    frac_ties: fraction of items that should be tied
    num_groups: number of tie groups
    probabilities: probabilities of selecting each item as a tie group start
    """

    if frac_ties == 0:
        return X

    n = len(X)

    assert num_groups <= n / 2
    assert len(probabilities) == n

    indices = np.arange(0, n)

    selected_start_indices = np.random.choice(
        indices, size=num_groups, replace=False, p=probabilities
    )
    selected_start_indices = _ensure_two_separation(selected_start_indices, n)

    X_with_ties = []

    num_tied_items = math.floor(frac_ties * n)

    if (num_tied_items / 2) < num_groups:
        raise Exception("Not enough groups")

    average_group_size = math.floor(num_tied_items / num_groups)

    i = 0

    while i < n:
        if i in selected_start_indices:
            tie_group_length = np.random.poisson(average_group_size - 2) + 2

            tie_group = [X[i]]

            for j in range(1, tie_group_length):
                if (i + j) in selected_start_indices:
                    i -= 1
                    break
                if i + j < n:
                    tie_group.append(X[i + j])

            X_with_ties.append(tie_group)
            i += j + 1
        else:
            X_with_ties.append(X[i])
            i += 1

    return X_with_ties


def simulate_rankings(
    a,
    b,
    len_x,
    len_y,
    overlap_probability_function,
    tie_probabilities_x=None,
    tie_probabilities_y=None,
    frac_ties_x=0,
    n_groups_x=0,
    frac_ties_y=0,
    n_groups_y=0,
    conjointness=1,
    truncate_rankings=True,
):
    """
    Simulate rankings of two sets of items.

    n: number of items to be ranked
    len_x: truncation length of the first ranking
    len_y: truncation length of the second ranking
    overlap_probability_function: function that determines the probability of increasing overlap between the two rankings at a given depth
    tie_probabilities_x: probabilities of selecting each item as a tie group start for the first ranking
    tie_probabilities_y: probabilities of selecting each item as a tie group start for the second ranking
    frac_ties_x: fraction of items that should be tied in the first ranking
    n_groups_x: number of tie groups in the first ranking
    frac_ties_y: fraction of items that should be tied in the second ranking
    n_groups_y: number of tie groups in the second ranking
    conjointness: degree of conjointness between the two rankings
    return_truncated: whether to return truncated rankings
    """

    assert a >= len_x
    assert b >= len_y

    # generate the two domains depending on the degree of conjointness
    A, B = generate_domains(a, b, conjointness)

    n = a if a < b else b

    S = []
    L = []
    case_list = []
    overlap_probs = []

    cases = [1, 2, 3, 4]

    decision = 0

    for depth in range(1, n + 1):

        overlap_prob = overlap_probability_function(depth=depth, n=n)

        overlap_probs.append(overlap_prob)

        u = np.random.uniform()

        item_S_domain = None
        item_L_domain = None

        item_S = None
        item_L = None

        if u < overlap_prob:
            # CASE 1: 1/4 of the time, choose some element that is in the intersection of S domain (a) and L so far
            # CASE 2: 1/4 of the time, choose some element that is in the intersection of L domain (b) and S so far
            # CASE 3: 1/4 of the time, choose some element that has not yet been taken - from the intersection a and b
            # CASE 4: 1/4 of the time, choose some element that from L and add to S and vice versa.

            decision = random.sample(cases, 1)[0]

            if decision == 1:
                item_S_domain = A.intersection(set(L))
                item_L_domain = B

            elif decision == 2:
                item_S_domain = A
                item_L_domain = B.intersection(set(S))

            elif decision == 3:
                item_S_domain = A.intersection(B)
                item_L_domain = A.intersection(B)

                # already draw item for S and L to make sure they are the same

                if len(item_S_domain) > 0:
                    item_S = random.sample(sorted(item_S_domain), 1)[0]
                    item_L = item_S

            elif decision == 4:
                item_S_domain = A.intersection(set(L))
                item_L_domain = B.intersection(set(S))

            else:
                raise Exception("Invalid decision")

        else:
            item_S_domain = A
            item_L_domain = B
            decision = 0

        if item_S is None:
            if len(item_S_domain) > 0:
                item_S = random.sample(sorted(item_S_domain), 1)[0]
            else:
                item_S = random.sample(sorted(A), 1)[0]
                decision = 0

        if item_L is None:
            if len(item_L_domain) > 0:
                item_L = random.sample(sorted(item_L_domain), 1)[0]
            else:
                item_L = random.sample(sorted(B), 1)[0]
                decision = 0

        case_list.append(decision)

        S.append(item_S)
        L.append(item_L)

        A.remove(item_S)
        B.remove(item_L)

    # randomly sample the rest of the items from the remaining domain

    for _ in range(n, a):
        item_S = random.sample(sorted(A), 1)[0]
        S.append(item_S)
        A.remove(item_S)

    for _ in range(n, b):
        item_L = random.sample(sorted(B), 1)[0]
        L.append(item_L)
        B.remove(item_L)

    S_with_ties = add_ties(
        S, frac_ties_x, n_groups_x, probabilities=tie_probabilities_x
    )
    L_with_ties = add_ties(
        L, frac_ties_y, n_groups_y, probabilities=tie_probabilities_y
    )

    if truncate_rankings:
        return (
            S_with_ties[:len_x],
            L_with_ties[:len_y],
            overlap_probs[:min(len_x, len_y)],
            case_list[:min(len_x, len_y)]
        )

    return S_with_ties, L_with_ties, overlap_probs, case_list
