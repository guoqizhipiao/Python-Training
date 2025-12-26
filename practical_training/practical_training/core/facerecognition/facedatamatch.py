#face_recognition模块识别人脸并与数据库中的学生信息进行匹配

import os
import numpy as np

from .facialrecognitiontext import facial_recognition_text
from .facialrecognitiontext import facial_recognition_from_frame
from core.databasecode.database import database

# 获取当前脚本所在目录（绝对路径）
facerecognition_path =  os.path.dirname(os.path.abspath(__file__))
core_path = os.path.dirname(facerecognition_path)
practical_training_path = os.path.dirname(core_path)
os.sys.path.append(practical_training_path)
database_path = os.path.join(core_path, "databasecode", "students.db")

# 欧氏距离阈值，越小越相似
THRESHOLD = 0.4

# 人脸数据匹配函数
def face_data_match(photo_path):
    # 从照片路径是否存在
	if not os.path.isfile(photo_path):
		print("照片路径无效")
		return "PHOTOINVALID"
    # 检查数据库是否存在
	elif not os.path.exists(database_path):
		print("数据库文件不存在")
		return "DBNOTFOUND"
    # 提取照片中的人脸特征向量
	encoding = facial_recognition_text(photo_path)
    # 如果没有检测到人脸
	if encoding is None or encoding.size == 0:
		print("没有检测到脸")
		return "NOFACE"
    # 提取到特征向量
	print("提取到特征向量:", encoding)
    #在数据库中匹配人脸特征向量
	da = database()
    # 初始化最小距离和匹配学生信息
	mindistance = float('inf')
	mins1 = None
    # 遍历数据库中的学生信息
	for s1 in da.iter_show_students():
		print(s1)
        # 获取存储的特征向量
		stored_encoding = s1[4]
        # 将二进制数据转换为 NumPy 数组
		match_encoding = np.frombuffer(stored_encoding, dtype=np.float32)
        # 计算欧氏距离
		distance  = np.linalg.norm(encoding - match_encoding)
        # 输出距离信息
		print(f"与 {s1[2]} 的距离: {distance}")
        # 更新最小距离和匹配学生信息
		if distance < mindistance:
			mindistance = distance
			mins1 = s1
		if mindistance < THRESHOLD:
			break
    # 判断是否匹配成功
	if mindistance < THRESHOLD:
		print(f"匹配成功，学生姓名: {mins1[2]}, 学号: {mins1[3]}")
		print("SUCCESS",mins1[0],mins1[1],mins1[2],mins1[3], mindistance)
		return ("SUCCESS",mins1[0],mins1[1],mins1[2],mins1[3], mindistance)
	else:
		print("没有匹配到已注册的学生")
		return "NOMATCH"

# 从摄像头帧中识别人脸并匹配数据库中的学生信息
def face_data_match_from_frame(frame):
    # 检查输入帧是否有效
    if frame is None or frame.size == 0:
        print("无效的视频帧")
        return "FRAMEINVALID"

    # 检查数据库是否存在
    if not os.path.exists(database_path):
        print("数据库文件不存在")
        return "DBNOTFOUND"

    # 提取当前帧的人脸编码
    encoding = facial_recognition_from_frame(frame)
    if encoding is None or encoding.size == 0:
        print("没有检测到脸")
        return "NOFACE"
    #在数据库中匹配人脸特征向量
    da = database()
    # 初始化最小距离和匹配学生信息
    mindistance = float('inf')
    mins1 = None
    # 遍历数据库中的学生信息
    for s1 in da.iter_show_students():
        # 获取存储的特征向量
        stored_encoding = s1[4]
        # 将二进制数据转换为 NumPy 数组
        match_encoding = np.frombuffer(stored_encoding, dtype=np.float32)
        # 计算欧氏距离
        distance = np.linalg.norm(encoding - match_encoding)
        # 输出距离信息
        if distance < mindistance:
            mindistance = distance
            mins1 = s1
        if mindistance < THRESHOLD:
            break
    # 判断是否匹配成功
    if mindistance < THRESHOLD:
        return ("SUCCESS", mins1[0], mins1[1], mins1[2], mins1[3], mindistance)
    else:
        print("没有匹配到已注册的学生")
        return "NOMATCH"
