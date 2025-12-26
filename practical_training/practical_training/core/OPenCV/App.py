import sys
import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import threading
import os

# ======================
# 配置区（根据你的环境修改）
# ======================

opencv_path = os.path.dirname(os.path.abspath(__file__))

# 加载人脸识别模型

cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
face_detector = cv2.CascadeClassifier(cascade_path)


class FaceRecognitionApp:
    def __init__(self, root, recognizer, NAMES):
        self.recognizer = recognizer
        self.NAMES = NAMES
        self.root = root
        self.root.title("人脸识别系统")
        # 获取屏幕宽度和高度
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        # 设定窗口大小
        self.window_width = int(self.screen_width * 0.5)
        self.window_height = int(self.screen_height * 0.5)
        # 计算窗口左上角坐标，使其居中
        self.x = (self.screen_width - self.window_width) // 2
        self.y = (self.screen_height - self.window_height) // 2
        # 设置窗口最小宽度为 400，最小高度为 300
        self.root.minsize(400, 300)
        #设置大小和位置
        self.root.geometry(f"{self.window_width}x{self.window_height}+{self.x}+{self.y}")
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
                    ids, confidence = self.recognizer.predict(gray[y:y + h, x:x + w])
                    if confidence > 80:
                        text = "unknown"
                    else:
                        name = self.NAMES[ids - 1] if 1 <= ids <= len(self.NAMES) else "unknown"
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

    def show_about(self):
        messagebox.showinfo("关于", "人脸识别系统\n基于 OpenCV + LBPH\n作者：你自己 😊")

    def quit_app(self):
        self.app.stop_recognition()
        self.app.root.destroy()  # 销毁窗口







# ======================
# 主程序入口
# ======================
if __name__ == '__main__':
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.protocol("WM_DELETE_WINDOW", root.quit_app)  # 点×关闭时释放资源
    root.mainloop()