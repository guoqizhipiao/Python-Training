#face_recognition模块封装了dlib的人脸识别功能，提供了简单易用的API。

import face_recognition
import os
from PIL import Image
import numpy as np

# 从图像文件中提取人脸特征向量
def facial_recognition_text(image_path, return_all=False):
    # 检查文件是否存在
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图像文件不存在: {image_path}")
    # 加载图像（face_recognition 自动处理 RGB）
    image = face_recognition.load_image_file(image_path)

    # 获取人脸位置（可选：model="cnn" 更准但慢，"hog" 快但略差）
    face_locations = face_recognition.face_locations(image, model="hog")
    # 如果没有检测到人脸，返回 None 或空列表
    if len(face_locations) == 0:
        return [] if return_all else None

    # 提取人脸编码（即 128 维特征向量）
    face_encodings = face_recognition.face_encodings(image, known_face_locations=face_locations)
    # 根据需求返回所有人脸的编码或第一个人脸的编码
    if return_all:
        return face_encodings
    else:
        # 第一个人脸的 embedding，shape=(128,)
        return face_encodings[0]  


# 从摄像头帧中提取人脸特征向量
def facial_recognition_from_frame(frame, return_all=False):
    # 检查文件是否存在
    if frame is None or frame.size == 0:
        raise ValueError("输入帧为空")

    # OpenCV 默认是 BGR，face_recognition 需要 RGB
    rgb_frame = frame[:, :, ::-1]  #快速 BGR -> RGB

    # 检测人脸位置（使用 HOG 模型，速度快）
    face_locations = face_recognition.face_locations(rgb_frame, model="hog")
    # 如果没有检测到人脸，返回 None 或空列表
    if len(face_locations) == 0:
        return [] if return_all else None

    # 提取人脸编码
    face_encodings = face_recognition.face_encodings(rgb_frame, known_face_locations=face_locations)
    # 根据需求返回所有人脸的编码或第一个人脸的编码
    if return_all:
        return face_encodings
    else:
        # 返回第一个人脸的 128 维特征
        return face_encodings[0]


if __name__ == "__main__":
    # 示例：提取单个人脸特征向量
    path = r"E:\GZT\C_C++\PYthon_shixun\github\practical_training\practical_training\core\OPenCV\3.jpg"
    emb = facial_recognition_text(path)
    if emb is not None:
        print("特征向量维度:", emb.shape)  # 应该是 (128,)
        print(emb)
    else:
        print("未检测到人脸！")