import cv2
import os
from PIL import Image
import numpy as np


def getImageAndLabels_database(imagePaths):
    facesSamples = []
    ids = []

    # 支持的图像格式
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')

    # 获取所有图像路径

    print('数据排列：', imagePaths)

    # 使用 OpenCV 自带的人脸检测器
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
    face_detector = cv2.CascadeClassifier(cascade_path)

    print(cascade_path)

    if face_detector.empty():
        raise IOError(f"无法加载级联分类器: {cascade_path}")

    for imagePath in imagePaths:
        try:
            # 打开并转为灰度图
            PIL_img = Image.open(imagePath).convert('L')
            img_numpy = np.array(PIL_img, 'uint8')

            # 检测人脸
            faces = face_detector.detectMultiScale(
                img_numpy,
                scaleFactor=1.1,
                minNeighbors=3,
                minSize=(60, 60),
                maxSize=(10000, 1000)
            )

            # 从文件名提取 ID（假设格式为 "1.jpg", "2.png" 等）
            filename = os.path.split(imagePath)[1]
            id = int(filename.split('.')[0])  # 如 "123.jpg" → 123

            # 保存每张检测到的人脸区域
            for (x, y, w, h) in faces:
                facesSamples.append(img_numpy[y:y + h, x:x + w])
                ids.append(id)
                print(f'已添加样本：ID={id}, 位置=({x},{y}) 尺寸=({w}x{h})')

            if len(faces) == 0:
                print(f'警告：{imagePath} 中未检测到人脸，跳过。')

        except Exception as e:
            print(f'处理 {imagePath} 时出错: {e}')

    print(f'共收集 {len(facesSamples)} 张人脸样本，对应 {len(set(ids))} 个用户。')
    return facesSamples, ids


