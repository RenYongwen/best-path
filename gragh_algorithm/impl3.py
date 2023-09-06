from heapq import heappush, heappop

class Node:
    def __init__(self, idx, type, supply=0, demand=0):
        self.idx = idx
        self.type = type
        self.supply = supply
        self.demand = demand
        self.neighbors = {}

    def add_neighbor(self, neighbor, weight):
        self.neighbors[neighbor] = weight

    def __lt__(self, other):
        return True
class Edge:
    def __init__(self, src, dst, weight):
        self.src = src
        self.dst = dst
        self.weight = weight

class Truck:
    def __init__(self, capacity):
        self.capacity = capacity
        self.remaining = capacity


import heapq

def dijkstra(nodes, start):
    # 创建优先队列，以起始节点开始进行最短路径搜索
    queue = [(0, start)]
    # 存储每个节点到起始节点的最短距离，初始值为正无穷
    dist = {node: float('inf') for node in nodes}
    # 起始节点到自身的距离为0
    dist[start] = 0

    # 当队列不为空时循环
    while queue:
        # 取出距离起始节点最近的节点，以及到该节点的距离
        curr_dist, curr_node = heapq.heappop(queue)

        # 如果该节点的最短距离已经计算过，则跳过
        if curr_dist > dist[curr_node]:
            continue

        # 遍历当前节点的邻居节点
        neighbors = [(neighbor, weight) for neighbor, weight in curr_node.neighbors.items()]
        for neighbor, weight in [(n, w) for n, w in neighbors if curr_dist + w < dist[n]]:
            # 计算邻居节点到起始节点的总距离
            total_dist = curr_dist + weight
            # 如果计算得到的距离比之前计算的该邻居节点的最短距离要小，则更新该邻居节点的最短距离，并将其加入到优先队列中
            dist[neighbor] = total_dist
            heapq.heappush(queue, (total_dist, neighbor))

    # 当队列为空时，所有节点到起始节点的最短距离都被计算出来了
    # 将其作为结果返回
    return dist



# 水源分配函数，计算从供水节点到需水节点运输水的最小代价
def water_distribution(nodes, edges, trucks):
    # 存储所有供水节点和需水节点
    supply_nodes = [node for node in nodes if node.type == 'supply']
    demand_nodes = [node for node in nodes if node.type == 'demand']

    # 计算每个供水节点到其他节点的最短距离
    dists = {node: dijkstra(nodes, node) for node in supply_nodes}

    # 遍历每辆卡车和每个需水节点，计算最小代价并将水运输到该需水节点
    for truck in trucks:
        for demand_node in demand_nodes:
            # 寻找到该需水节点的最短路径
            shortest_path = min(dists[supply_node][demand_node] for supply_node in supply_nodes)
            # 计算最大可以运输的水量（取决于卡车的容量和需水节点的需求量与供水量之差）
            max_water = min(truck.capacity, demand_node.demand - demand_node.supply)
            # 更新卡车剩余容量和需水节点的供水量
            truck.remaining -= max_water
            demand_node.supply += max_water

            # 更新供水节点与需水节点间的连接关系，使其满足最小代价限制
            for supply_node in supply_nodes:
                if dists[supply_node][demand_node] <= shortest_path:
                    supply_node.supply -= max_water
                    supply_node.neighbors[demand_node] = dists[supply_node][demand_node]

                    # 如果该供水节点的供水量小于0，则将多余的水分配到需水节点上，更新可运输的水量
                    if supply_node.supply < 0:
                        demand_node.supply += supply_node.supply
                        max_water += supply_node.supply
                        supply_node.supply = 0

                    # 如果已经达到了卡车的最大容量，则跳出循环
                    if max_water == truck.capacity:
                        break

            # 如果无法再分配更多的水，则跳出循环
            if max_water == 0:
                break

    # 计算实际运输的水的总代价（所有未被满足的需水节点之间的连线的长度）
    total_distance = sum(edge.weight for edge in edges if edge.src.supply > 0 and edge.dst.demand > 0)
    return total_distance

# 创建5个Node实例
node1 = Node(1, 'supply', supply=100)  # 供水节点1，初始供水量为100
node2 = Node(2, 'demand', demand=50)  # 需水节点1，初始需求量为50
node3 = Node(3, 'demand', demand=30)  # 需水节点2，初始需求量为30
node4 = Node(4, 'supply', supply=80)  # 供水节点2，初始供水量为80
node5 = Node(5, 'supply', supply=120)  # 供水节点3，初始供水量为120

# 对于每个Node实例添加其它节点为邻居以及到达邻居所需要的距离
node1.add_neighbor(node2, 10)
node1.add_neighbor(node4, 15)
node2.add_neighbor(node1, 10)
node2.add_neighbor(node3, 20)
node3.add_neighbor(node2, 20)
node4.add_neighbor(node1, 15)
node4.add_neighbor(node5, 25)
node5.add_neighbor(node4, 25)

nodes = [node1,node2,node3,node4,node5]

# 创建5个Edge实例，表示相邻两个节点之间的连接关系
edge1 = Edge(node1, node2, 10)
edge2 = Edge(node1, node4, 15)
edge3 = Edge(node2, node3, 20)
edge4 = Edge(node4, node5, 25)
edge5 = Edge(node1, node5, float('inf'))  # 在这种情况下，将节点1和节点5直接连接（边的权值为正无穷），以便卡车从供水节点1直接向需水节点2和3运输水

edges = [edge1,edge2,edge3,edge4,edge5]

# 创建5个Truck实例，每辆卡车的容量不同
truck1 = Truck(50)
truck2 = Truck(80)
truck3 = Truck(100)
truck4 = Truck(70)
truck5 = Truck(90)

trucks = [truck1,truck2,truck3,truck4,truck5]

print(water_distribution(nodes,edges,trucks))