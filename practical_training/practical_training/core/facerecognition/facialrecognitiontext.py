import face_recognition
import os
from PIL import Image
import numpy as np

def facial_recognition_text(image_path, return_all=False):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图像文件不存在: {image_path}")
    # 加载图像（face_recognition 自动处理 RGB）
    image = face_recognition.load_image_file(image_path)

    # 获取人脸位置（可选：model="cnn" 更准但慢，"hog" 快但略差）
    face_locations = face_recognition.face_locations(image, model="hog")

    if len(face_locations) == 0:
        return [] if return_all else None

    # 提取人脸编码（即 128 维特征向量）
    face_encodings = face_recognition.face_encodings(image, known_face_locations=face_locations)

    if return_all:
        return face_encodings  # list of ndarray
    else:
        return face_encodings[0]  # 第一个人脸的 embedding，shape=(128,)

if __name__ == "__main__":
    # 示例：提取单个人脸特征向量
    path = r"E:\GZT\C_C++\PYthon_shixun\github\practical_training\practical_training\core\OPenCV\3.jpg"
    emb = facial_recognition_text(path)
    if emb is not None:
        print("特征向量维度:", emb.shape)  # 应该是 (128,)
        print(emb)
    else:
        print("未检测到人脸！")