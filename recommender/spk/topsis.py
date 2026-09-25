"""TOPSIS: perankingan alternatif. Stdlib only."""

import math


def rank(scores, weights, is_cost):
    """Rank alternatif menurun berdasarkan nilai preferensi Vi.

    scores: list baris [C1..C6] (float). Mengembalikan list dict
    {"idx", "vi", "d_pos", "d_neg", "gap"} terurut Vi menurun.
    gap[j] = |v_ij - A+_j|, dipakai untuk explainability.
    """
    n, m = len(scores), len(scores[0])
    den = [math.sqrt(sum(scores[i][j] ** 2 for i in range(n))) for j in range(m)]
    v = [[(scores[i][j] / den[j]) * weights[j] for j in range(m)] for i in range(n)]
    ideal_pos = [(min(v[i][j] for i in range(n)) if is_cost[j]
                  else max(v[i][j] for i in range(n))) for j in range(m)]
    ideal_neg = [(max(v[i][j] for i in range(n)) if is_cost[j]
                  else min(v[i][j] for i in range(n))) for j in range(m)]
    out = []
    for i in range(n):
        dp = math.sqrt(sum((v[i][j] - ideal_pos[j]) ** 2 for j in range(m)))
        dn = math.sqrt(sum((v[i][j] - ideal_neg[j]) ** 2 for j in range(m)))
        out.append({"idx": i, "vi": dn / (dp + dn), "d_pos": dp, "d_neg": dn,
                    "gap": [abs(v[i][j] - ideal_pos[j]) for j in range(m)]})
    return sorted(out, key=lambda r: r["vi"], reverse=True)
