"""
@Time    : 2020/5/11 14:24
@Author  : weijiang
@Site    : 
@File    : 数据库操作.py
@Software: PyCharm
"""
import sqlite3

print('Starting the create database operation')
print('------------------------------------')
conn = sqlite3.connect("staff.db")
print('create database...')
cur = conn.cursor()
print('create user table...')
cur.execute('''CREATE TABLE IF NOT EXISTS user (
            id varchar(50) PRIMARY KEY,
            username varchar(255),
            password varchar(255),
            department varchar(255),
            position varchar(255),
            position_salary varchar(255),
            grade_salary int(11),
            retained_allowance int(11),
            border_allowance int(11),
            hardship_allowance int(11),
            intellectual_allowance int(11),
            technical_allowance int(11),
            seniority_allowance int(11),
            base_salary_subtotal int(11),
            position_performance int(11),
            incentive_performance int(11),
            performance_salary_subtotal int(11), 
            total_payable_salary int(11), 
            endowment_insurance int(11),
            medical_insurance int(11),
            unemployment_insurance int(11),
            pension int(11),
            housing_fund int(11),
            personal_income_tax int(11),
            other int(11),
            actual_salary_paid int(11), 
            remarks varchar(255));''')
print('user table created done.')
print('------------------------------------')

print('operate done.')
print('create database successful.')


# print('Is insert some sample data into the database?')
# print('1. insert')
# print('2. exit')
# insert_tag = input('please select the option:')
# if insert_tag == '1':
#     print('------------------------------------')
#     print('starting the insert data operation...')
#     admin_data = ['12644064935811ea9063d8c497639e37', 'admin', '21232f297a57a5a743894a0e4a801fc3', 0,
#                   '2020-05-11 15:23:12', 0, '2020-05-11 15:24:23']
#     user_data = ['99477a9e935811ea8171d8c497639e37', 'zhangsan', 'e10adc3949ba59abbe56e057f20f883e', 1,
#                  '2020-05-11 15:23:12', 0, '2020-05-11 15:24:23']
#     sql = 'insert into user (id, username, password, role, create_time, delete_flag, current_login_time) values(%s,%s,'\
#           '%s,%s,%s,%s,%s)'
#     cur.execute(sql, admin_data)
#     cur.execute(sql, user_data)
#     conn.commit()
#     cur.close()
#     conn.close()
#     print('insert operation done.')
#     print('------------------------------------')
#     print('Now you can use admin account login with username="admin" password="admin" or use the normal account login'
#           'with username="zhangsan" password="123456".')
# else:
#     print('system exit.')
