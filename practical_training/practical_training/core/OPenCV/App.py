import sys
import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import threading

# ======================
# 配置区（根据你的环境修改）
# ======================
TRAINER_PATH = r'D:\OPenCV\trainer\trainer.yml'
NAMES = ['0', '1', 'zhuwanli']  # ID 1 → NAMES[0]

# 加载人脸识别模型
try:
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(TRAINER_PATH)
except Exception as e:
    messagebox.showerror("错误", f"无法加载训练模型:\n{e}")
    sys.exit(1)

cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
face_detector = cv2.CascadeClassifier(cascade_path)


class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("人脸识别系统")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # 创建菜单
        self.menu = TopMenu(self)
        self.root.config(menu=self.menu)

        # 视频显示区域
        self.video_label = tk.Label(root, bg='black')
        self.video_label.pack(expand=True, fill=tk.BOTH)

        # 控制变量
        self.is_running = False
        self.cap = None

        # 启动后自动开始识别（可选）
        # self.start_recognition()

    def start_recognition(self):
        if not self.is_running:
            self.is_running = True
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("错误", "无法打开摄像头！")
                self.is_running = False
                return
            self.update_frame()

    def stop_recognition(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.video_label.config(image='')  # 清空画面

    def update_frame(self):
        if not self.is_running:
            return

        ret, frame = self.cap.read()
        if ret:
            # 人脸识别处理
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5,
                minSize=(100, 100), maxSize=(300, 300)
            )

            for (x, y, w, h) in faces:
                # 画圆形框
                center = (x + w // 2, y + h // 2)
                radius = w // 2
                cv2.circle(frame, center, radius, (0, 255, 0), 2)

                # 预测
                try:
                    ids, confidence = recognizer.predict(gray[y:y + h, x:x + w])
                    if confidence > 80:
                        text = "unknown"
                    else:
                        name = NAMES[ids - 1] if 1 <= ids <= len(NAMES) else "unknown"
                        text = name
                    cv2.putText(frame, text, (x + 10, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                except Exception as e:
                    print("预测出错:", e)

            # 转为 PIL 图像并在 Tkinter 中显示
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        # 每 20ms 更新一帧
        self.video_label.after(20, self.update_frame)


class TopMenu(tk.Menu):
    def __init__(self, app: FaceRecognitionApp):
        super().__init__()
        self.app = app
        self.file_menu()
        self.operation_menu()
        self.help_menu()

    def file_menu(self):
        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(label='退出', command=self.quit_app)
        self.add_cascade(label='文件', menu=file_menu)

    def operation_menu(self):
        op_menu = tk.Menu(self, tearoff=False)
        op_menu.add_command(label='启动识别', command=self.app.start_recognition)
        op_menu.add_command(label='停止识别', command=self.app.stop_recognition)
        self.add_cascade(label='操作', menu=op_menu)

    def help_menu(self):
        help_menu = tk.Menu(self, tearoff=False)
        help_menu.add_command(label='关于', command=self.show_about)
        self.add_cascade(label='帮助', menu=help_menu)

    def quit_app(self):
        self.app.stop_recognition()
        self.app.root.quit()
        sys.exit()

    def show_about(self):
        messagebox.showinfo("关于", "人脸识别系统\n基于 OpenCV + LBPH\n作者：你自己 😊")


# ======================
# 主程序入口
# ======================
if __name__ == '__main__':
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop_recognition)  # 点×关闭时释放资源
    root.mainloop()