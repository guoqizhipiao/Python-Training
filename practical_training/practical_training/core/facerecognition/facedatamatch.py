import os
import numpy as np




facerecognition_path =  os.path.dirname(os.path.abspath(__file__))
core_path = os.path.dirname(facerecognition_path)
practical_training_path = os.path.dirname(core_path)
os.sys.path.append(practical_training_path)

from .facialrecognitiontext import facial_recognition_text
from .facialrecognitiontext import facial_recognition_from_frame
from core.databasecode.database import database

# 欧氏距离阈值，越小越相似
THRESHOLD = 0.4

database_path = os.path.join(core_path, "databasecode", "students.db")

def face_data_match(photo_path):
	if not os.path.isfile(photo_path):
		print("照片路径无效")
		return "PHOTOINVALID"
	elif not os.path.exists(database_path):
		print("数据库文件不存在")
		return "DBNOTFOUND"
	encoding = facial_recognition_text(photo_path)
	if encoding is None or encoding.size == 0:
		print("没有检测到脸")
		return "NOFACE"
	print("提取到特征向量:", encoding)

	da = database()
	mindistance = float('inf')
	mins1 = None
	for s1 in da.iter_show_students():
		print(s1)
		stored_encoding = s1[4]
		match_encoding = np.frombuffer(stored_encoding, dtype=np.float32)
		distance  = np.linalg.norm(encoding - match_encoding)
		print(f"与 {s1[2]} 的距离: {distance}")
		if distance < mindistance:
			mindistance = distance
			mins1 = s1
		if mindistance < THRESHOLD:
			break
	if mindistance < THRESHOLD:
		print(f"匹配成功，学生姓名: {mins1[2]}, 学号: {mins1[3]}")
		print("SUCCESS",mins1[0],mins1[1],mins1[2],mins1[3], mindistance)
		return ("SUCCESS",mins1[0],mins1[1],mins1[2],mins1[3], mindistance)
	else:
		print("没有匹配到已注册的学生")
		return "NOMATCH"

def face_data_match_from_frame(frame):
    """
    从摄像头帧中识别人脸并匹配数据库中的学生信息。
    
    参数:
        frame (np.ndarray): 从 self.cap.read() 获取的 BGR 图像帧。
    
    返回:
        匹配结果，格式同原函数。
    """
    if frame is None or frame.size == 0:
        print("无效的视频帧")
        return "FRAMEINVALID"

    # 检查数据库是否存在
    if not os.path.exists(database_path):
        print("数据库文件不存在")
        return "DBNOTFOUND"

    # 提取当前帧的人脸编码
    encoding = facial_recognition_from_frame(frame)  # 假设此函数支持传入 np.ndarray 图像
    if encoding is None or encoding.size == 0:
        print("没有检测到脸")
        return "NOFACE"

    da = database()
    mindistance = float('inf')
    mins1 = None

    for s1 in da.iter_show_students():
        stored_encoding = s1[4]
        match_encoding = np.frombuffer(stored_encoding, dtype=np.float32)
        distance = np.linalg.norm(encoding - match_encoding)

        if distance < mindistance:
            mindistance = distance
            mins1 = s1
        if mindistance < THRESHOLD:
            break

    if mindistance < THRESHOLD:
        return ("SUCCESS", mins1[0], mins1[1], mins1[2], mins1[3], mindistance)
    else:
        print("没有匹配到已注册的学生")
        return "NOMATCH"
