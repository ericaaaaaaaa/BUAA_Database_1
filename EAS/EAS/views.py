# -*- coding:utf-8 -*-
import pymysql
from django.http import JsonResponse
from django.shortcuts import render, redirect
import json

# 打开数据库连接
db = pymysql.connect(host="localhost", port=3306, user="root",
                     password="root", database="eas", charset="utf8")

# 使用cursor()方法获取操作游标
cursor = db.cursor()

# 使用预处理语句创建表
# 学生(学号 密码)
sql1 = '''
CREATE TABLE IF NOT EXISTS student (
stuId varchar(50),
password varchar(50) NOT NULL,
primary key (stuId)
)ENGINE=innodb DEFAULT CHARSET=utf8;
'''

# 教师(工号 密码)
sql2 = '''
CREATE TABLE IF NOT EXISTS teacher (
teaId varchar(50),
password varchar(50) NOT NULL,
primary key (teaId)
)ENGINE=innodb DEFAULT CHARSET=utf8;
'''

# 课程(课程编号 课程名称 授课教师 容量)
sql3 = '''
CREATE TABLE IF NOT EXISTS course (
courseId int NOT NULL AUTO_INCREMENT,
courseName varchar(50),
teaId varchar(50),
capacity int,
primary key (courseId)
)ENGINE=innodb DEFAULT CHARSET=utf8;
'''

# 选课情况(课程编号 学号)
sql4 = '''
CREATE TABLE IF NOT EXISTS course_selection (
courseId int,
stuId varchar(50),
primary key (courseId,stuId)
)ENGINE=innodb DEFAULT CHARSET=utf8;
'''

cursor.execute(sql1)
cursor.execute(sql2)
cursor.execute(sql3)
cursor.execute(sql4)

currUserId = ''
salt = "xxxxxx"


# 学生注册
def stuRegister(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        stuId = data['studentId']
        password = data['studentPwd']
        sql = f'''
        insert into student (stuId,password)
        values ("{stuId}", "{password}");
        '''
        cursor.execute(sql)
        db.commit()
        print("学生注册成功")
        return JsonResponse({
            "data": {
            },
            "status": 0,
            "statusInfo": {
                "message": "注册成功",
                "detail": ""
            }
        })
    else:
        print("学生注册失败")
        return JsonResponse({
            "data": {
            },
            "status": 1,
            "statusInfo": {
                "message": "注册失败",
                "detail": ""
            }
        })


# 教师注册
def teaRegister(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        teaId = data['teacherId']
        password = data['teacherPwd']
        sql = f'''
        insert into teacher (teaId,password)
        values ("{teaId}", "{password}");
        '''
        cursor.execute(sql)
        db.commit()
        print("教师注册成功")
        return JsonResponse({
            "data": {
            },
            "status": 0,
            "statusInfo": {
                "message": "注册成功",
                "detail": ""
            }
        })
    else:
        print("教师注册失败")
        return JsonResponse({
            "data": {
            },
            "status": 1,
            "statusInfo": {
                "message": "注册失败",
                "detail": ""
            }
        })


import jwt
import datetime


# 学生登陆
def stuLogin(request):
    if request.method == 'GET':
        request.encoding = "utf-8"
        stuId = request.GET['studentId']
        password = request.GET['studentPwd']
        print("stuId " + stuId)
        print("stuPwd " + password)
        sql = f'''
        select password from student where stuId="{stuId}";
        '''
        cursor.execute(sql)
        db.commit()
        results = cursor.fetchall()
        status = 0 if len(results) == 1 and results[0][0] == password else 1
        message = "登陆成功" if status == 0 else "密码错误"
        message = "用户未注册" if len(results) != 1 else message
        # payload = {
        #     "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        # }
        # headers = {
        #     'typ': 'jwt',
        #     'alg': 'HS256'
        # }
        # token = None if status != 0 else jwt.encode(payload=payload, key=salt, algorithm="HS256",
        #                                             headers=headers).decode("utf-8")
        global currUserId
        currUserId = stuId
        print("学生登陆成功")
        print(status)
        return JsonResponse({
            "data": {
                "userID": stuId,
                "token": None
            },
            "status": status,
            "statusInfo": {
                "message": message,
                "detail": ""
            }
        })
    else:
        print("学生登陆失败")
        return JsonResponse({
            "data": {
                "userID": "",
                "token": None
            },
            "status": 1,
            "statusInfo": {
                "message": "登陆失败",
                "detail": ""
            }
        })


# 教师登录
def teaLogin(request):
    if request.method == 'GET':
        request.encoding = "utf-8"
        teaId = request.GET['teacherId']
        password = request.GET['teacherPwd']
        print(teaId)
        print(password)
        sql = f'''
        select password from teacher where teaId="{teaId}";
        '''
        cursor.execute(sql)
        db.commit()
        results = cursor.fetchall()
        status = 0 if len(results) == 1 and results[0][0] == password else 1
        message = "登陆成功" if status == 0 else "密码错误"
        message = "用户未注册" if len(results) != 1 else message
        # payload = {
        #     "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        # }
        # headers = {
        #     'typ': 'jwt',
        #     'alg': 'HS256'
        # }
        # token = None if status != 0 else jwt.encode(payload=payload, key=salt, algorithm="HS256",
        #                                            headers=headers).decode("utf-8")
        global currUserId
        currUserId = teaId
        print("教师登陆成功")
        print(status)
        return JsonResponse({
            "data": {
                "userID": teaId,
                "token": None
            },
            "status": status,
            "statusInfo": {
                "message": message,
                "detail": ""
            }
        })
    else:
        print("教师登陆失败")
        return JsonResponse({
            "data": {
                "userID": "",
                "token": None
            },
            "status": 1,
            "statusInfo": {
                "message": "登陆失败",
                "detail": ""
            }
        })


def stuLesson(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        operation = data['operation']
        if operation == "select":
            userId = data['userId']
            courseId = data['courseId']
            sql = f'''
                    insert into course_selection values("{courseId}", "{userId}");
                    '''
            cursor.execute(sql)
            db.commit()
            # 查询剩余未选课程
            sql1 = f'''
                    select * from course where courseId not in
                    (select courseId from course_selection where stuId="{userId}");
                    '''
            cursor.execute(sql1)
            db.commit()
            results1 = cursor.fetchall()
            unCourseTable = []
            for each in results1:
                unCourseTable.append({
                    "id": each[0],
                    "name": each[1],
                    "teacher": each[2],
                    "capacity": each[3]
                })
            #查询已选课程
            sql2 = f'''
                    select * from course where courseId in
                    (select courseId from course_selection where stuId="{userId}");
                    '''
            cursor.execute(sql2)
            db.commit()
            results2 = cursor.fetchall()
            CourseTable = []
            for each in results2:
                CourseTable.append({
                    "id": each[0],
                    "name": each[1],
                    "teacher": each[2],
                    "capacity": each[3]
                })
            return JsonResponse({
                "data": {
                    "courseTable": CourseTable,
                    "unCourseTable": unCourseTable
                },
                "status": 0,
                "statusInfo": {
                    "message": "",
                    "detail": ""
                }
            })
        elif operation == "delete":
            userId = data['userId']
            courseId = data['courseId']
            sql = f'''
                    delete from course_selection where courseId="{courseId}" and stuId="{userId}";
                    '''
            cursor.execute(sql)
            db.commit()
            # 查询剩余未选课程
            sql1 = f'''
                                select * from course where courseId not in
                                (select courseId from course_selection where stuId="{userId}");
                                '''
            cursor.execute(sql1)
            db.commit()
            results1 = cursor.fetchall()
            unCourseTable = []
            for each in results1:
                unCourseTable.append({
                    "id": each[0],
                    "name": each[1],
                    "teacher": each[2],
                    "capacity": each[3]
                })
            # 查询已选课程
            sql2 = f'''
                                select * from course where courseId in
                                (select courseId from course_selection where stuId="{userId}");
                                '''
            cursor.execute(sql2)
            db.commit()
            results2 = cursor.fetchall()
            CourseTable = []
            for each in results2:
                CourseTable.append({
                    "id": each[0],
                    "name": each[1],
                    "teacher": each[2],
                    "capacity": each[3]
                })
            return JsonResponse({
                "data": {
                    "courseTable": CourseTable,
                    "unCourseTable": unCourseTable
                },
                "status": 0,
                "statusInfo": {
                    "message": "",
                    "detail": ""
                }
            })
    elif request.method == 'GET':
        request.encoding = 'utf-8'
        if request.GET['operation'] == "unselected":
            userId = request.GET['userId']
            sql = f'''
                    select * from course where courseId not in
                    (select courseId from course_selection where stuId="{userId}");
                    '''
            if request.GET['searchText']:
                sql = f'''
                        select * from course where courseName like "%{request.GET['searchText']}%" and courseId not in
                        (select courseId from course_selection where stuId="{userId}");
                        '''
            cursor.execute(sql)
            db.commit()
            results = cursor.fetchall()
            courseTable = []
            for each in results:
                courseTable.append({
                    "id": each[0],
                    "name": each[1],
                    "teacher": each[2],
                    "capacity": each[3]
                })
            return JsonResponse({
                "data": {
                    "courseTable": courseTable
                },
                "status": 0,
                "statusInfo": {
                    "message": "",
                    "detail": ""
                }
            })
        elif request.GET['operation'] == "selected":
            userId = request.GET['userId']
            print(userId)
            sql = f'''
                    select * from course where courseId in
                    (select courseId from course_selection where stuId="{userId}");
                    '''
            if request.GET['searchText']:
                sql = f'''
                        select * from course where courseName like "%{request.GET['searchText']}%" and courseId in
                        (select courseId from course_selection where stuId="{userId}");
                        '''
            cursor.execute(sql)
            db.commit()
            results = cursor.fetchall()
            print(len(results))
            courseTable = []
            for each in results:
                courseTable.append({
                    "id": each[0],
                    "name": each[1],
                    "teacher": each[2],
                    "capacity": each[3]
                })
            return JsonResponse({
                "data": {
                    "courseTable": courseTable
                },
                "status": 0,
                "statusInfo": {
                    "message": "",
                    "detail": ""
                }
            })
    return JsonResponse({
        "data": {
            "courseTable": []
        },
        "status": 0,
        "statusInfo": {
            "message": "",
            "detail": ""
        }
    })



def teaLesson(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        operation = data['operation']
        if operation == "add":
            courseName = data['courseName']
            capacity = data['courseSum']
            sql = f'''
                    insert into course (courseName,teaId,capacity)
                    values("{courseName}", "{currUserId}", "{capacity}");
                    '''
            cursor.execute(sql)
            db.commit()
            return JsonResponse({
                "data": {},
                "status": 0,
                "statusInfo": {
                    "message": "",
                    "detail": ""
                }
            })
        elif operation == "delete":
            courseName = data['courseName']
            sql = f'''
            delete from course where courseName="{courseName}";
            '''
            cursor.execute(sql)
            db.commit()
            return JsonResponse({
                "data": {},
                "status": 0,
                "statusInfo": {
                    "message": "",
                    "detail": ""
                }
            })


def add(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        courseName = data['title']
        capacity = data['sum']
        sql = f'''
                insert into course (courseName,teaId,capacity)
                values("{courseName}", "{currUserId}", "{capacity}");
                '''
        cursor.execute(sql)
        db.commit()
        return JsonResponse({
            "data": {},
            "status": 0,
            "statusInfo": {
                "message": "",
                "detail": ""
            }
        })


def teaQuery(request):
    if request.method == 'GET':
        request.encoding = 'utf-8'
        sql = f'''
        select * from course where teaId="{currUserId}");
        '''
        if 'searchText' in request.GET:
            sql = f'''
            select * from course where courseName like "%{request.GET['searchText']}%" and teaId="{currUserId}");
            '''
        cursor.execute(sql)
        db.commit()
        results = cursor.fetchall()
        courseTable = []
        for each in results:
            courseTable.append({
                "id": each[0],
                "name": each[1],
                "capacity": each[3]
            })
        return JsonResponse({
            "data": {
                "courseTable": courseTable
            },
            "status": 0,
            "statusInfo": {
                "message": "",
                "detail": ""
            }
        })


def verify_token(request):
    if 'token' in request.headers:
        token = request.headers['token']
        a, b = test_token(token)
        if not a:
            return my_json(b)
        else:
            print("token验证成功")
    else:
        return my_json("请求头无token")


from jwt import exceptions


def test_token(token):
    try:
        verified_payload = jwt.decode(token, salt, True)
        return True, "ok"
    except exceptions.ExpiredSignatureError:
        return False, "token已失效"
    except jwt.DecodeError:
        return False, "token认证失败"
    except jwt.InvalidTokenError:
        return False, "非法的token"


def my_json(message, status=1, courseTable=None):
    return JsonResponse({
        "data": {
            "courseTable": courseTable
        },
        "status": status,
        "statusInfo": {
            "message": message,
            "detail": ""
        }
    })


def index(request):
    res = verify_token(request)
    if res:
        return res
    return render(request, 'index.html')