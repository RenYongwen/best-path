"""
coding:utf-8
file: dbutil.py
@author: jiangwei
@contact: jiangwei_1994124@163.com
@time: 2020/5/9 20:03
@desc:
"""
import sqlite3,frozen_dir,os
import pandas as pd

class DBHelp:
    instance = None

    def __init__(self):
        self._conn = sqlite3.connect(frozen_dir.app_path()+"/util/staff.db")
        self._cur = self._conn.cursor()

    @classmethod
    def get_instance(cls):
        if cls.instance:
            return cls.instance
        else:
            cls.instance = DBHelp()
            return cls.instance

    def query_all(self, table_name):
        sql = 'select * from {}'.format(table_name)
        self._cur.execute(sql)
        res = self._cur.fetchall()
        return len(res), res

    def query_super(self, table_name, column_names, conditions):
        sql = "select * from {} where ".format(table_name)
        for i in range(len(column_names)):
            if i ==0:
                sql += "{} = '{}'".format(column_names[i],conditions[i])
            else:
                sql += "and {} = '{}'".format(column_names[i],conditions[i])
        self._cur.execute(sql)
        res = self._cur.fetchall()
        return len(res), res
    
    def add_user(self, data):
        sql = "insert into 系统用户表 (账号,密码) values (?,?)"
        self._cur.execute(sql,data)

    def add_super(self, table_name, data):
        sql = "PRAGMA table_info({})".format(table_name)
        self._cur.execute(sql)
        columns = self._cur.fetchall()
        # 构造列名列表和列类型字典
        column_names = []
        column_types = {}
        for column in columns:
            column_names.append(column[1])
            if column[2] == 'INTEGER':
                column_types[column[1]] = int
            elif column[2] == 'REAL':
                column_types[column[1]] = float
            else:
                column_types[column[1]] = str

        # 自动识别字段类型并进行转换
        for i in range(len(data)):
            if column_names[i] in column_types:
                data[i] = column_types[column_names[i]](data[i])
        sql = "insert into "+table_name+ " values ("+ ','.join(['?']*len(column_names)) +")"
        self._cur.execute(sql,data)

    def update_super(self, table_name, column_names, conditions, data):
        self.delete_super(table_name,column_names,conditions)
        self.add_super(table_name,data)

    def delete_super(self, table_name, column_names, conditions):
        sql = "delete from {} where ".format(table_name)
        for i in range(len(column_names)):
            if i ==0:
                sql += "{} = '{}'".format(column_names[i],conditions[i])
            else:
                sql += "and {} = '{}'".format(column_names[i],conditions[i])
        print(sql)
        self._cur.execute(sql)

    def get_header(self,table_name):
        sql = "PRAGMA table_info({})".format(table_name)
        self._cur.execute(sql)
        columns = self._cur.fetchall()
        # 构造列名列表和列类型字典
        column_names = []
        for column in columns:
            column_names.append(column[1])
        return column_names

    def get_primary_key(self,table_name):
        sql = "SELECT name FROM pragma_table_info('{}') WHERE pk != 0;".format(table_name)
        self._cur.execute(sql)
        columns = self._cur.fetchall()
        return [item[0] for item in columns]

    def import_to_sql(self, file_name, table_name):
        try:
            column_names = self.get_header(table_name)
            self._cur.execute(f"DELETE FROM {table_name}")
            df = pd.read_excel(file_name)
            if df.columns.tolist()!=column_names:
                return False
            df.to_sql(table_name, self._conn, if_exists='replace',index=False)
            return True
        except Exception as e:
            return False


    def export_to_excel(self, table_name, file_name):
        try:
            query = "select * from {}".format(table_name)
            df = pd.read_sql_query(query, self._conn)
            df.to_excel(file_name, index=False)
            return True
        except Exception as e:
            return False

    def db_commit(self):
        self._conn.commit()

    def db_rollback(self):
        self._conn.rollback()
