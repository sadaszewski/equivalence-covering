#
# Copyright (C) Stanislaw Adaszewski, 2021.
# All Rights Reserved.
# License: BSD 2-clause
#


import networkx as nx
import numpy as np
from typing import Set, List, Any


def find_all_subsets(s: Set[Any], include_empty: bool= False) -> List[frozenset]:
    s = np.array(list(s))
    res = []
    for i in range(2**len(s)):
        mask = np.array([ bool((i >> k) & 0x1) for k in range(len(s)) ])
        if np.all(mask == False) and not include_empty:
            continue
        res.append(frozenset(s[mask]))
    return res


def find_all_cliques(g: nx.Graph) -> List[frozenset]:
    res = set()
    for c in nx.find_cliques(g):
        for c in find_all_subsets(c):
            res.add(c)
    res = sorted(res, key=lambda c: len(c), reverse=True)
    return res


def clique_edges(c: List[int]) -> List[frozenset]:
    c = list(c)
    res = []
    for i in range(len(c)):
        for k in range(i + 1, len(c)):
            res.append(frozenset([ c[i], c[k] ]))
    return res


def find_equivalence_covering(g: nx.Graph) -> List[List[frozenset]]:
    all_cliques = find_all_cliques(g)
    all_clique_edges = [ clique_edges(c) for c in all_cliques ]

    all_edges = { frozenset(e) for e in g.edges }
    edges_in_cover = set()
    res = []
    while len(edges_in_cover) != len(g.edges):
        current_vertices = set()
        cliques_used = set()
        current = []

        while len(current_vertices) != len(g):
            missing_edges = all_edges.difference(edges_in_cover)
            priority_cliques = [ all_cliques[i] for i, ce in enumerate(all_clique_edges) \
                if any(e in missing_edges for e in ce) and not any(v in current_vertices for v in all_cliques[i]) ]
            priority_cliques = sorted(priority_cliques, key=lambda c: len(c), reverse=True)

            if len(priority_cliques) > 0:
                c = priority_cliques[0]
            else:
                priority_cliques = [ all_cliques[i] for i, ce in enumerate(all_clique_edges) \
                    if all_cliques[i] not in cliques_used and not any(v in current_vertices for v in all_cliques[i]) ]
                priority_cliques = sorted(priority_cliques, key=lambda c: len(c), reverse=True)
                if len(priority_cliques) > 0:
                    c = priority_cliques[0]
                else:
                    raise ValueError('Cannot find a suitable clique')

            cliques_used.add(c)
            current_vertices = current_vertices.union(c)
            edges_in_cover = edges_in_cover.union(clique_edges(c))
            current.append(c)
        res.append(current)
    return res


def verify_equivalence_covering(c: List[List[frozenset]], g: nx.Graph) -> bool:
    edges_in_cover = set()
    for c_1 in c:
        for c_2 in c_1:
            g_1 = g.subgraph(c_2)
            # print('c_2:', c_2, 'g_1:', g_1, 'dens:', nx.density(g_1))
            if not ( len(g_1) == 1 or nx.density(g_1) == 1 ):
                return False
            edges_in_cover = edges_in_cover.union(g_1.edges)
    if not len(edges_in_cover) == len(g.edges):
        return False
    return True
