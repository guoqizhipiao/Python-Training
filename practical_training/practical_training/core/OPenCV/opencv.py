import cv2
import os
import numpy as np


# 检测人脸
def detect_face(img):
    # 将测试图像转化为灰度图像，因为OpenCV人脸检测器需要灰度图像
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 适配不同环境的级联分类器路径
    mypath = r'D:\Anaconda3\envs\OpenCV\Lib\site-packages\cv2\data'
    face_cascade = cv2.CascadeClassifier(mypath + '/haarcascade_frontalface_default.xml')

    # 检测人脸
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)

    # 如果未检测到人脸，返回None
    if len(faces) == 0:
        return None, None

    # 提取第一个人脸的区域（x,y为左上角坐标，w为宽度，h为高度）
    (x, y, w, h) = faces[0]
    # 修正：人脸裁剪应该是 y:y+h, x:x+w（之前写反了w和h）
    return gray[y:y + h, x:x + w], faces[0]


# 准备训练数据
def prepare_training_data(data_folder_path):
    # 获取数据文件夹下的所有子目录
    dirs = os.listdir(data_folder_path)

    faces = []  # 存储所有人脸
    labels = []  # 存储对应的标签

    for dir_name in dirs:
        # 跳过非数字命名的文件夹（标签应为数字）
        if not dir_name.isdigit():
            continue

        # 将文件夹名转为标签（整数）
        label = int(dir_name)

        # 修正：正确拼接子文件夹路径，避免覆盖原路径
        subject_dir_path = os.path.join(data_folder_path, dir_name)

        # 获取子文件夹下的所有图片文件名
        subject_images_names = os.listdir(subject_dir_path)

        # 遍历每张图片
        for image_name in subject_images_names:
            # 跳过系统隐藏文件（如.DS_Store）
            if image_name.startswith("."):
                continue

            # 拼接完整的图片路径
            image_path = os.path.join(subject_dir_path, image_name)

            # 修正：正确读取图片（之前拼写错误）
            image = cv2.imread(image_path)

            # 检查图片是否读取成功
            if image is None:
                print(f"警告：无法读取图片 {image_path}")
                continue

            # 显示正在处理的图片（可选）
            cv2.imshow("Training in image...", cv2.resize(image, (400, 300)))
            cv2.waitKey(50)  # 显示50ms

            # 检测人脸
            face, rect = detect_face(image)

            # 如果检测到人脸，添加到训练集
            if face is not None:
                faces.append(face)
                labels.append(label)

    # 关闭所有显示窗口
    cv2.waitKey(1)
    cv2.destroyAllWindows()

    return faces, labels


# 在图片上绘制矩形框
def draw_rectangle(img, rect):
    (x, y, w, h) = rect
    cv2.rectangle(img, (x, y), (x + w, y + h), (128, 128, 0), 2)


# 在图片上绘制文字
def draw_text(img, text, x, y):  # 修正：变量名imh改为img
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_COMPLEX, 1, (128, 128, 0), 2)


# 人脸识别预测函数
def predict(test_img):
    # 避免修改原始图片
    img = test_img.copy()

    # 检测人脸
    face, rect = detect_face(img)

    # 如果未检测到人脸，直接返回原图和提示信息
    if face is None:
        return img, "No face detected"

    # 识别人脸（返回标签和置信度）
    label, confidence = face_recognizer.predict(face)

    # 根据标签获取对应的人名
    label_text = subjects[label] if 0 <= label < len(subjects) else "Unknown"

    # 绘制矩形框和文字
    draw_rectangle(img, rect)
    draw_text(img, label_text, rect[0], rect[1] - 5)

    return img, label_text


# -------------------------- 主程序执行 --------------------------
# 1. 定义人物标签（索引对应训练数据的文件夹名）
subjects = ["zhaoliying", "liudehua"]  # 0: 赵丽颖, 1: 刘德华

# 2. 准备训练数据（请确保training_data文件夹存在，且子文件夹为数字命名）
print("正在准备训练数据...")
faces, labels = prepare_training_data("training_data")
print(f"训练数据准备完成：共检测到 {len(faces)} 个人脸")

# 3. 训练人脸识别模型
if len(faces) > 0:
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    face_recognizer.train(faces, np.array(labels))
    print("模型训练完成！")
else:
    print("没有可用的训练数据，程序退出")
    exit()

# 4. 加载测试图片并进行预测
# 检查测试图片路径是否存在
test_img1_path = r"D:\OPenCV\test_data\test1_img1\test1.jpg.jpeg"
test_img2_path = r"D:\OPenCV\test_data\test2_img2\test2.jpg.jpeg"

if not os.path.exists(test_img1_path) or not os.path.exists(test_img2_path):
    print("警告：测试图片不存在，请检查路径！")
    exit()

test_img1 = cv2.imread(test_img1_path)
test_img2 = cv2.imread(test_img2_path)

# 5. 进行预测
predicted_img1, pre_label_text1 = predict(test_img1)
predicted_img2, pre_label_text2 = predict(test_img2)

# 6. 显示预测结果
cv2.imshow(pre_label_text1 + ' - Test 1', predicted_img1)
cv2.imshow(pre_label_text2 + ' - Test 2', predicted_img2)

# 等待按键后关闭窗口
cv2.waitKey(0)
cv2.destroyAllWindows()