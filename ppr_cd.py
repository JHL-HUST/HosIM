import collections


def ppr_cd(adjacency_list, subgraph_nodes, seed_nodes, query_node, center_node=None, sample_flag=False):
    alpha = 0.99
    tol = 0.001
    x = {}  # Store x, r as dictionaries
    r = {}  # initialize residual
    Q = collections.deque()  # initialize queue
    if center_node is None:
        for sn in seed_nodes:
            if sn == query_node:
                r[sn] = 0.3 / len(seed_nodes) + 0.7
            else:
                r[sn] = 0.3 / len(seed_nodes)
            Q.append(sn)
    else:
        for sn in seed_nodes:
            if sn == query_node:
                r[sn] = 0.2 / len(seed_nodes) + 0.7
            elif sn == center_node:
                r[sn] = 0.2 / len(seed_nodes) + 0.1
            else:
                r[sn] = 0.2 / len(seed_nodes)
            Q.append(sn)
    nodes_neighbors = dict()
    for tn in subgraph_nodes:
        nodes_neighbors[tn] = adjacency_list[tn].intersection(subgraph_nodes)
    while len(Q) > 0:
        v = Q.popleft()  # v has r[v] > tol*deg(v)
        if v not in x:
            x[v] = 0
        x[v] += (1 - alpha) * r[v]
        mass = alpha * r[v] / (2 * len(nodes_neighbors[v]))
        for u in nodes_neighbors[v]:  # for neighbors of u
            assert u is not v, "Error"
            if u not in r: r[u] = 0.
            if r[u] < len(nodes_neighbors[u]) * tol and r[u] + mass >= len(nodes_neighbors[u]) * tol:
                Q.append(u)  # add u to queue if large
            r[u] = r[u] + mass
        r[v] = mass * len(nodes_neighbors[v])
        if r[v] >= len(nodes_neighbors[v]) * tol:
            Q.append(v)
    for v in x:
        x[v] = x[v] / len(nodes_neighbors[v])
    sv = sorted(x.items(), key=lambda x: x[1], reverse=True)
    if sample_flag is True:
        return sv
    S = set()
    volS = 0
    cutS = 0
    Gvol = 0
    for tn in subgraph_nodes:
        Gvol += len(nodes_neighbors[tn])
    bestcond = 1
    bestset = sv
    for p in sv:
        s = p[0]  # get the vertex
        volS += len(nodes_neighbors[s])  # add degree to volume
        for v in nodes_neighbors[s]:
            if v in S:
                cutS -= 1
            else:
                cutS += 1
        # #         print("v: %4i  cut: %4f  vol: %4f"%(s, cutS,volS))
        S.add(s)
        denom = min(volS, Gvol - volS)
        if cutS == denom:
            bestset = [v for (v, p) in sv]
            bestcond = 1
        else:
            if cutS / denom < bestcond:
                bestcond = cutS / denom
                bestset = set(S)  # make a copy
    return set(bestset)  # , bestcond
