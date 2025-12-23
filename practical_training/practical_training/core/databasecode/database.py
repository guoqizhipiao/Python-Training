#数据库
#数据库模块
import sqlite3
import os
#高级文件操作
import shutil


# 获取当前脚本所在目录（绝对路径）
databasecode_path = os.path.dirname(os.path.abspath(__file__))
photo_path = os.path.join(databasecode_path, "students_photos")
database_path = os.path.join(databasecode_path, "students.db")

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
                photo_path TEXT NOT NULL -- 照片路径文本类型
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
                    return
                # 复制照片到指定目录
                photo_filename = f"{student_id}.jpg"
                photo_dest_path = f"{photo_path}/{photo_filename}"
                shutil.copy(photo_source_path, photo_dest_path)
                # 插入学生信息到数据库
                cur.execute('''
                    INSERT INTO students (id_number, name, student_id, photo_path)
                    VALUES (?, ?, ?, ?)
                ''', (id_number, name, student_id, photo_dest_path))
                print(f"学生 {name} 信息添加成功")
        except Exception as e:
            print(f"添加失败：{e}")

    #生成器 逐行返回学生信息元组 (id_number, name, student_id, photo_path)
    #注意一个生成器不能重置 只能新建一个生成器实例
    def iter_show_students(self):
        
        try:
            with sqlite3.connect(database_path) as con:
                cur = con.cursor()
                cur.execute('SELECT id_number, name, student_id, photo_path FROM students')
                # 等价于 for row in cur: yield row
                yield from cur
        except Exception as e:
            print(f"查询失败：{e}")
            return

    #生成器 按身份证号查询学生信息，返回学生信息元组
    def iter_find_show_students_idnumber(self, id_number):
        try:
            with sqlite3.connect(database_path) as con:
                cur = con.cursor()
                cur.execute('SELECT id_number, name, student_id, photo_path FROM students WHERE id_number = ?', (id_number,))
                yield from cur
        except Exception as e:
            print(f"查询失败：{e}")
            return
    #按身份证号查询学生信息，返回学生信息元组 或 None
    def find_show_students_idnumber(self, id_number):
        find_students = self.iter_find_show_students_idnumber(id_number)
        return next(find_students, None)
    
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

    f1 = da.find_show_students_idnumber("123456789012345677")
    if f1:
        print(f1)
    else:
        print("未找到该学生信息")