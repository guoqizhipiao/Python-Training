#数据库管理界面
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

#数据库管理界面
class databasegui:
    
    #启动函数
    def __init__(self):
        self.setup_ui()


    # 初始化界面
    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title("数据库")
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
        # 分割左右两栏
        self.left_frame = tk.Frame(self.root, width=300, bg="lightgray", padx=10, pady=10)
        self.left_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.right_frame = tk.Frame(self.root, bg="white")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        # 设置grid布局管理器网格权重
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        # ====================== 左侧：添加学生 ======================
        # 添加照片区域
        self.photo_label = tk.Label(self.left_frame, text="添加照片", font=("Arial", 12), relief="solid", borderwidth=2, width=20, height=8)
        self.photo_label.pack(pady=10)
        # 照片路径
        self.photo_path = ""
        # 点击添加照片
        self.photo_label.bind("<Button-1>", lambda e: self.select_photo())
        # 输入框
        tk.Label(self.left_frame, text="姓名：").pack(anchor="w", pady=5)
        self.name_entry = tk.Entry(self.left_frame, width=20)
        self.name_entry.pack(pady=5)
        tk.Label(self.left_frame, text="学号：").pack(anchor="w", pady=5)
        self.sid_entry = tk.Entry(self.left_frame, width=20)
        self.sid_entry.pack(pady=5)
        tk.Label(self.left_frame, text="身份证：").pack(anchor="w", pady=5)
        self.id_entry = tk.Entry(self.left_frame, width=20)
        self.id_entry.pack(pady=5)
        # 提交按钮
        self.submit_btn = tk.Button(self.left_frame, text="提交", command=self.add_student)
        self.submit_btn.pack(pady=10)
        # ====================== 右侧：搜索与显示 ======================

        # 让 right_frame 的行列可以伸展
        self.right_frame.grid_rowconfigure(1, weight=1)    # 第1行（Treeview 所在行）可以拉伸
        self.right_frame.grid_rowconfigure(0, weight=0)    # 第0行（顶部控件）固定高度
        self.right_frame.grid_columnconfigure(0, weight=1) # Treeview 所在列可以横向拉伸
        self.right_frame.grid_columnconfigure(1, weight=0) # 滚动条列固定宽度

        # ------------------- 1. 顶部区域 -------------------
        self.top_frame = tk.Frame(self.right_frame)
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(5, 10))
        self.top_frame.grid_columnconfigure(1, weight=1)  # 让中间空隙可以伸展（搜索框靠右）

        # 加载数据库按钮
        self.load_btn = tk.Button(self.top_frame, text="加载数据库", command=self.load_database)
        self.load_btn.grid(row=0, column=0, padx=(5, 10), pady=5, sticky="w")

        # 进度条（紧跟按钮右侧）
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.top_frame, variable=self.progress_var, maximum=100, length=200)
        self.progress_bar.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # 搜索区域（靠右对齐）
        self.search_frame = tk.Frame(self.top_frame)
        self.search_frame.grid(row=0, column=2, padx=(0, 5), pady=5, sticky="e")

        self.search_type = tk.StringVar(value="身份证")
        self.search_combo = ttk.Combobox(self.search_frame, textvariable=self.search_type, values=["身份证", "学号"], width=10)
        self.search_combo.pack(side="left", padx=5)

        self.search_entry = tk.Entry(self.search_frame, width=30)
        self.search_entry.pack(side="left", padx=5)

        self.search_btn = tk.Button(self.search_frame, text="搜索", command=self.search_student)
        self.search_btn.pack(side="left", padx=5)

        # ------------------- 2 & 3. 底部区域：Treeview + 滚动条 -------------------
        # Treeview 和滚动条放在第1行，分为两列
        self.tree = ttk.Treeview(self.right_frame, columns=("姓名", "学号", "身份证"), show="headings")
        self.tree.heading("姓名", text="姓名")
        self.tree.heading("学号", text="学号")
        self.tree.heading("身份证", text="身份证")
        self.tree.column("姓名", width=100, anchor="center")
        self.tree.column("学号", width=100, anchor="center")
        self.tree.column("身份证", width=150, anchor="center")

        # Treeview 放在第1行，第0列，允许伸展
        self.tree.grid(row=1, column=0, sticky="nsew", padx=(5, 0), pady=(0, 5))

        # 垂直滚动条放在第1行，第1列
        self.scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=1, column=1, sticky="ns", pady=(0, 5))

        # 关联滚动条与 Treeview
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # 初始加载数据
        self.update_list()


    # 选择照片函数
    def select_photo(self):
        file_path = filedialog.askopenfilename(
            title="选择照片",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")]
        )
        if file_path:
            self.photo_path = file_path
            print("选择", self.photo_path)
            # 可选：在标签上显示缩略图（这里简化处理）
            self.photo_label.config(text="✓ 已选择")

    # 添加学生信息函数
    def add_student(self):
        self.name = self.name_entry.get().strip()
        self.student_id = self.sid_entry.get().strip()
        self.id_number = self.id_entry.get().strip()
        if not self.name or not self.student_id or not self.id_number or not self.photo_path:
            print("缺少信息, 请填写姓名、学号、身份证并选择照片。")
            messagebox.showwarning("缺少信息", "请填写姓名、学号、身份证并选择照片。")
            return
        print("添加学生：", self.name, self.student_id, self.id_number, self.photo_path)
        messagebox.showinfo("成功", "学生信息添加成功！")

    def load_database(self):
        # 示例：添加一些测试数据
        self.test_data = [
            {"姓名": "张三测试", "学号": "2023001", "身份证": "110101199001011234", "照片": "/测试"},
            {"姓名": "李四测试", "学号": "2023002", "身份证": "110101199102021235", "照片": "/测试"},
            {"姓名": "王五测试", "学号": "2023003", "身份证": "110101199203031236", "照片": "/测试"}
        ]

    # 搜索学生信息函数
    def search_student(self):
        pass

    def update_list(self):
        # 清空树形控件
        for item in self.tree.get_children():
            self.tree.delete(item)




if __name__ == "__main__":
    dagui = databasegui()
    dagui.root.mainloop()