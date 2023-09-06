from collections import deque


class Node:
    def __init__(self, name, flow=0):
        self.name = name
        self.flow = flow
        self.edges = []

    def __repr__(self):
        return self.name


class Edge:
    def __init__(self, source, dest, capacity, cost):
        self.source = source
        self.dest = dest
        self.capacity = capacity
        self.cost = cost
        self.flow = 0

    def __repr__(self):
        return f'{self.source} -> {self.dest} ({self.flow}/{self.capacity}, {self.cost})'


class Network:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_node(self, name, flow=0):
        node = Node(name, flow)
        self.nodes.append(node)
        return node

    def add_edge(self, source, dest, capacity, cost):
        edge = Edge(source, dest, capacity, cost)
        self.edges.append(edge)
        source.edges.append(edge)
        dest.edges.append(edge)


def allocate_trucks(sources, intermediates, destinations, trucks):
    """
    解决路径最优问题的函数，输入为出水点、中转站和用水点的列表，以及卡车的列表，
    输出为分配方案，即每个卡车要经过哪些节点，以及每个节点需要接收多少水。
    """
    # 创建网络模型
    network = Network()
    source_node = network.add_node('source')
    intermediate_nodes = [network.add_node(name) for name in intermediates]
    dest_nodes = [network.add_node(name) for name in destinations]

    # 添加出水点到中转站的边
    for i, source in enumerate(sources):
        for j, intermediate in enumerate(intermediate_nodes):
            network.add_edge(source_node, intermediate, float('inf'), 0)
            network.add_edge(intermediate, source_node, 0, 0)

    # 添加中转站到用水点的边
    for i, intermediate in enumerate(intermediate_nodes):
        for j, dest in enumerate(dest_nodes):
            network.add_edge(intermediate, dest, float('inf'), 0)
            network.add_edge(dest, intermediate, 0, 0)

    # 添加源节点到出水点的边
    for i, source in enumerate(sources):
        source_node.edges[i].capacity = source.flow
        source_node.edges[i].cost = 0
        source_node.edges[i].dest.flow += source.flow

    # 添加用水点到汇节点的边
    for i, dest in enumerate(dest_nodes):
        dest.edges[i].capacity = dest.flow
        dest.edges[i].cost = 0
        dest.edges[i].source.flow -= dest.flow

    # 添加卡车的容量限制
    for i, truck in enumerate(trucks):
        for node in network.nodes:
            if node == source_node or node == dest_nodes:
                continue
            demand = min(node.flow, truck.capacity)
            network.add_edge(node, node, demand, 1)
            node.flow -= demand

    # 求解最小费用最大流
    while True:
        # 使用BFS算法查找增广路径
        queue = deque([source_node])
        parent = {node: None for node in network.nodes}
        parent[source_node] = source

        while queue:
            node = queue.popleft()
            for edge in node.edges:
                if edge.capacity - edge.flow > 0 and parent[edge.dest] is None:
                    parent[edge.dest] = edge
                    queue.append(edge.dest)
                    if edge.dest in dest_nodes:
                        break

        # 如果没有增广路径，则退出循环
        if parent[dest_nodes[0]] is None:
            break

        # 计算增广路径的流量和费用
        flow = min(edge.capacity - edge.flow for edge in parent.values() if edge is not None)
        cost = sum(edge.cost * flow for edge in parent.values() if edge is not None)

        # 更新每条边的流量
        for edge in parent.values():
            if edge is not None:
                edge.flow += flow
                edge.source.flow -= flow
                edge.dest.flow += flow

    # 根据最小费用最大流结果计算每个卡车需要经过的节点和每个节点需要接收的水量
    allocations = {}
    for i, truck in enumerate(trucks):
        allocations[i] = []
        for node in network.nodes:
            if node == source_node or node == dest_nodes:
                continue
            for edge in node.edges:
                if edge.source == node and edge.flow > 0:
                    allocations[i].append((node, edge.flow))

    return allocations
    # 这个函数的输入为出水点、中转站和用水点的列表，以及卡车的列表，输出为分配方案，即每个卡车要经过哪些节点，以及每个节点需要接收多少水。
