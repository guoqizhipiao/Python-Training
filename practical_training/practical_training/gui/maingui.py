#主界面
import tkinter

#主界面
class maingui:
    #启动函数
    def open_top_window(self):
        root = tkinter.Tk()
        root.title("主界面")
        # 获取屏幕宽度和高度
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        # 设定窗口大小
        window_width = int(screen_width * 0.5)
        window_height = int(screen_height * 0.5)
        # 计算窗口左上角坐标，使其居中
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        # 进入主循环
        root.mainloop()
