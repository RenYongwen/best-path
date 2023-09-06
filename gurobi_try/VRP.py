import numpy as np
import random
import matplotlib.pyplot as plt
from gurobipy import Model, GRB, quicksum
import gurobipy




# def count_path(path, s, e):  # [1,3,2,4,6,8]中寻找
#     # model.update()
#     count = 0
#     for i in range(len(path) - 1):
#         count += path[i] - s
#         print(path[i],count)

#     return count

# def path2tuple(path):  # [1,3,2,4,6,8]转化为[('N1','N3'),('N2,'N4'),('N6','N8'))
#     tuple = []
#     for i in range(0, len(path), 2):
#         pair = (path[i], path[i + 1])
#         tuple.append(pair)
#     return tuple

def node2num(Ni):
    if Ni[0] == 'P':
        return int(Ni[1:])
    elif Ni[0] == 'N':
        return int(Ni[1:]) + len(Nodes['P'])
    elif Ni[0] == 'C':
        return int(Ni[1:]) + len(Nodes['P']) + len(Nodes['N'])


def num2node(i):
    if i < len(Nodes['P']):
        return 'P' + str(i)
    elif i < len(Nodes['P']) + len(Nodes['N']):
        return 'N' + str(i - len(Nodes['P']))
    else:
        return 'C' + str(i - len(Nodes['P']) - len(Nodes['N']))



random.seed(1)  # 随机种子，如有本行，则程序每次运行结果一样。可任意赋值

data_dict = {'A': (10, 3, 10), 'B': (5, 2, 15), 'C': (2, 1, 20)}  # (载重，每公里价格，车数量)默认每辆车每天可跑500km

Nodes = {
    'P': {f'P{i}': (random.random() * 100, random.random() * 50, random.randint(500, 1000)) for i in range(3)},  # 供给方Pi（X，Y，供水量）
    'N': {f'N{i}': (random.random() * 100, random.random() * 50,) for i in range(5)},  # 中转站Ni（X，Y）
    'C': {f'C{i}': (random.random() * 100, random.random() * 50, random.randint(50, 100)) for i in range(10)},  # 需求方Ci（X，Y，耗水量）
    'T': {f'T{x}{i}': (data_dict[x][0], data_dict[x][1]) for x in data_dict.keys() for i in range(data_dict[x][2])}  # 卡车TXi（载重，每公里价格）
}

model = Model('TRY')
K_P = [Pi for Pi in Nodes['P'].keys()]
K_N = [Ni for Ni in Nodes['N'].keys()]
K_C = [Ci for Ci in Nodes['C'].keys()]
K_PN = [(Pi, Nj) for Pi in Nodes['P'].keys() for Nj in Nodes['N'].keys()]
K_NC = [(Ni, Cj) for Ni in Nodes['N'].keys() for Cj in Nodes['C'].keys()]
K_T = [(x, no) for x in data_dict.keys() for no in range(data_dict[x][2])]
K_PATH = [(x, no, node) for x, no in K_T for node in range(10)]  # ('C',0,0)
K_INDIC = [(x, no, node, Pi, Nj) for x, no, node in K_PATH for Pi, Nj in K_PN]  # ('C',0,0)


D_PN = {(node2num(Pi), node2num(Nj)): np.hypot(Nodes['P'][Pi][0] - Nodes['N'][Nj][0], Nodes['P'][Pi][1] - Nodes['N'][Nj][1]) for Pi, Nj in K_PN}
D_NC = {(node2num(Ni), node2num(Cj)): np.hypot(Nodes['N'][Ni][0] - Nodes['C'][Cj][0], Nodes['N'][Ni][1] - Nodes['C'][Cj][1]) for Ni, Cj in K_NC}
D_PP = {(node2num(Pi), node2num(Nj)): 100000 for Pi in K_P for Nj in K_P}
D_NN = {(node2num(Pi), node2num(Nj)): 100000 for Pi in K_N for Nj in K_N}
D_CC = {(node2num(Pi), node2num(Nj)): 100000 for Pi in K_C for Nj in K_C}
D_PN.update(D_NC)
D_PN.update(D_PP)
D_PN.update(D_NN)
D_PN.update(D_CC)

P = model.addVars(K_P, vtype=GRB.INTEGER)  # 车走过的路线
PATH_T = model.addVars(K_PATH, vtype=GRB.INTEGER)  # 车走过的路线
NOW_PN = model.addVars(K_PN, vtype=GRB.INTEGER)  # 该条路的运量
NOW_NC = model.addVars(K_NC, vtype=GRB.INTEGER)  # 该条路的运量
INDIC_PATH = model.addVars(K_INDIC, vtype=GRB.BINARY)

model.addConstrs(P[j] >= P[i] for i in K_P for j in K_P)

MAX_PN = model.addVars(K_PN, vtype=GRB.INTEGER)  # 经过这条路的车的最大运量
MAX_NC = model.addVars(K_NC, vtype=GRB.INTEGER)  # 经过这条路的车的最大运量

# 对路线的约束
model.addConstrs(Nodes['P'][Pi][2] >= quicksum(NOW_PN[Pi, Nj] for Nj in K_N) for Pi in K_P)  # P层节点的所有出路的运量<生产量
model.addConstrs(quicksum(NOW_PN[Pl, Ni] for Pl in K_P) == quicksum(NOW_NC[Ni, Cj] for Cj in K_C) for Ni in K_N)  # N层节点的所有入路的运量=N层节点的所有出路的运量
model.addConstrs(quicksum(NOW_NC[Ni, Cj] for Ni in K_N) == Nodes['C'][Cj][2] for Cj in K_C)  # C层节点的所有入路的运量=消耗量

# 经过这条路的车的最大运量（次数*容量）和>这条路的运量100 200
# model.update()

# 对于第条Pi，Nj路的约束
for Pi, Nj in K_PN:
    for x, no, i in K_PATH:
        model.addConstr((PATH_T[x, no, i] - node2num(Pi))**2 <= INDIC_PATH[x, no, i, Pi, Nj]*100000000+0.000000001)
        model.addConstr((PATH_T[x, no, i] - node2num(Pi))**2 >= INDIC_PATH[x, no, i, Pi, Nj]-1+0.01)
        if i+1!=10:
            model.addConstr((PATH_T[x, no, i+1] - node2num(Nj))**2 <= INDIC_PATH[x, no, i, Pi, Nj]*100000000+0.000000001)
            model.addConstr((PATH_T[x, no, i+1] - node2num(Nj))**2 >= INDIC_PATH[x, no, i, Pi, Nj]-1+0.01)


#每条路线的最大运量大于理想运量
model.addConstrs(quicksum((1-INDIC_PATH[x, no, i, Pi, Nj])*data_dict[x][0] for x, no, i in K_PATH) >= NOW_PN[Pi, Nj] for Pi,Nj in K_PN)
# 每辆车的路线里程和<=500——要记录每辆车的路线（必须首尾相连）
model.addConstrs(quicksum((1-INDIC_PATH[x, no, i, Pi, Nj])*1 for i in range(9) for Pi,Nj in K_PN) <= 500 for x, no in K_T)



# model.addConstrs(quicksum(count_path([PATH_T[x, no, i] for i in range(len(K_PATH) // len(K_T))], node2num(Pi), node2num(Nj)) * data_dict[x][0] for x, no in K_T) - NOW_PN[Pi, Nj] >= 0 for Pi, Nj in K_PN)
# model.addConstrs(quicksum(count_path([PATH_T[x, no, i] for i in range(len(K_PATH)//len(K_T))], node2num(Pi),node2num(Nj)) * data_dict[x][0] for x, no in K_T) >= NOW_PN[Pi, Nj] for Pi, Nj in K_PN)
# model.addConstrs(quicksum(count_path([PATH_T[x, no, i] for i in range(len(K_PATH) // len(K_T))], node2num(Ni), node2num(Cj)) * data_dict[x][0] for x, no in K_T) >= NOW_NC[Ni, Cj] for Ni, Cj in K_NC)


model.modelSense = GRB.MINIMIZE  # 目标为最小化
model.setObjective(quicksum(quicksum(quicksum((1-INDIC_PATH[x, no, i, Pi, Nj])*D_PN[Pi,Nj] for i in range(9)) for Pi,Nj in K_PN) * data_dict[x][1] for x, no in K_T))  # 目标函数为车的路线里程和*每公里价格

model.optimize()  # 优化

# 最小化车经过的节点数
# 最小化实际和理论之差