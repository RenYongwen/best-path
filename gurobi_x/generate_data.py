import random
from dbutil import DBHelp
import sqlite3
from gdmap import get_mappath

print('Starting the create database operation')
print('------------------------------------')
conn = sqlite3.connect("sqlite.db")
print('create database...')
cur = conn.cursor()
print('create user table...')
cur.execute('''
DROP TABLE IF EXISTS "节点";
''')
cur.execute('''
CREATE TABLE "节点" (
	"节点ID" INTEGER,
	"节点类型" INTEGER,
	"单位时间需求" INTEGER,
	"单位时间产量" INTEGER,
	PRIMARY KEY ("节点ID")
);
''')
cur.execute('''
DROP TABLE IF EXISTS "路线";
''')
cur.execute('''
CREATE TABLE "路线" (
	"路线ID" INTEGER,
	"出发节点ID" INTEGER,
	"到达节点ID" INTEGER,
	"路程" INTEGER,
	PRIMARY KEY ("路线ID"),
	CONSTRAINT "出发节点" FOREIGN KEY ("出发节点ID") REFERENCES "节点" ("节点ID") ON DELETE NO ACTION ON UPDATE NO ACTION,
	CONSTRAINT "到达节点" FOREIGN KEY ("到达节点ID") REFERENCES "节点" ("节点ID") ON DELETE NO ACTION ON UPDATE NO ACTION
);
''')
cur.execute('''
DROP TABLE IF EXISTS "车型";
''')
cur.execute('''
CREATE TABLE "车型" (
	"车型ID" INTEGER,
	"可装数量" INTEGER,
	"单位运价" INTEGER,
	"装卸货时长" REAL,
	PRIMARY KEY ("车型ID")
);
''')
cur.execute('''
DROP TABLE IF EXISTS "车辆";
''')
cur.execute('''
CREATE TABLE "车辆" (
	"车辆ID" INTEGER,
	"车型ID" INTEGER,
	PRIMARY KEY ("车辆ID"),
	CONSTRAINT "车型" FOREIGN KEY ("车型ID") REFERENCES "车型" ("车型ID") ON DELETE NO ACTION ON UPDATE NO ACTION
);
''')
print('user table created done.')
print('------------------------------------')

print('operate done.')
print('create database successful.')


print('Is insert some sample data into the database?')
print('1. insert')
print('2. exit')
insert_tag = input('please select the option:')
if insert_tag == '1':

    random.seed(1)  # 随机种子，如有本行，则程序每次运行结果一样。可任意赋值

    Nodes = []
    Nodes.extend([(i, 0, 0, random.choice([4000, 5000, 6000])) for i in range(3)])  # Producer
    Nodes.extend([(i, 1, 0, 0) for i in range(3, 8)])
    Nodes.extend([(i, 2, random.randint(40, 50), 0) for i in range(8, 465)])

    Paths = []
    for Ni in Nodes:
        for Nj in Nodes:
            if Ni[0] == Nj[0]:
                Paths.append((len(Paths), Ni[0], Nj[0], 0))
            elif Ni[1] - Nj[1] == 1:
                Paths.append((len(Paths), Ni[0], Nj[0], random.randint(20,40)))
                Paths.append((len(Paths), Nj[0], Ni[0], random.randint(20,40)))

    CarTypes = []
    CarTypes.append([0, 40, 50, 1])
    CarTypes.append([1, 30, 30, 0.5])
    CarTypes.append([2, 20, 20, 0.2])

    Cars = []
    Cars.extend([(i, 0) for i in range(100)])
    Cars.extend([(i, 1) for i in range(100, 300)])
    Cars.extend([(i, 2) for i in range(300, 500)])

    db = DBHelp()
    for Node in Nodes:
        db.add_super(table_name="节点", data=Node)
    for Path in Paths:
        db.add_super(table_name="路线", data=Path)
    for CarType in CarTypes:
        db.add_super(table_name="车型", data=CarType)
    for Car in Cars:
        db.add_super(table_name="车辆", data=Car)
    db.db_commit()
    db.instance = None
    del db

    print('insert operation done.')
    print('------------------------------------')
else:
    print('system exit.')
