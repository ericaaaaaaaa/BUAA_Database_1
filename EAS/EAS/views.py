# -*- coding:utf-8 -*-
import pymysql
from django.http import JsonResponse
from django.shortcuts import render, redirect
import json

# 打开数据库连接
conn = pymysql.connect(host="localhost", port=3306, user="root",
                     password="root", database="eams", charset="utf8")

# 使用cursor()方法获取操作游标
cursor = conn.cursor()

# 使用预处理语句创建表
# 学生(学号 密码)
sql1 = '''
CREATE TABLE IF NOT EXISTS student (
stuId varchar(50) NOT NULL,
password varchar(50) NOT NULL,
primary key (stuId)
)ENGINE=innodb DEFAULT CHARSET=utf8;
'''

# 教师(工号 密码)
sql2 = '''
CREATE TABLE IF NOT EXISTS teacher (
teaId varchar(50) NOT NULL,
password varchar(50) NOT NULL,
primary key (teaId)
)ENGINE=innodb DEFAULT CHARSET=utf8;
'''

# 课程(课程编号 课程名称 授课教师 容量)
sql3 = '''
CREATE TABLE IF NOT EXISTS course (
courseId int NOT NULL AUTO_INCREMENT,
courseName varchar(50) NOT NULL,
teaId varchar(50),
capacity int NOT NULL,
primary key (courseId)
)ENGINE=innodb DEFAULT CHARSET=utf8;
'''

# 选课情况(课程编号 学号)
sql4 = '''
CREATE TABLE IF NOT EXISTS course_selection (
courseId int NOT NULL,
stuId varchar(50) NOT NULL,
primary key (courseId,stuId)
)ENGINE=innodb DEFAULT CHARSET=utf8;
'''

cursor.execute(sql1)
cursor.execute(sql2)
cursor.execute(sql3)
cursor.execute(sql4)
cursor.close()

currUserId = ''
salt = "xxxxxx"


# 学生注册
def stuRegister(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        stuId = data['studentId']
        password = data['studentPwd']
        cursor = conn.cursor()
        sql = f'''
        insert into student (stuId,password)
        values ("{stuId}", "{password}");
        '''
        cursor.execute(sql)
        conn.commit()
        cursor.close()
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
        cursor = conn.cursor()
        sql = f'''
        insert into teacher (teaId,password)
        values ("{teaId}", "{password}");
        '''
        cursor.execute(sql)
        conn.commit()
        cursor.close()
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
        cursor = conn.cursor()
        sql = f'''
        select password from student where stuId="{stuId}";
        '''
        cursor.execute(sql)
        conn.commit()
        results = cursor.fetchall()
        status = 0 if len(results) == 1 and results[0][0] == password else 1
        message = "登陆成功" if status == 0 else "密码错误"
        message = "用户未注册" if len(results) != 1 else message
        cursor.close()
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
        cursor = conn.cursor()
        sql = f'''
        select password from teacher where teaId="{teaId}";
        '''
        cursor.execute(sql)
        conn.commit()
        results = cursor.fetchall()
        status = 0 if len(results) == 1 and results[0][0] == password else 1
        message = "登陆成功" if status == 0 else "密码错误"
        message = "用户未注册" if len(results) != 1 else message
        cursor.close()
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
            cursor = conn.cursor()
            sql = f'''
                    insert into course_selection values("{courseId}", "{userId}");
                    '''
            cursor.execute(sql)
            conn.commit()
            # 查询剩余未选课程
            sql1 = f'''
                    select * from course where courseId not in
                    (select courseId from course_selection where stuId="{userId}");
                    '''
            cursor.execute(sql1)
            conn.commit()
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
            conn.commit()
            results2 = cursor.fetchall()
            CourseTable = []
            for each in results2:
                CourseTable.append({
                    "id": each[0],
                    "name": each[1],
                    "teacher": each[2],
                    "capacity": each[3]
                })
            cursor.close()
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
            cursor = conn.cursor()
            sql = f'''
                    delete from course_selection where courseId="{courseId}" and stuId="{userId}";
                    '''
            cursor.execute(sql)
            conn.commit()
            # 查询剩余未选课程
            sql1 = f'''
                                select * from course where courseId not in
                                (select courseId from course_selection where stuId="{userId}");
                                '''
            cursor.execute(sql1)
            conn.commit()
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
            conn.commit()
            results2 = cursor.fetchall()
            CourseTable = []
            for each in results2:
                CourseTable.append({
                    "id": each[0],
                    "name": each[1],
                    "teacher": each[2],
                    "capacity": each[3]
                })
            cursor.close()
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
            cursor = conn.cursor()
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
            conn.commit()
            results = cursor.fetchall()
            courseTable = []
            for each in results:
                courseTable.append({
                    "id": each[0],
                    "name": each[1],
                    "teacher": each[2],
                    "capacity": each[3]
                })
            cursor.close()
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
            cursor = conn.cursor()
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
            conn.commit()
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
            cursor.close()
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
            cursor = conn.cursor()
            sql = f'''
                    insert into course (courseName,teaId,capacity)
                    values("{courseName}", "{currUserId}", "{capacity}");
                    '''
            cursor.execute(sql)
            conn.commit()
            cursor.close()
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
            cursor = conn.cursor()
            sql1 = f'''
                    select * from course where courseName="{courseName}";
                    '''
            cursor.execute(sql1)
            conn.commit()
            result = cursor.fetchall()
            courseId = result[0][0]
            sql2 = f'''
                    delete from course where courseName="{courseName}";
                    '''
            cursor.execute(sql2)
            conn.commit()
            sql3 = f'''
                    delete from course_selection where courseId="{courseId}";
                    '''
            cursor.execute(sql3)
            conn.commit()
            cursor.close()
            return JsonResponse({
                "data": {},
                "status": 0,
                "statusInfo": {
                    "message": "",
                    "detail": ""
                }
            })
    elif request.method == 'GET':
        request.encoding = 'utf-8'
        if request.GET['operation'] == "getClass":
            teaId = request.GET['userId']
            cursor = conn.cursor()
            sql = f'''
                    select * from course where teaId="{teaId}";
                    '''
            cursor.execute(sql)
            conn.commit()
            results = cursor.fetchall()
            courseTable = []
            for each in results:
                courseTable.append({
                    "title": each[1],
                    "done": False,
                    "sum": each[3]
                })
            cursor.close()
            return JsonResponse({
                "courseTable": courseTable,
                "status": 0,
                "statusInfo": {
                    "message": "",
                    "detail": ""
                }
            })
    return JsonResponse({
        "data": {},
        "status": 0,
        "statusInfo": {
            "message": "",
            "detail": ""
        }
    })


def stuChangePwd(request):
    if request.method == 'GET':
        request.encoding = 'utf-8'
        stuId = request.GET['studentId']
        pwd = request.GET['studentPwd']
        newPwd = request.GET['studentNewPwd']
        cursor = conn.cursor()
        sql1 = f'''
                select password from student where stuId="{stuId}";
                '''
        cursor.execute(sql1)
        conn.commit()
        results = cursor.fetchall()
        status = 0 if len(results) == 1 and results[0][0] == pwd else 1
        message = "密码修改成功" if status == 0 else "原密码错误"
        message = "用户未注册" if len(results) != 1 else message
        if status == 0:
            sql2 = f'''
                    update student set password="{newPwd}" where stuId="{stuId}";
                    '''
            cursor.execute(sql2)
        cursor.close()
        return JsonResponse({
            "data": {},
            "status": status,
            "statusInfo": {
                "message": message,
                "detail": ""
            }
        })
    return JsonResponse({
        "data": {},
        "status": 1,
        "statusInfo": {
            "message": "密码修改失败",
            "detail": ""
        }
    })


def teaChangePwd(request):
    if request.method == 'GET':
        request.encoding = 'utf-8'
        teaId = request.GET['teacherId']
        pwd = request.GET['teacherPwd']
        newPwd = request.GET['teacherNewPwd']
        cursor = conn.cursor()
        sql1 = f'''
                select password from teacher where teaId="{teaId}";
                '''
        cursor.execute(sql1)
        conn.commit()
        results = cursor.fetchall()
        status = 0 if len(results) == 1 and results[0][0] == pwd else 1
        message = "密码修改成功" if status == 0 else "原密码错误"
        message = "用户未注册" if len(results) != 1 else message
        if status == 0:
            sql2 = f'''
                    update teacher set password="{newPwd}" where teaId="{teaId}";
                    '''
            cursor.execute(sql2)
        cursor.close()
        return JsonResponse({
            "data": {},
            "status": status,
            "statusInfo": {
                "message": message,
                "detail": ""
            }
        })
    return JsonResponse({
        "data": {},
        "status": 1,
        "statusInfo": {
            "message": "密码修改失败",
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