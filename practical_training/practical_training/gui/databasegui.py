#数据库管理界面
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import os
import time
import threading
import queue

from core.databasecode.database import database

gui_path = os.path.dirname(os.path.abspath(__file__))
practical_training_path = os.path.dirname(gui_path) 

core_path = os.path.join(practical_training_path, 'core')
database_path = os.path.join(core_path, 'databasecode')
students_photo_path = os.path.join(database_path, "students_photos")

#数据库管理界面
class databasegui:
    
    #启动函数
    def __init__(self, maingui):
        self.data_queue = queue.SimpleQueue()
        self.load_database_count = False
        self.loading = 0
        self.maingui = maingui
        self.setup_ui()
        self.root.mainloop()


    # 初始化界面
    def setup_ui(self):
        self.root = tk.Toplevel(self.maingui)
        self.root.transient(self.maingui)
        #self.root = tk.Tk()
        self.root.title("数据库")
        # 获取屏幕宽度和高度
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        # 设定窗口大小
        self.window_width = int(self.screen_width * 0.6)
        self.window_height = int(self.screen_height * 0.6)
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
        self.progress_var = tk.DoubleVar(self.top_frame, value=0)
        self.progress_bar = ttk.Progressbar(self.top_frame, variable=self.progress_var, mode='determinate', maximum=100, length=200)
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
        self.tree = ttk.Treeview(self.right_frame, columns=("身份证", "姓名", "学号"), show="headings")
        self.tree.heading("身份证", text="身份证")
        self.tree.heading("姓名", text="姓名")
        self.tree.heading("学号", text="学号")
        self.tree.column("身份证", width=100, anchor="center")
        self.tree.column("姓名", width=100, anchor="center")
        self.tree.column("学号", width=100, anchor="center")
      

        # Treeview 放在第1行，第0列，允许伸展
        self.tree.grid(row=1, column=0, sticky="nsew", padx=(5, 0), pady=(0, 5))
        # 垂直滚动条放在第1行，第1列
        self.scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=1, column=1, sticky="ns", pady=(0, 5))
        # 关联滚动条与 Treeview
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # 绑定点击事件
        self.tree.bind("<ButtonRelease-1>", self.on_student_select)

        # 清空Treeview
        self.update_list()

        '''# 调试按钮
        self.btn = ttk.Button(self.top_frame, text="调试", command=self.debug)
        self.btn.grid(row=1, column=1, padx=10)'''



    def schedule_check_queue(self):
        self.check_queue()
        if self.loading > 0:  # 如果还在加载，继续调度
            self.root.after(50, self.schedule_check_queue)  # 每50ms检查一次

    def check_queue(self):
        try:
            while True:  # 快速清空当前所有消息（但不阻塞）
                msg_type, queue_data = self.data_queue.get_nowait()
                if msg_type == 'tree_insert':
                    data = queue_data[0]
                    progress = queue_data[1]
                    print("插入数据：", data)
                    self.tree.insert("", "end", values=(data[0], data[1], data[2]))
                    print("进度条：", progress)
                    self.progress_var.set(progress)

                elif msg_type == 'load_database_done':
                    print("加载完成")
                    self.load_database_count = False
                    self.loading -= 1  # 在主线程安全地更新
                    return  # 停止本次检查（但不会阻塞）
        except queue.Empty:
            pass  # 队列空了，正常退出

    # 选择照片函数
    def select_photo(self):
        self.file_path = filedialog.askopenfilename(
            title="选择照片",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")]
        )
        if self.file_path:
            self.photo_path = self.file_path
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
        self.da = database()
        return_message = self.da.add_student(self.id_number, self.name, self.student_id, self.photo_path)

        if return_message == "NOFACE":
            messagebox.showerror("错误", "照片中未检测到人脸，请选择其他照片。")
            return
        elif return_message == "REPEAT":
            messagebox.showerror("错误", "该学生信息已存在，无法重复添加。")
            return
        elif return_message == "SUCCESS":
            messagebox.showinfo("成功", "学生信息添加成功！")
        else:
            messagebox.showerror("错误", f"添加学生信息失败：{return_message}")
            return
        

    def load_database(self):
        self.da = database()
        self.count = self.da.get_student_count()
        print("学生总数：", self.count)
        if self.count == 0:
            self.update_list()
            self.tree.insert("", "end", values=("","未有数据",""))
            return
        elif self.load_database_count:
            print("正在加载")
        else:
            self.load_database_count = True
            self.update_list()  # 清空列表
            self.progress_var.set(0)
            self.thread = threading.Thread(target=self.load_data_thread, args=(self.da,))
            self.thread.daemon = True
            self.thread.start()
            self.loading += 1
            # 启动非阻塞的队列检查
            self.schedule_check_queue()
    

    def load_data_thread(self, da):
        self.step = 0
        for self.s1 in da.iter_show_students():
            self.step += 1
            self.progress = (self.step / self.count) * 100
            print(self.progress, self.s1)
            self.data_queue.put(('tree_insert', (self.s1, self.progress)))
            #time.sleep(0.5)  # 模拟耗时
        print("正在load_database_done")
        self.data_queue.put(('load_database_done', None))

    def on_student_select(self, event):



        print("点击", event)
        selection = self.tree.selection()
        if not selection:
            return
        print(selection)


        item = self.tree.item(selection[0])
        print("选中项：", item)

        print("选中学生信息：", item['values'])
        da = database()
        id_to_query = item['values'][0]
        print(f"正在查询身份证号/学号: {repr(id_to_query)} (类型: {type(id_to_query)})")
        student =  self.da.find_show_students_idnumber(id_to_query)
        if student is None:
            print("未找到该学生信息")
            self.tree.selection_remove(self.tree.selection())
            return
        print("完整学生信息：", student)
        self.show_studet_data_window(student)
        self.tree.selection_remove(self.tree.selection())

    def deletes(self, data):
        delete_window = tk.Toplevel(self.root)
        delete_window.title("删除确认")
        delete_window.transient(self.studet_data_window)
        x = (self.screen_width - 200) // 2
        y = (self.screen_height - 150) // 2
        delete_window.geometry(f"200x150+{x}+{y}")
        
        tk.Label(delete_window, text="确定要删除该学生的信息吗？").pack(pady=10)
        confirm_button = tk.Button(delete_window, text="确认",
                                    command=lambda: self.confirm_delete(data, delete_window))
        confirm_button.pack(side="left", padx=10, pady=10)
        cancel_button = tk.Button(delete_window, text="取消", command=delete_window.destroy)
        cancel_button.pack(side="right", padx=10, pady=10)
    
    def confirm_delete(self, data, delete_window):
        da = database()
        da.delete_student_idnumber(data[0])
        delete_window.destroy()
        self.studet_data_window.destroy()
        return 


    def show_studet_data_window(self, data):
        try:
            self.studet_data_window = tk.Toplevel(self.root)
            self.studet_data_window.title(f"学生详情 - {data[1]}")
            self.studet_data_window_x = (self.screen_width - 400) // 2
            self.studet_data_window_y = (self.screen_height - 500) // 2
            self.studet_data_window.geometry(f"400x500+{self.studet_data_window_x}+{self.studet_data_window_y}")
            try:
                pphhoottoo = os.path.join(students_photo_path,data[3])
                self.img = Image.open(pphhoottoo)
                self.img = self.img.resize((150, 200), Image.Resampling.LANCZOS)
                self.photo = ImageTk.PhotoImage(self.img)
                self.label_img = tk.Label(self.studet_data_window, image=self.photo)
                self.label_img.image = self.photo  # 防止被垃圾回收
                self.label_img.pack(pady=10)
            except Exception as e:
                tk.Label(self.studet_data_window, text="照片加载失败", fg="red").pack()
            stext = f"""
    姓名：{data[1]}
    身份证：{data[0]}
    学号：{data[2]}""".strip()
            tk.Label(self.studet_data_window, text=stext, justify="left", font=("Arial", 12)).pack(pady=10)
            tk.Button(self.studet_data_window, text="删除", command=lambda: self.deletes(data)).pack(pady=10)
        except Exception as e:
            self.tree.selection_remove(self.tree.selection())
            return


    # 搜索学生信息函数
    def search_student(self):
        self.current_value = self.search_type.get().strip()
        search_value = self.search_entry.get().strip()
        print("搜索值：", search_value)
        print("搜索类型：", self.current_value)
        if not search_value:
            return
        self.da = database()
        if self.current_value == "身份证":
            return_message = self.da.find_show_students_idnumber(search_value)
            
        elif self.current_value == "学号":
            return_message = self.da.find_show_students_studentid(search_value)
        if return_message is None:
            self.update_list()
            self.tree.insert("", "end", values=("", "未找到该学生信息", ""))
            return
        else:
            print("搜索结果：", return_message)
            self.update_list()  # 清空列表
            self.tree.insert("", "end", values=(return_message[0], return_message[1], return_message[2]))
            return

    def update_list(self):
        # 清空树形控件
        for item in self.tree.get_children():
            self.tree.delete(item)

    def debug(self):
        # 弹出对话框输入进度
        self.user_input = simpledialog.askstring("输入进度", "请输入 0-100 的百分比：")
        if self.user_input is not None:
            self.value = float(self.user_input)
            self.progress_var.set(self.value)
            self.root.update_idletasks()


if __name__ == "__main__":
    dagui = databasegui()
    dagui.root.mainloop()