import cv2 as cv


def face_detect():
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # 使用 OpenCV 自带的级联分类器路径
    cascade_path = cv.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv.CascadeClassifier(cascade_path)

    # 检测人脸
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        cv.rectangle(img, (x, y), (x + w, y + h), color=(0, 0, 255), thickness=2)

    cv.imshow('result', img)


# 读取图像（注意文件扩展名是否正确）
img = cv.imread(r'D:\OPenCV\test.jpg')

# 检查图像是否成功加载
if img is None:
    print("Error: 图像未找到，请检查路径！")
else:
    face_detect()
    # 等待按键退出
    while True:
        key = cv.waitKey(0)
        if key == ord('q') or key == 27:  # 'q' 或 ESC 键退出
            break

cv.destroyAllWindows()