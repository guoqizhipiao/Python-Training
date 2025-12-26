#主界面
import tkinter as tk
from PIL import Image, ImageTk
import os

from . import databasegui
from . import opencvgui

gui_path = os.path.dirname(os.path.abspath(__file__))
guielements_path = os.path.join(gui_path, "guielements")

#主界面
class maingui:
    #启动函数
    def __init__(self):

        self.setup_ui()
        self.root.mainloop()


    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title("主界面")
    
        # 获取屏幕宽高
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
    
        # 设置窗口大小（70% 屏幕）
        window_width = int(self.screen_width * 0.7)
        window_height = int(self.screen_height * 0.7)
        x = (self.screen_width - window_width) // 2
        y = (self.screen_height - window_height) // 2
    
        self.root.minsize(800, 600)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    

        self.left_frame = tk.Frame(self.root)
        self.left_frame.grid(row=0, column=0,padx=20, pady=20, sticky="nsew")
        self.right_frame = tk.Frame(self.root)
        self.right_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.root.rowconfigure(0, weight=1)

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)

        try:
            print(os.path.join(guielements_path, "face_recognition.jpg"))
            face_img = Image.open(os.path.join(guielements_path, "face_recognition.jpg"))

            face_img = face_img.resize((400, 400), Image.Resampling.LANCZOS)  # 调整大小
            self.face_photo = ImageTk.PhotoImage(face_img)  # 必须保持引用，防止被回收
            left_image_label = tk.Label(self.left_frame, image=self.face_photo)
        except Exception as e:
            # 如果图片加载失败，显示占位文字
            left_image_label = tk.Label(self.left_frame, text="图片位置", font=("Arial", 14), fg="gray")

        left_image_label.grid(row=0, column=0, padx=10, pady=10)

        try:
            print(os.path.join(guielements_path, "data_base.jpg"))
            da_img = Image.open(os.path.join(guielements_path, "data_base.jpg"))

            da_img = da_img.resize((400, 400), Image.Resampling.LANCZOS)  # 调整大小
            self.da_photo = ImageTk.PhotoImage(da_img)  # 必须保持引用，防止被回收
            right_image_label = tk.Label(self.right_frame, image=self.da_photo)
        except Exception as e:
            # 如果图片加载失败，显示占位文字
            right_image_label = tk.Label(self.right_frame, text="图片位置", font=("Arial", 14), fg="gray")

        right_image_label.grid(row=0, column=0, padx=10, pady=10)

        # === 按钮区域 ===
        button_font = ("Arial", 16, "bold")
        button_width = 20
        button_height = 2

        self.db_btn = tk.Button(
            self.right_frame,
            text="数据库管理",
            command=self.database,
            font=button_font,
            width=button_width,
            height=button_height
        )
        self.db_btn.grid(row=1, column=0, padx=10, pady=10)

        self.face_btn = tk.Button(
            self.left_frame,
            text="人脸识别",
            command=self.opencv,
            font=button_font,
            width=button_width,
            height=button_height
        )
        self.face_btn.grid(row=1, column=0, padx=10, pady=10)

        
        self.left_frame.rowconfigure(0, weight=1)
        self.left_frame.rowconfigure(1, weight=1)
        self.left_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(0, weight=1)
        self.right_frame.rowconfigure(1, weight=1)
        self.right_frame.columnconfigure(0, weight=1)


       
    def database(self):
        self.database_window = databasegui.databasegui(self.root)

    def opencv(self):
        self.opencv_window = opencvgui.opencvgui(self.root)



if __name__ == "__main__":
    gui = maingui()