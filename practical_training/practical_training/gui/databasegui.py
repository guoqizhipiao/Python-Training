#主界面
import tkinter as tk

#主界面
class databasegui:
    
    #启动函数
    def open_top_window(self):
        root = tk.Tk()
        root.title("数据库")
        # 获取屏幕宽度和高度
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        # 设定窗口大小
        window_width = int(screen_width * 0.5)
        window_height = int(screen_height * 0.5)
        # 计算窗口左上角坐标，使其居中
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        # 设置窗口最小宽度为 400，最小高度为 300
        root.minsize(400, 300)
        #打开窗口，设置大小和位置
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        # 添加标签和输入框示例
        name = tk.StringVar()
        tk.Label(root, text="姓名：", width=1,height=1).place(x=1,y=1)
        tk.Entry(root, textvariable=name, width=20).place(x=20,y=1)




        # 进入主循环
        root.mainloop()
        





if __name__ == "__main__":
    dagui = databasegui().open_top_window()