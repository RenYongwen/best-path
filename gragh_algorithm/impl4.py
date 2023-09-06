from queue import PriorityQueue

def find_min_cost_max_flow(s, t, n, d, s_list, c, edges):
    # 1. 将所有节点拆分为供水/需水节点，建图并计算净需求 
    m = len(c)
    super_s, super_t = 2 * n, 2 * n + 1
    g = [[] for _ in range(2 * n + 2)]
    ans = 0
    for i in range(n):
        if s[i] > 0:
            g[super_s].append((i, s[i], 0, len(g[i])))
            g[i].append((super_s, 0, 0, len(g[super_s]) - 1))
        else:
            g[i + n].append((super_t, -s[i], 0, len(g[super_t])))
            g[super_t].append((i + n, 0, 0, len(g[i + n]) - 1))
        ans += abs(s[i])
    for i in range(m):
        u, v, w = edges[i]
        g[u].append((v + n, float('inf'), w, len(g[v + n])))
        g[v + n].append((u, 0, -w, len(g[u]) - 1))
    for i in range(n):
        g[i].append((i + n, d[i], 0, len(g[i + n])))
        g[i + n].append((i, 0, 0, len(g[i]) - 1))

    # 2. 使用最小费用最大流算法 
    flow = 0
    cost = 0
    while True:
        dist = [float('inf')] * (2 * n + 2)
        dist[super_s] = 0
        pq = PriorityQueue()
        pq.put((0, super_s))
        pre = [(None, None)] * (2 * n + 2)
        vis = [False] * (2 * n + 2)
        while not pq.empty():
            d, u = pq.get()
            if vis[u]:
                continue
            vis[u] = True
            for i in range(len(g[u])):
                v, cap, w, idx = g[u][i]
                if cap <= 0 or dist[v] <= d + w:
                    continue
                pre[v] = (u, idx)
                dist[v] = d + w
                pq.put((dist[v], v))
        if dist[super_t] == float('inf'):
            break
        f = float('inf')
        u = super_t
        while u != super_s:
            p, idx = pre[u]
            _, cap, _, _ = g[p][idx]
            f = min(f, cap)
            u = p
        flow += f
        cost += f * dist[super_t]
        u = super_t
        while u != super_s:
            p, idx = pre[u]
            g[p][idx] = (g[p][idx][0], g[p][idx][1] - f, g[p][idx][2], g[p][idx][3])
            _, cap, w, rev_idx = g[u][idx]
            g[u][idx] = (g[u][idx][0], g[u][idx][1] + f, g[u][idx][2], g[u][idx][3])
            u = p

    # 3. 确定答案并返回结果 
    if flow < ans:
        return "Not enough water supply"
    trucks = 0
    for i in range(m):
        u, v, w = edges[i]
        for j in range(w):
            remain = c[trucks] - s_list[u * w + j]
            if remain >= s_list[v * w + j]:
                remain -= s_list[v * w + j]
            else:
                trucks += 1
                remain = c[trucks] - s_list[u * w + j]
            s_list[v * w + j] = 0
            s_list[u * w + j] += remain
    return trucks + 1, cost
