import cv2

# ===== 配置区 =====
# 训练好的模型路径
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(r'D:\OPenCV\trainer\trainer.yml')

# 姓名列表：必须与训练时的 ID 顺序一致！
# 例如：ID=1 → names[0], ID=2 → names[1], ...
names = ['0', '1', '2']  # ←←← 请根据你的情况修改！


# ==================

def face_detect(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
    face_detector = cv2.CascadeClassifier(cascade_path)

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(100, 100),
        maxSize=(300, 300)
    )

    for (x, y, w, h) in faces:
        # 画圆形人脸框
        cv2.circle(img, center=(x + w // 2, y + h // 2), radius=w // 2, color=(0, 255, 0), thickness=2)

        # 人脸识别
        ids, confidence = recognizer.predict(gray[y:y + h, x:x + w])
        print(f'标签ID: {ids}, 置信评分: {confidence:.2f}')

        # 显示结果
        if confidence > 80:
            text = 'unknown'
        else:
            # 注意：ID 从 1 开始，names 索引从 0 开始
            name = names[ids - 1] if ids <= len(names) else 'unknown'
            text = name

        cv2.putText(img, text, (x + 10, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

    cv2.imshow('Face Recognition', img)


# 主程序
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("错误：无法打开摄像头！")
    exit()

print("按空格键退出...")

while True:
    ret, frame = cap.read()
    if not ret:
        print("无法获取帧")
        break

    face_detect(frame)

    # 按空格键退出
    if cv2.waitKey(1) & 0xFF == ord(' '):
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()