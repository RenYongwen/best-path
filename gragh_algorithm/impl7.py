import networkx as nx

def find_max_flow_paths(G, source, target):
    # 计算最大流量及其分配方案
    _, flow_dict = nx.maximum_flow(G, source, target)
    # 获取最大流量的路径列表
    max_flow_paths = []
    for u in G.successors(source):
        for v in G.predecessors(target):
            if u in flow_dict and v in flow_dict[u] and flow_dict[u][v] > 0:
                max_flow_paths.append(nx.shortest_path(G, u, v))
    print(max_flow_paths)
    exit()
    # 找到所有最大流量路径上的路径方案
    all_max_flow_paths = []
    for path in max_flow_paths:
        for simple_path in nx.all_simple_paths(G, path[0], path[-1]):
            if all(flow_dict[simple_path[i]][simple_path[i+1]] > 0 for i in range(len(simple_path)-1)):
                all_max_flow_paths.append(simple_path)
    
    return all_max_flow_paths
# 创建有向图
G = nx.DiGraph()
G.add_edges_from([('s', 'a', {'capacity': 3}), ('s', 'b', {'capacity': 4}),
                  ('a', 'b', {'capacity': 2}), ('a', 'c', {'capacity': 2}),
                  ('b', 'd', {'capacity': 3}), ('c', 'd', {'capacity': 2}),
                  ('c', 't', {'capacity': 3}), ('d', 't', {'capacity': 4})])

# 找到所有最大流量路径方案
max_flow_paths = find_max_flow_paths(G, 's', 't')

# 打
print(max_flow_paths)