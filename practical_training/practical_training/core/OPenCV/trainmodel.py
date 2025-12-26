import os
import sys
import cv2
import numpy as np
from datetime import datetime
import json

opencv_path = os.path.dirname(os.path.abspath(__file__))
core_path = os.path.dirname(opencv_path)
practical_training_path = os.path.dirname(core_path)
sys.path.append(practical_training_path)
database_path = os.path.join(core_path, 'databasecode')
students_photo_path = os.path.join(database_path, 'students_photos')
trainer_path = os.path.join(opencv_path, 'trainer')


from core.databasecode.database import database
from .enter_photos import getImageAndLabels_database

def database_train_model():
    # 初始化数据库
    da = database()
    NAMES = {}
    imagePaths = []

    for s1 in da.iter_show_students_trainmodel():
        NAMES[s1[0]] = s1[2]  # id_number : name
        s1_photo = os.path.join(students_photo_path, s1[4])
        imagePaths.append(s1_photo)  # photo_path
        print(f"加载学生: ID={s1[0]}, 姓名={s1[2]}, 照片路径={s1_photo}")
        
    print(f"已加载 {len(NAMES)} 名学生的信息用于训练模型。")
    faces, ids = getImageAndLabels_database(imagePaths)

    if len(faces) == 0:
        print("错误：未收集到任何人脸样本，请检查图像和检测器。")
    else:
        # 创建 trainer 目录
        os.makedirs('trainer', exist_ok=True)

        # 训练识别器
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(faces, np.array(ids))

        # 保存模型
        nowtime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        with open(f'{trainer_path}/database_{len(faces)}_{nowtime}.json', 'w', encoding='utf-8') as f:
            json.dump(NAMES, f, ensure_ascii=False, indent=4)
            print(f"已保存姓名映射至 {trainer_path}/database_{len(faces)}_{nowtime}.json")
        recognizer.write(f'{trainer_path}/database_{len(faces)}_{nowtime}.yml')
        print(f"训练完成，模型已保存至 {trainer_path}/database_{len(faces)}_{nowtime}.yml")

