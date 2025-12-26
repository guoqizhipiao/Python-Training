import tkinter as tk
from tkinter import filedialog, ttk
import numpy as np
import os
from pathlib import Path

#from core.OPenCV.App import 

gui_path = os.path.dirname(os.path.abspath(__file__))
practical_training_path = os.path.dirname(gui_path)

core_path = os.path.join(practical_training_path, 'core')
opencv_path = os.path.join(core_path, 'OPenCV')

trainer_path = os.path.join(opencv_path, 'trainer')

core_path = os.path.dirname(opencv_path)
os.sys.path.append(practical_training_path)

from core.facerecognition.facedatamatch import face_data_match
from core.OPenCV.trainmodel import database_train_model
from core.OPenCV.database_camera import camera

class opencvgui:
    
    #启动函数
    def __init__(self, maingui):
        self.current_model = ""
        self.photo_path = ""
        self.maingui = maingui
        self.setup_ui()
        self.root.mainloop()

    # 初始化界面
    def setup_ui(self):
        self.root = tk.Toplevel(self.maingui)
        self.root.transient(self.maingui)
        #self.root = tk.Tk()
        self.root.title("人脸识别")
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

        # =================== 左侧区域 ===================
        # 已选择模型标签

        self.model_label = tk.Label(self.left_frame, text="查询数据库", font=("Arial", 12), bg="lightgray")
        self.model_label.pack(pady=5)

        # 添加照片区域
        self.photo_label = tk.Label(self.left_frame, text="添加照片", font=("Arial", 12), relief="solid", borderwidth=2, width=20, height=8)
        self.photo_label.pack(pady=10)
        # 照片路径
        self.photo_path = ""
        # 点击添加照片
        self.photo_label.bind("<Button-1>", lambda e: self.select_photo())

        # 人脸识别按钮
        tk.Button(self.left_frame, text="人脸识别", font=("Arial", 12), command=self.face_recognition).pack(pady=5)

        # 识别信息展示框
        self.info_text = tk.Text(self.left_frame, width=30, height=40, font=("Arial", 10))
        self.info_text.pack(pady=10)
        self.info_text.insert(tk.END, "识别结果将显示在此处...")

        # =================== 右侧区域 ===================

        self.top_frame = tk.Frame(self.right_frame)
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(5, 10))


        self.camera_button = tk.Button(self.top_frame, text="使用摄像头", command=self.start_camera)
        self.camera_button.grid(row=0, column=0, padx=(5, 10), pady=5, sticky="w")

        self.camera_button = tk.Button(self.top_frame, text="刷新模型列表", command=self.refresh_model_list)
        self.camera_button.grid(row=0, column=1, padx=(5, 10), pady=5, sticky="w")

        self.model_label = tk.Label(self.top_frame, text="选择LBPH模型：", font=("Arial", 12), bg="lightgray")
        self.model_label.grid(row=0, column=2, padx=(5, 10), pady=5, sticky="w")

        self.trainmodel_button = tk.Button(self.top_frame, text="训练LBPH模型", command=self.train_model)
        self.trainmodel_button.grid(row=0, column=3, padx=(5, 10), pady=5, sticky="e")

        self.top_frame.columnconfigure(0, weight=1)
        self.top_frame.columnconfigure(3, weight=1)


        self.tree = ttk.Treeview(self.right_frame, columns=("LBPH模型名称"), show="headings")
        self.tree.heading("LBPH模型名称", text="LBPH模型名称")
        self.tree.column("LBPH模型名称", width=100, anchor="center")
      

        # Treeview 放在第1行，第1列，允许伸展
        self.tree.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=(0, 5))
        # 垂直滚动条放在第1行，第2列
        self.scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=1, column=2, sticky="ns", pady=(0, 5))
        # 关联滚动条与 Treeview
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.update_list()

        self.tree.bind("<Button-1>", self.on_tree_click)
        self.tree.bind("<ButtonRelease-1>", self.on_model_select)
        self.tree.bind("<Button-3>", self.on_right_click)


        self.add_sample_models()

        self.right_frame.rowconfigure(1, weight=1)
        self.right_frame.columnconfigure(0, weight=0)
        self.right_frame.columnconfigure(1, weight=1)
        self.right_frame.columnconfigure(2, weight=0)



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

    #人脸识别函数
    def face_recognition(self):
        if not self.photo_path:
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, "请先选择一张照片进行识别。\n")
            return
        return_message = face_data_match(self.photo_path)
        if return_message == "PHOTOINVALID":
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, "照片路径无效，请选择有效的照片后重试。\n")
            return
        elif return_message == "NOFACE":
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, "照片中未检测到人脸，请更换照片后重试。\n")
            return
        elif return_message == "DBNOTFOUND":
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, "数据库文件不存在，请先初始化数据库。\n")
            return
        elif isinstance(return_message, tuple) and return_message[0] == "SUCCESS":
            id_number, name, student_id = return_message[1], return_message[2], return_message[3]
            confidence = return_message[5]
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"识别成功！\n欧氏距离：{confidence:.2f} ∈ [0,√2]\n身份证号: {id_number}\n姓名: {name}\n学号: {student_id}\n")
        elif return_message == "NOMATCH":
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, "未匹配到已注册的学生。\n")

    #启动摄像头
    def start_camera(self):
        camera(self.root, self.current_model)

    #训练模型
    def train_model(self):
        database_train_model()
        self.refresh_model_list()

    # 清空树形控件
    def update_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    # 刷新模型列表
    def refresh_model_list(self):
        self.update_list()
        self.add_sample_models()

    def add_sample_models(self):
        print(trainer_path)
        path_trainer_path = Path(trainer_path)
        yml_files = tuple(path_trainer_path.glob("*.yml"))
        print(yml_files)

        one_current_model = 0
        for model in yml_files:
            filename = model.name

            if one_current_model == 0:
                self.current_model = filename
                self.model_label.config(text=f"已选择LBPH模型：{filename}")
                one_current_model = 1

            self.tree.insert("", "end", text=filename, values=(filename,))


    def on_model_select(self, event):
        """当用户选择模型时触发"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            print(item)
            item
            model_name = item["text"]
            self.current_model = model_name
            print(f"选择LBPH模型: {model_name}")
            self.model_label.config(text=f"已选择LBPH模型：{model_name}")

    def on_tree_click(self, event):
        """处理 Treeview 左键点击，用于检测是否点击空白区域"""
        # 获取点击位置对应的 item
        item = self.tree.identify_row(event.y)
        if not item:  # 点击的是空白区域
            self.tree.selection_remove(self.tree.selection())
            self.current_model = None
            self.model_label.config(text="未选择模型")
            print("点击空白区域，已取消选择")

    def on_right_click(self, event):
        """右键点击事件，显示上下文菜单"""
        # 获取鼠标点击位置对应的 item ID
        item_id = self.tree.identify_row(event.y)
    
        if item_id:
            # 可选：高亮/选中该项（让用户知道点的是谁）
            self.tree.selection_set(item_id)  # 这会取消其他选中，只选中当前项
            self.tree.focus(item_id)          # 确保焦点也在该项上（可选但推荐）

            item = self.tree.item(item_id)
            model_name = item["text"]
        
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="删除模型", command=lambda: self.delete_model(model_name))
            menu.post(event.x_root, event.y_root)
            print(f"右键点击LBPH模型: {model_name}")
        else:
            self.tree.selection_remove(self.tree.selection())

    def delete_model(self, model_name):
        print(f"删除LBPH模型: {model_name}")
        model_path = os.path.join(trainer_path, model_name)
        json_path = os.path.splitext(model_path)[0] + ".json"

        if os.path.exists(model_path):
            os.remove(model_path)
            print(f"已删除模型文件: {model_path}")
        else:
            print(f"模型文件不存在: {model_path}")

        if os.path.exists(json_path):
            os.remove(json_path)
            print(f"已删除JSON文件: {json_path}")
        else:
            print(f"JSON文件不存在: {json_path}")
        self.refresh_model_list()
