class Node:
    def __init__(self, id, type, supply):
        self.id = id
        self.type = type
        self.supply = supply

class Edge:
    def __init__(self, from_node, to_node, capacity):
        self.from_node = from_node
        self.to_node = to_node
        self.capacity = capacity
