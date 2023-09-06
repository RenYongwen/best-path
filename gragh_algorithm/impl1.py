from typing import List, Tuple, Dict

def water_allocation(produces: List[float], needs: List[float], edges: List[Tuple[int, int, float]], vols: List[float]) -> Dict[int, List[Tuple[int, float]]]:
    n = len(produces) + len(needs)  # 总节点数
    m = len(edges)  # 总边数

    # 构造网络流图的邻接表表示
    graph = [[] for _ in range(n)]
    for i, (u, v, w) in enumerate(edges):
        graph[u].append((v, i))  # 正向边
        graph[v].append((u, i))  # 反向边

    # 构造网络流模型的超级源点和超级汇点
    source = n
    sink = n + 1

    # 构造源点和汇点与其他节点之间的边
    edges.extend([(source, i, float("inf")) for i in range(len(produces))])  # 超级源点连接出水点
    edges.extend([(i + len(produces), sink, float("inf")) for i in range(len(needs))])  # 用水点连接超级汇点

    # 构造每辆卡车可以经过的节点列表
    paths = []
    for vol in vols:
        path = []
        cur_vol = 0
        for i, need in enumerate(needs):
            if cur_vol + need <= vol:
                path.append((i + len(produces), need))
                cur_vol += need
            else:
                path.append((i + len(produces), vol - cur_vol))
                cur_vol = vol
                break
        paths.append(path)

    # 按照题意构造最大流模型，并求解最大流量
    max_flow = 0
    for path in paths:
        residual_graph = [[(b,c) for a, b, c in edges if a==_] for _ in range(n + 2)]  # 残留网络
        print(graph)
        print(residual_graph)
        while True:
            q = [source]
            pred = [-1] * (n + 2)
            while q and pred[sink] == -1:
                u = q.pop(0)
                for v, e_idx in graph[u]:
                    if residual_graph[u][e_idx] > 0 and pred[v] == -1:
                        pred[v] = e_idx
                        q.append(v)
            if pred[sink] == -1:
                break
            bottleneck = float("inf")
            v = sink
            while v != source:
                u = edges[pred[v]][0]
                bottleneck = min(bottleneck, residual_graph[u][pred[v]])
                v = u
            v = sink
            while v != source:
                u = edges[pred[v]][0]
                residual_graph[u][pred[v]] -= bottleneck
                residual_graph[v][pred[v] ^ 1] += bottleneck
                v = u
            max_flow += bottleneck * vol

    # 构造最优分配方案
    allocation = {}
    for i, path in enumerate(paths):
        allocation[i] = [(j, f) for j, f in path if f > 0]

    return allocation

def test_water_allocation():
    # 构造网络流图
    produces = [20.0, 30.0]
    needs = [25.0, 0, 25.0, 25.0]
    edges = [(0, 2, 10.0), (1, 2, 5.0), (2, 3, 30.0), (2, 4, 20.0), (3, 5, 20.0), (4, 5, 30.0)]
    vols = [10, 60.0, 80.0]

    # 测试最优分配方案是否正确
    allocation = water_allocation(produces, needs, edges, vols)

    print(allocation)

test_water_allocation()