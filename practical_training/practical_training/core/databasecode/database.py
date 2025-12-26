#数据库
#数据库模块
import sqlite3
import os
#高级文件操作
import shutil
import numpy as np
import sys




# 获取当前脚本所在目录（绝对路径）
databasecode_path = os.path.dirname(os.path.abspath(__file__))
photo_path = os.path.join(databasecode_path, "students_photos")
database_path = os.path.join(databasecode_path, "students.db")

core_path = os.path.dirname(databasecode_path)
practical_training_path = os.path.dirname(core_path)

sys.path.append(practical_training_path)

from core.facerecognition.facialrecognitiontext import facial_recognition_text

class database:
    #初始化
    def __init__(self):
        # 确保目录存在
        os.makedirs(os.path.dirname(database_path), exist_ok=True)
        #创建数据库连接
        con = sqlite3.connect(database_path)
        cur = con.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT, -- 主键int类型，自增长
                id_number TEXT NOT NULL UNIQUE, -- 身份证号文本类型，唯一
                name TEXT NOT NULL, -- 姓名文本类型
                student_id TEXT NOT NULL UNIQUE, -- 学号文本类型，唯一
                photo_path TEXT NOT NULL, -- 照片路径文本类型
                face_encoding BLOB  -- 新增：存储128维特征向量的二进制数据
            )
        ''')
        #提交更改并关闭连接
        con.commit()
        con.close()
        print("数据库初始化完成")

    #添加学生信息
    def add_student(self, id_number, name, student_id, photo_source_path):
        #检查输入的有效性
        if not id_number or not name or not student_id or not photo_source_path:
            print("所有字段均为必填项")
            return
        if not os.path.isfile(photo_source_path):
            print("照片路径无效")
            return
        try:
            with sqlite3.connect(database_path) as con:
                #连接数据库
                cur = con.cursor()
                #检查身份证号或学号是否已存在
                cur.execute('''
                    SELECT 1 FROM students 
                    WHERE id_number = ? OR student_id = ?
                ''', (id_number, student_id))

                if cur.fetchone():
                    print("身份证号或学号已存在")
                    return "REPEAT"
                #提取人脸特征向量
                encoding = facial_recognition_text(photo_source_path)

                if encoding is None or encoding.size == 0:
                    print("没有检测到脸")
                    return "NOFACE"

                embedding_blob = encoding.astype(np.float32).tobytes()

                # 插入学生信息到数据库
                cur.execute('''
                    INSERT INTO students (id_number, name, student_id, photo_path, face_encoding)
                    VALUES (?, ?, ?, ?, ?)
                ''', (id_number, name, student_id, photo_source_path, embedding_blob))


                student_db_id = cur.lastrowid

                #获取照片扩展名并命名为 学号.扩展名
                original_ext = os.path.splitext(photo_source_path)[1].lower()
                photo_filename = f"{student_db_id}{original_ext}"
                #复制照片到指定目录
                photo_dest_path = f"{photo_path}/{photo_filename}"
                shutil.copy(photo_source_path, photo_dest_path)
                #更新数据库中的照片路径
                cur.execute('''
                    UPDATE students SET photo_path = ? WHERE id = ?
                ''', (photo_filename, student_db_id))

                print(f"学生 {name} 信息添加成功")
                return "SUCCESS"
        except Exception as e:
            print(f"添加失败：{e}")

    #生成器 逐行返回学生信息元组 (id_number, name, student_id, photo_path)
    #注意一个生成器不能重置 只能新建一个生成器实例
    def iter_show_students(self):
        try:
            with sqlite3.connect(database_path) as con:
                cur = con.cursor()
                cur.execute('SELECT id_number, name, student_id, photo_path, face_encoding FROM students')
                # 等价于 for row in cur: yield row
                yield from cur
        except Exception as e:
            print(f"查询失败：{e}")
            return
    def iter_show_students_trainmodel(self):
        try:
            with sqlite3.connect(database_path) as con:
                cur = con.cursor()
                cur.execute('SELECT id, id_number, name, student_id, photo_path, face_encoding FROM students')
                # 等价于 for row in cur: yield row
                yield from cur
        except Exception as e:
            print(f"查询失败：{e}")
            return

    '''#生成器 按身份证号查询学生信息，返回学生信息元组
    def iter_find_show_students_idnumber(self, id_number):
        try:
            with sqlite3.connect(database_path) as con:
                cur = con.cursor()
                cur.execute('SELECT id_number, name, student_id, photo_path FROM students WHERE id_number = ?', (id_number,))
                print("身份证号查询到：",cur)
                row = cur.fetchone()
                print("查询结果：", row)
                yield from cur
        except Exception as e:
            print(f"查询失败：{e}")
            return
    #按身份证号查询学生信息，返回学生信息元组 或 None
    def find_show_students_idnumber(self, id_number):
        find_students = self.iter_find_show_students_idnumber(id_number)
        return next(find_students, None)'''
    
    def find_show_students_idnumber(self, id_number):
        try:
            with sqlite3.connect(database_path) as con:
                cur = con.cursor()
                cur.execute('SELECT id_number, name, student_id, photo_path FROM students WHERE id_number = ?', (id_number,))
                return cur.fetchone()  # 返回 tuple 或 None
        except Exception as e:
            print(f"查询失败：{e}")
            return None

    #生成器 按学号查询学生信息，返回学生信息元组
    def iter_find_show_students_studentid(self, student_id):
        try:
            with sqlite3.connect(database_path) as con:
                cur = con.cursor()
                cur.execute('SELECT id_number, name, student_id, photo_path FROM students WHERE student_id = ?', (student_id,))
                print("学号查询到：",cur)
                yield from cur
        except Exception as e:
            print(f"查询失败：{e}")
            return

    #按学号查询学生信息，返回学生信息元组 或 None
    def find_show_students_studentid(self, student_id):
        find_students = self.iter_find_show_students_studentid(student_id)
        return next(find_students, None)


    def delete_student_idnumber(self, id_number):
        student = self.find_show_students_idnumber(id_number)
        if not student:
            print("未找到该学生信息")
            return
        else:
            try:
                with sqlite3.connect(database_path) as con:
                    cur = con.cursor()
                    #删除学生照片文件
                    
                    student_photo_path = os.path.join(photo_path, student[3])
                    if os.path.isfile(student_photo_path):
                        os.remove(student_photo_path)
                        print("照片删除成功")
                    print(student_photo_path)
                    #从数据库中删除学生记录
                    cur.execute('DELETE FROM students WHERE id_number = ?', (id_number,))
                    print(f"学生 {student[1]} 信息删除成功")
            except Exception as e:
                print(f"删除失败：{e}")

    def get_student_count(self):
        try:
            with sqlite3.connect(database_path) as con:
                cur = con.cursor()
                cur.execute("SELECT COUNT(*) FROM students")
                count = cur.fetchone()[0]
                return count
        except Exception as e:
            print(f"获取个数失败：{e}")
                

if __name__ == "__main__":
    core_path = os.path.dirname(databasecode_path)
    practical_training_path = os.path.dirname(core_path)
    testfolder_path = os.path.join(practical_training_path, "testfolder")
    da = database()
    da.add_student("123456789012345678", "张三测试", "1900061298", os.path.join(testfolder_path, "cszp1.jpg"))
    da.add_student("123456789012345679", "小美测试", "1900061299", os.path.join(testfolder_path, "cszp2.png"))
    #print(os.path.dirname(databasecode_path), os.path.join(core_path, "testfolder"))
    #print(os.path.join(testfolder_path, "cszp1.jpg"), os.path.join(testfolder_path, "cszp2.png"))
    print("完成")

    for s1 in da.iter_show_students():
        print(s1)
    """s2 = da.iter_show_students()
    s3 = da.iter_show_students()
    print(next(s2))
    print(next(s3))"""

    f1 = da.find_show_students_idnumber("1")
    if f1:
        print(f1)
    else:
        print("未找到该学生信息")

    f2 = da.find_show_students_studentid("1")
    if f2:
        print(f2)
    else:
        print("未找到该学生信息")

    da.delete_student_idnumber("123456789012345677")

    count = da.get_student_count()
    if count != None:
        print(f"有{count}个学生")
    else:
        print("获取学生个数失败")