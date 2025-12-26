#主界面
import tkinter as tk

from . import databasegui
from . import opencvgui

#主界面
class maingui:
    #启动函数
    def __init__(self):

        self.setup_ui()
        self.root.mainloop()


    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title("主界面")
        # 获取屏幕宽度和高度
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        # 设定窗口大小
        window_width = int(self.screen_width * 0.7)
        window_height = int(self.screen_height * 0.7)
        # 计算窗口左上角坐标，使其居中
        x = (self.screen_width - window_width) // 2
        y = (self.screen_height - window_height) // 2
        # 设置窗口最小宽度为 400，最小高度为 300
        self.root.minsize(400, 300)
        #打开窗口，设置大小和位置
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        # 进入主循环

        # 按钮
        self.submit_btn = tk.Button(self.root, text="数据库管理", command=self.database)
        self.submit_btn.place(x=100,y=100)

        self.submit_btn = tk.Button(self.root, text="人脸识别", command=self.opencv)
        self.submit_btn.place(x=200,y=200)


       
    def database(self):
        self.database_window = databasegui.databasegui(self.root)

    def opencv(self):
        self.opencv_window = opencvgui.opencvgui(self.root)



if __name__ == "__main__":
    gui = maingui()