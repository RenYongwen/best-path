import random
from gurobipy import Model, GRB, quicksum
from dbutil import DBHelp

db = DBHelp()
NodesS = db.query_super(table_name="节点", column_names=["节点类型"], conditions=[0])  # 供给方Pi（X，Y，供水量）
NodesN = db.query_super(table_name="节点", column_names=["节点类型"], conditions=[1])  # 中转站Ni（X，Y）
NodesC = db.query_super(table_name="节点", column_names=["节点类型"], conditions=[2])
Paths = db.query_all(table_name="路线")
CarTypes = db.query_all(table_name="车型")
Cars = db.query_all(table_name="车辆")
db.db_commit()
db.instance = None
del db

Dict = {
    'S': {NS[0]: NS[3] for NS in NodesS},  # 供给方Pi（X，Y，供水量）
    'C': {NC[0]: NC[2] for NC in NodesC},  # 需求方Ci（X，Y，耗水量）
    'X': {Car[0]: CarTypes[Car[1]] for Car in Cars}
}

D = {}
for Path in Paths:
    D[Path[1], Path[2]] = Path[3]


max_time = 10
max_distance = 500

# 创建模型，添加变量该路是否经过及运量
model = Model('TRY')
K_S = [NS[0] for NS in NodesS]
K_N = [NN[0] for NN in NodesN]
K_C = [NC[0] for NC in NodesC]
K_SN = [(i, j) for i in K_S for j in K_N]
K_NC = [(i, j) for i in K_N for j in K_C]
K_SNC = K_SN + K_NC
INDIC_SNC = model.addVars(K_SNC, vtype=GRB.BINARY)  # 车是否走过该路
GOAL_SNC = model.addVars(K_SNC, lb=0, vtype=GRB.INTEGER)  # 该路线的目标运量

# 每条路线的目标运量必须满足实际条件
model.addConstrs(Dict['S'][i] >= quicksum(INDIC_SNC[i, j] * GOAL_SNC[i, j] for j in K_N) for i in K_S)  # P层节点的所有出路的运量<生产量
model.addConstrs(quicksum(INDIC_SNC[l, i] * GOAL_SNC[l, i] for l in K_S) == quicksum(INDIC_SNC[i, j] * GOAL_SNC[i, j] for j in K_C) for i in K_N)  # N层节点的所有入路的运量=N层节点的所有出路的运量
model.addConstrs(quicksum(INDIC_SNC[i, j] * GOAL_SNC[i, j] for i in K_N) == Dict['C'][j] for j in K_C)  # C层节点的所有入路的运量=消耗量

# 最短路径的目标函数设置
model.modelSense = GRB.MINIMIZE
model.setObjective(quicksum(INDIC_SNC[i, j] * D[i, j] for i, j in K_SNC))
model.optimize()

# 将经过的路打包到PATHS中
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

# 添加变量
K_X = [i for i in Dict['X'].keys()]
K_T = [i for i in range(max_time)]
K_P = [i for i in range(len(PATHS))]
K_XI = [(x, i) for x in K_X for i in K_S + K_N + K_C]
K_XT = [(x, t) for x in K_X for t in K_T]
K_TP = [(t, p) for t in K_T for p in K_P]
K_XP = [(x, p) for x in K_X for p in K_P]
K_XTP = [(x, t, p) for x in K_X for t in K_T for p in K_P]  # 500*6*1535
INDIC_XTP = model.addVars(K_XTP, vtype=GRB.BINARY)  # 车X在时刻T是否走过P路

# 表示可能出现的连续路
CONNS = [(p1, p2) for p1 in K_P for p2 in K_P if PATHS[p1][1] == PATHS[p2][0]]
print(len(PATHS), len(CONNS))

# 每条需求路线的最大运量必须大于目标运量
model.addConstrs(quicksum(INDIC_XTP[x, t, p] * Dict['X'][x][1] for x, t in K_XT) >= GOAL_SNC[PATHS[p]].x for p in K_P if PATHS[p][0] < PATHS[p][1])

# 每辆车的路线里程和<=max_distance
model.addConstrs(quicksum(INDIC_XTP[x, t, p] * D[PATHS[p]] for t, p in K_TP) <= max_distance for x in K_X)

# 每辆车每个时刻在一条路线
model.addConstrs(quicksum(INDIC_XTP[x, t, p] for p in K_P) == 1 for x, t in K_XT)

# 每辆车的路线必须首尾相连（每个节点出等于入）
model.addConstrs(quicksum(INDIC_XTP[x, t, p] for t, p in K_TP if PATHS[p][0] == i) == quicksum(INDIC_XTP[x, t, p] for t, p in K_TP if PATHS[p][1] == i) for x, i in K_XI)

model.modelSense = GRB.MINIMIZE  # 目标为最小化
model.setObjective(quicksum(INDIC_XTP[x, t, p] * Dict['X'][x][2] + Dict['X'][x][3] if D[PATHS[p]]==0 else 0 for x, t, p in K_XTP))  # 目标函数为车的路线里程和*每公里价格
model.optimize()  # 优化

if model.status == GRB.Status.OPTIMAL or model.status == GRB.Status.TIME_LIMIT:
    for x, t, p in K_XTP:
        if INDIC_XTP[x, t, p].x == 1:
            print("{},{},{}".format(x, t, PATHS[p]))
else:
    print("no solution")
