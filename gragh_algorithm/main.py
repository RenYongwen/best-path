import random

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.parent = []
        self.children = []

    def add_child(self, child_node):
        child_node.parent.append(self)
        self.children.append(child_node)

    def get_parent(self):
        return self.parent

    def get_children(self):
        return self.children

    def get_sibling(self):
        if self.parent is not None:
            siblings = self.parent.children
            index = siblings.index(self)
            if index > 0:
                return siblings[index - 1]
            else:
                return None

    def __str__(self):
        return str(self.value)

# 初始化节点和路线
nodes = [
    ['C1','C2','C3'],
    ['N1','N2','N3','N4','N5'],
    ['P1','P2','P3','P4','P5','P6','P7','P8','P9','P10'],
]

M_CN = [[random.randint(0, 100) for j in range(len(nodes[0]))] for i in range(len(nodes[1]))]
M_NP = [[random.randint(0, 100) for j in range(len(nodes[1]))] for i in range(len(nodes[2]))]

# 创建根节点
Node_R = TreeNode('R')
for C in nodes[0]:
    Node_C = TreeNode(C)
    Node_R.add_child(Node_C)
    for N in nodes[1]:
        Node_N = TreeNode(N)
        Node_C.add_child(Node_N)
        for P in nodes[2]:
            Node_P = TreeNode(P)
            Node_N.add_child(Node_P)

root = TreeNode('A')

# 创建子节点并连接到根节点
child_b = TreeNode('B')
root.add_child(child_b)

child_c = TreeNode('C')
root.add_child(child_c)

# 创建孙节点并连接到子节点
grandchild_d = TreeNode('D')
child_b.add_child(grandchild_d)
child_c.add_child(grandchild_d)

grandchild_e = TreeNode('E')
child_b.add_child(grandchild_e)
child_c.add_child(grandchild_e)

# 访问父节点、兄弟节点和孩子节点
print(grandchild_d.get_parent())    # 输出: A
print(grandchild_e.get_sibling())   # 输出: B
print(root.get_children())    # 输出: [B, C]
