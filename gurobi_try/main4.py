import numpy as np
import random
from gurobipy import Model, GRB, quicksum


random.seed(1)  # 随机种子，如有本行，则程序每次运行结果一样。可任意赋值

Nodes = {
    'P': {i: random.randint(500, 1000) for i in range(5)},  # 供给方Pi（X，Y，供水量）
    'N': {i + 5: 0 for i in range(10)},  # 中转站Ni（X，Y）
    'C': {i + 15: random.randint(50, 100) for i in range(500)},  # 需求方Ci（X，Y，耗水量）
    'T': {i: (50, 4) for i in range(500)}
}
max_time = 10
max_distance = 500

model = Model('TRY')
K_P = [Pi for Pi in Nodes['P'].keys()]
K_N = [Ni for Ni in Nodes['N'].keys()]
K_C = [Ci for Ci in Nodes['C'].keys()]
K_T = [Ti for Ti in Nodes['T'].keys()]

K_PN = [(i, j) for i in K_P for j in K_N]
K_NC = [(i, j) for i in K_N for j in K_C]

D = {}
for i in K_P + K_N + K_C:
    for j in K_P + K_N + K_C:
        if i == j:
            D[i, j] = 0
        elif i in K_N and j in K_P:
            D[i, j] = random.randint(10, 50)
        elif i in K_P and j in K_N:
            D[i, j] = random.randint(10, 50)
        elif i in K_N and j in K_C:
            D[i, j] = random.randint(10, 50)
        elif i in K_C and j in K_N:
            D[i, j] = random.randint(10, 50)

K_D = [(i, j) for i, j in D.keys()]

INDIC_D = model.addVars(K_D, vtype=GRB.BINARY)  # 车是否走过该路
GOAL_D = model.addVars(K_D, lb=0, vtype=GRB.INTEGER)  # 该路线的目标运量

# 每条路线的目标运量必须满足实际条件
model.addConstrs(Nodes['P'][i] >= quicksum(INDIC_D[i, j] * GOAL_D[i, j] for j in K_N) for i in K_P)  # P层节点的所有出路的运量<生产量
model.addConstrs(quicksum(INDIC_D[i, j] * GOAL_D[l, i] for l in K_P) == quicksum(INDIC_D[i, j] * GOAL_D[i, j] for j in K_C) for i in K_N)  # N层节点的所有入路的运量=N层节点的所有出路的运量
model.addConstrs(quicksum(INDIC_D[i, j] * GOAL_D[i, j] for i in K_N) == Nodes['C'][j] for j in K_C)  # C层节点的所有入路的运量=消耗量

model.modelSense = GRB.MINIMIZE  # 目标为最小化
model.setObjective(quicksum(INDIC_D[i, j] * D[i, j] for i, j in K_D))  # 目标函数为车的路线里程和*每公里价格
model.optimize()  # 优化

K_TRUCK = {}
if model.status == GRB.Status.OPTIMAL or model.status == GRB.Status.TIME_LIMIT:
    for i, j in K_D:
        if INDIC_D[i, j].x == 1:
            K_TRUCK[i, j] = GOAL_D[i, j]
else:
    print("no solution")

K_X = [(x, t, i, j) for x in K_T for t in range(max_time) for i, j in K_TRUCK.keys()]  # 80*10*(745)
INDIC_X = model.addVars(K_X, vtype=GRB.BINARY)  # 车是否走过该路

# 每条路线的最大运量必须大于目标运量
model.addConstrs(quicksum(INDIC_X[x, t, i, j] * Nodes['T'][x][0] for x in K_T for t in range(max_time)) >= GOAL_D[i, j] for i, j in K_TRUCK.keys())

# 每辆车每个时刻只能走一条路线
model.addConstrs(quicksum(INDIC_X[x, t, i, j] for i, j in K_TRUCK.keys()) == 1 for x in K_T for t in range(max_time))

# 每辆车的路线里程和<=max_distance
model.addConstrs(quicksum(INDIC_X[x, t, i, j] for t in range(max_time) for i, j in K_TRUCK.keys()) <= max_distance for x in K_T)

# 每辆车的路线必须首尾相连
model.addConstrs(quicksum(INDIC_X[x, t, i, k] for i in K_P+K_N+K_C if (i,k) in K_TRUCK.keys()) == quicksum(INDIC_X[x, (t + 1) % max_time, k, j] for j in K_P+K_N+K_C if (k,j) in K_TRUCK.keys()) for x in K_T for t in range(max_time) for k in K_P + K_N + K_C)


model.modelSense = GRB.MINIMIZE  # 目标为最小化
model.setObjective(quicksum(INDIC_X[x, t, i, j] for x in K_T for t in range(max_time) for i, j in K_TRUCK.keys()))  # 目标函数为车的路线里程和*每公里价格
model.optimize()  # 优化

if model.status == GRB.Status.OPTIMAL or model.status == GRB.Status.TIME_LIMIT:
    for x, t, i, j in K_X:
        if INDIC_X[x, t, i, j].x == 1:
            print("{},{},{},{}".format(x, t, i, j))
else:
    print("no solution")
