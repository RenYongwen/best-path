import random
from gurobipy import Model, GRB, quicksum


random.seed(1)  # 随机种子，如有本行，则程序每次运行结果一样。可任意赋值

Trucks = {'A': (100, 3, 5), 'B': (80, 2, 10), 'C': (50, 1, 15)}  # (载重，每公里价格，车数量)默认每辆车每天可跑500km
Nodes = {
    'P': {i: random.randint(5000, 10000) for i in range(5)},  # 供给方Pi（X，Y，供水量）
    'N': {i + 5: 0 for i in range(10)},  # 中转站Ni（X，Y）
    'C': {i + 15: random.randint(100, 200) for i in range(20)},  # 需求方Ci（X，Y，耗水量）
}
max_time = 10
max_distance = 500
# 10-20-20 5-10-100 10 58550参数0.19s
# 10-20-20 5-10-200 10 109550参数0.38s
# 10-20-200 5-10-200 10 496550参数2.3s
# 100-200-200 5-10-200 10 1077050参数6.54s
# 100-200-200 5-10-400 10 2079050参数15s

model = Model('TRY')
K_P = [Pi for Pi in Nodes['P'].keys()]
K_N = [Ni for Ni in Nodes['N'].keys()]
K_C = [Ci for Ci in Nodes['C'].keys()]
K_T = [(x, no) for x in Trucks.keys() for no in range(Trucks[x][2])]
K_PN = [(i, j) for i in K_P for j in K_N]
K_NC = [(i, j) for i in K_N for j in K_C]
D = {}
for i in K_P + K_N + K_C:
    for j in K_P + K_N + K_C:
        if i == j:
            D[i, j] = 0
        elif i in K_N and j in K_P:
            D[i, j] = random.randint(10, 40)
        elif i in K_P and j in K_N:
            D[i, j] = random.randint(10, 40)
        elif i in K_N and j in K_C:
            D[i, j] = random.randint(10, 40)
        elif i in K_C and j in K_N:
            D[i, j] = random.randint(10, 40)

K_D = [(i, j) for i, j in D.keys()]
K_INDIC = [(x, no, t, node) for x, no in K_T for t in range(max_time) for node in K_P + K_N + K_C]  # (x,no,t)所在的点
INDIC = model.addVars(K_INDIC, vtype=GRB.BINARY)  # 车是否走过该路
GOAL = model.addVars(K_PN + K_NC, lb=0, vtype=GRB.INTEGER)  # 该路线的目标运量

# 每条路线的目标运量必须满足实际条件
model.addConstrs(Nodes['P'][i] >= quicksum(GOAL[i, j] for j in K_N) for i in K_P)  # P层节点的所有出路的运量<生产量
model.addConstrs(quicksum(GOAL[l, i] for l in K_P) == quicksum(GOAL[i, j] for j in K_C) for i in K_N)  # N层节点的所有入路的运量=N层节点的所有出路的运量
model.addConstrs(quicksum(GOAL[i, j] for i in K_N) == Nodes['C'][j] for j in K_C)  # C层节点的所有入路的运量=消耗量

# 每条路线的最大运量必须大于目标运量
model.addConstrs(quicksum(INDIC[x, no, t, i] * INDIC[x, no, t + 1, j] * Trucks[x][0] for x, no in K_T for t in range(max_time - 1)) >= GOAL[i, j] for i, j in K_PN + K_NC)

# 每辆车每个时刻在一个节点
model.addConstrs(quicksum(INDIC[x, no, t, i] for i in K_P + K_N + K_C) == 1 for x, no in K_T for t in range(max_time))

# 每辆车的路线里程和<=max_distance
model.addConstrs(quicksum(INDIC[x, no, t, i] * INDIC[x, no, t + 1, j] * D[i, j] for t in range(max_time - 1) for i, j in K_D) <= max_distance for x, no in K_T)

# 每辆车的路线必须首尾相连
model.addConstrs(quicksum(INDIC[x, no, 0, i] * INDIC[x, no, max_time - 1, i] for i in K_P + K_N + K_C) == 1 for x, no in K_T)

model.modelSense = GRB.MINIMIZE  # 目标为最小化
model.setObjective(quicksum(INDIC[x, no, t, i] * INDIC[x, no, t + 1, j] * D[i, j] * Trucks[x][1] for x, no in K_T for t in range(max_time - 1) for i, j in K_D))  # 目标函数为车的路线里程和*每公里价格
model.optimize()  # 优化

if model.status == GRB.Status.OPTIMAL or model.status == GRB.Status.TIME_LIMIT:
    for x, no in K_T:
        print("{}{}:{}".format(x, no, quicksum(INDIC[x, no, 0, i] * INDIC[x, no, max_time - 1, i] for i in K_P + K_N + K_C)))
else:
    print("no solution")

# 最小化车经过的节点数
# 最小化实际和理论之差
