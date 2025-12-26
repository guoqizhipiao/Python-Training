import sys
import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk,ImageDraw,ImageFont
import threading
import os
import json
import numpy as np
from collections import deque
import time
# ======================
# 配置区（根据你的环境修改）
# ======================

opencv_path = os.path.dirname(os.path.abspath(__file__))
core_path = os.path.dirname(opencv_path)
practical_training_path = os.path.dirname(core_path)
sys.path.append(practical_training_path)

from core.facerecognition.facedatamatch import face_data_match_from_frame

# 加载人脸识别模型

cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
face_detector = cv2.CascadeClassifier(cascade_path)


class FaceRecognitionApp:
    def __init__(self, root, recognizer, NAMES):

        self.frame_deque = deque()
        self.frame_deque_lock = threading.Lock()  # 添加锁
        self.face_data_match_deque = deque()
        self.face_data_match_lock = threading.Lock()  # 添加锁

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

        #self.start_recognition()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.video_label.config(image='')
        self.root.destroy()


    def start_recognition(self):
        print(self.recognizer)
        for i in self.NAMES:
            print(i,self.NAMES[i])
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
        print("启动多线程人脸识别")

        self.match_confidence = 0
        self.cv2_confidence = 0
        self.cv2_text = ""
        self.match_text = ""

        self.t1 = threading.Thread(target=self.face_data_match_from_frame_thread, daemon=True)
        self.t1.start()
        self.update_frame_main()


    def update_frame_main(self):
        if not self.is_running:
            return

        # 清空队列，保持最新一帧
        while len(self.frame_deque) > 1:
            self.frame_deque.pop()

        ret, frame = self.cap.read()
        if ret: 
            # 将当前帧放入队列
            self.frame_deque.append(frame)
            cv2_return = self.cv2_face_recognize(frame)

            if cv2_return:
                w1, w2 = 0.7, 0.3
                frame, self.cv2_text, self.cv2_confidence, x, y = cv2_return
                #print("OpenCV识别结果:", self.cv2_text, self.cv2_confidence)
                self.cv2_confidence = 1 - (self.cv2_confidence/80)
                self.cv2_confidence = w2 * self.cv2_confidence
                text =  self.cv2_text
                if len(self.face_data_match_deque) > 0:

                    with self.face_data_match_lock:
                        match_result = self.face_data_match_deque.pop()

                    if isinstance(match_result, tuple) and match_result[0] == "SUCCESS":
                        self.match_text = match_result[2]
                        self.match_confidence = match_result[5]

                        self.match_confidence = 1 - (self.match_confidence / 0.4)
                        self.match_confidence = w1 * self.match_confidence

                    elif match_result == "NOMATCH":
                        self.match_text = "未知人员"

                print("==========opencv识别结果:", self.cv2_text, self.cv2_confidence)
                print("==========math识别结果:", self.match_text, self.match_confidence)

                if self.match_text == self.cv2_text:
                    text = self.match_text
                elif self.match_text != self.cv2_text:
                    if self.match_confidence > self.cv2_confidence:
                        text = self.match_text
                    else:
                        text = self.cv2_text
                elif self.match_text == "未知人员":
                    text = self.match_text

                frame = self.cv2_putText_chinese(
                frame,
                text,
                pos=(x + 10, y - 30),  # 注意：PIL 的 y 坐标可能需要微调（比 OpenCV 高一点）
                font_path="simsun.ttc",  # Windows 系统宋体
                font_size=24,
                color=(0, 255, 0))

            # 转为 PIL 图像并在 Tkinter 中显示
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        # 每 20ms 更新一帧
        self.video_label.after(20, self.update_frame_main)


    def cv2_face_recognize(self, frame):

            # 人脸识别处理
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(
                gray, scaleFactor=1.2, minNeighbors=5,
                minSize=(60, 60), maxSize=(1000, 1000)
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
                        confidence = 80
                        text = "未知人员"
                    else:
                        name = self.NAMES.get(str(ids), "未知人员")
                        text = name

                    return (frame, text, confidence, x, y)
                    break

                except Exception as e:
                    print("预测出错:", e)

    def face_data_match_from_frame_thread(self):
        if not self.is_running:
            return
        while self.is_running:
            if len(self.frame_deque) == 0:
                time.sleep(0.05)
                continue
            # 获取最新一帧
            with self.frame_deque_lock:
                frame = self.frame_deque[-1].copy()
            # 调用匹配函数
            result = face_data_match_from_frame(frame)
            if result == "NOFACE":
                print("未检测到人脸")
            elif isinstance(result, tuple) and result[0] == "SUCCESS":
                print("识别结果:", result)
                time.sleep(1)  # 控制处理频率
            elif result == "NOMATCH":
                print("没有匹配到已注册的学生")
                time.sleep(1)  # 控制处理频率

            with self.face_data_match_lock:
                self.face_data_match_deque.append(result)


    def cv2_putText_chinese(self, img, text, pos, font_path="simsun.ttc", font_size=30, color=(0, 255, 0)):
        """
        在 OpenCV 图像上绘制中文
    
        参数:
            img: OpenCV 图像 (BGR 格式)
            text: 要绘制的中文文本
            pos: 文本左上角坐标 (x, y)
            font_path: 中文字体文件路径（Windows 常用 simsun.ttc 或 msyh.ttc）
            font_size: 字体大小
            color: BGR 颜色 (注意：OpenCV 是 BGR，PIL 是 RGB，这里做转换)
        """
        # 将 OpenCV 的 BGR 图像转为 RGB（供 PIL 使用）
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
    
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            # 如果指定字体找不到，使用默认字体（可能仍不支持中文）
            font = ImageFont.load_default()
            print("警告：未找到中文字体，中文可能显示为方框。")
    
        # PIL 使用 RGB，所以要把 BGR 的 color 转成 RGB
        rgb_color = (color[2], color[1], color[0])  # BGR → RGB
        draw.text(pos, text, fill=rgb_color, font=font)
    
        # 转回 OpenCV 的 BGR 格式
        img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        return img_cv

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



def camera(oprnvvgui,current_model):
    try:
        trainer_path = os.path.join(opencv_path, 'trainer', current_model)
        print("加载模型路径:", trainer_path)
        time_name = os.path.splitext(trainer_path)[0]
        json_path = f"{time_name}.json"
        with open(json_path, 'r', encoding='utf-8') as f:
            NAMES = json.load(f)
        for i in NAMES:
            print(f"加载姓名: ID={i}, 姓名={NAMES[i]}") 

        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.read(trainer_path)
        except Exception as e:
            messagebox.showerror("错误", f"无法加载训练模型:\n{e}")

        root = tk.Toplevel(oprnvvgui)
        app = FaceRecognitionApp(root,recognizer,NAMES)
        root.mainloop()
    except Exception as e:
        print("启动摄像头失败:", e)



# ======================
# 主程序入口
# ======================
if __name__ == '__main__':
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.protocol("WM_DELETE_WINDOW", root.quit_app)  # 点×关闭时释放资源
    root.mainloop()