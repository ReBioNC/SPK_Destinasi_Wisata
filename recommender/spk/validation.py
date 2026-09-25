"""Validasi internal: SAW pembanding + korelasi Spearman. Stdlib only.

Tidak diekspos ke pengguna; hanya untuk test dan cangkang Django.
"""


def saw_rank(scores, weights, is_cost):
    """Ranking SAW; mengembalikan list (idx, Si) terurut Si menurun."""
    n, m = len(scores), len(scores[0])
    lo = [min(scores[i][j] for i in range(n)) for j in range(m)]
    hi = [max(scores[i][j] for i in range(n)) for j in range(m)]
    ranked = []
    for i in range(n):
        s = sum(weights[j] * (lo[j] / scores[i][j] if is_cost[j] else scores[i][j] / hi[j])
                for j in range(m))
        ranked.append((i, s))
    return sorted(ranked, key=lambda t: t[1], reverse=True)


def spearman(order_a, order_b):
    """Korelasi peringkat; input = list idx dari terbaik ke terburuk."""
    n = len(order_a)
    pos_b = {idx: r for r, idx in enumerate(order_b)}
    d2 = sum((r - pos_b[idx]) ** 2 for r, idx in enumerate(order_a))
    return 1 - (6 * d2) / (n * (n * n - 1))
