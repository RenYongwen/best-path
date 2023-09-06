import random
from gurobipy import Model, GRB, quicksum

random.seed(1)  # 随机种子，如有本行，则程序每次运行结果一样。可任意赋值

Nodes = {
    'S': {i: 9000 for i in range(3)},  # 供给方Pi（X，Y，供水量）
    'N': {i + 3: 0 for i in range(5)},  # 中转站Ni（X，Y）
    'C': {i + 8: random.randint(40, 60) for i in range(280)},  # 需求方Ci（X，Y，耗水量）
    'X': {i: (200, 4) for i in range(400)}
}
max_time = 10
max_distance = 500

model = Model('TRY')
K_S = [Si for Si in Nodes['S'].keys()]
K_N = [Ni for Ni in Nodes['N'].keys()]
K_C = [Ci for Ci in Nodes['C'].keys()]

K_SN = [(i, j) for i in K_S for j in K_N]
K_NC = [(i, j) for i in K_N for j in K_C]

D = {}
for i in K_S + K_N + K_C:
    for j in K_S + K_N + K_C:
        if i == j:
            D[i, j] = 0
        elif i in K_S and j in K_N:
            D[i, j] = D[j, i] = random.randint(10, 50)
        elif i in K_N and j in K_C:
            D[i, j] = D[j, i] = random.randint(10, 50)

K_SNC = K_SN + K_NC
INDIC_SNC = model.addVars(K_SNC, vtype=GRB.BINARY)  # 车是否走过该路
GOAL_SNC = model.addVars(K_SNC, lb=0, vtype=GRB.INTEGER)  # 该路线的目标运量

# 每条路线的目标运量必须满足实际条件
model.addConstrs(Nodes['S'][i] >= quicksum(INDIC_SNC[i, j] * GOAL_SNC[i, j] for j in K_N) for i in K_S)  # P层节点的所有出路的运量<生产量
model.addConstrs(quicksum(INDIC_SNC[l, i] * GOAL_SNC[l, i] for l in K_S) == quicksum(INDIC_SNC[i, j] * GOAL_SNC[i, j] for j in K_C) for i in K_N)  # N层节点的所有入路的运量=N层节点的所有出路的运量
model.addConstrs(quicksum(INDIC_SNC[i, j] * GOAL_SNC[i, j] for i in K_N) == Nodes['C'][j] for j in K_C)  # C层节点的所有入路的运量=消耗量

model.modelSense = GRB.MINIMIZE  # 目标为最小化
model.setObjective(quicksum(INDIC_SNC[i, j] * D[i, j] for i, j in K_SNC))  # 目标函数为车的路线里程和*每公里价格
model.optimize()  # 优化


PATHS = []
if model.status == GRB.Status.OPTIMAL or model.status == GRB.Status.TIME_LIMIT:
    for i, j in K_SNC:
        if INDIC_SNC[i, j].x == 1:
            PATHS.append((i, j))
            PATHS.append((j, i))
            PATHS.append((i, i))
            PATHS.append((j, j))
else:
    print("no solution")
PATHS = list(set(PATHS))

K_X = [i for i in Nodes['X'].keys()]
K_T = [i for i in range(max_time)]
K_P = [i for i in range(len(PATHS))]
K_XT = [(x, t) for x in K_X for t in K_T]
K_XI = [(x, i) for x in K_X for i in K_S + K_N + K_C]
K_TP = [(t, p) for t in K_T for p in K_P]
K_XP = [(x, p) for x in K_X for p in K_P]
K_XTP = [(x, t, p) for x in K_X for t in K_T for p in K_P]  # 500*6*1535
INDIC_XTP = model.addVars(K_XTP, vtype=GRB.BINARY)  # 车X在时刻T是否走过P路

# 表示可能出现的连续路
CONNS = [(p1, p2) for p1 in K_P for p2 in K_P if PATHS[p1][1] == PATHS[p2][0]]
print(len(PATHS), len(CONNS))



# 每条需求路线的最大运量必须大于目标运量
model.addConstrs(quicksum(INDIC_XTP[x, t, p] * Nodes['X'][x][0] for x, t in K_XT) >= GOAL_SNC[PATHS[p]].x for p in K_P if PATHS[p][0] < PATHS[p][1])

# 每辆车的路线里程和<=max_distance
model.addConstrs(quicksum(INDIC_XTP[x, t, p] * D[PATHS[p]] for t, p in K_TP) <= max_distance for x in K_X)

# 每辆车每个时刻在一条路线
model.addConstrs(quicksum(INDIC_XTP[x, t, p] for p in K_P) == 1 for x, t in K_XT)

# 每辆车的路线必须首尾相连（每个节点出等于入）
model.addConstrs(quicksum(INDIC_XTP[x, t, p] for t, p in K_TP if PATHS[p][0] == i) == quicksum(INDIC_XTP[x, t, p] for t, p in K_TP if PATHS[p][1] == i) for x,i in K_XI)

model.modelSense = GRB.MINIMIZE  # 目标为最小化
model.setObjective(quicksum(INDIC_XTP[x, t, p] * Nodes['X'][x][1] for x, t, p in K_XTP))  # 目标函数为车的路线里程和*每公里价格
model.optimize()  # 优化


PathVTCount = {}

if model.status == GRB.Status.OPTIMAL or model.status == GRB.Status.TIME_LIMIT:
    for v, t, p in K_XTP:
        if INDIC_XTP[v, t, p].x == 1:
            if (PATHS[p]) in PathVTCount.keys():
                PathVTCount[PATHS[p]] += 1
            else:
                PathVTCount[PATHS[p]] = 1
else:
    print("no solution")

print(PathVTCount)

a = quicksum(PathVTCount[i,j] if i!=j else 0 for i,j in PathVTCount.keys())
b = quicksum(PathVTCount[i,j] if i==j else 0 for i,j in PathVTCount.keys())
print(a,b)