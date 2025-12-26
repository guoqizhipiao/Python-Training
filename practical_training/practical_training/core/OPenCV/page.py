import sys
import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, ttk
import cv2
from PIL import Image, ImageTk
import os
import json

# ======================
# 配置区
# ======================
BASE_DIR = r'D:\OPenCV'
TRAINER_PATH = os.path.join(BASE_DIR, 'trainer', 'trainer.yml')
DATASET_PATH = os.path.join(BASE_DIR, 'dataset')
NAMES_JSON = os.path.join(BASE_DIR, 'names.json')

# 确保目录存在
os.makedirs(DATASET_PATH, exist_ok=True)
os.makedirs(os.path.dirname(TRAINER_PATH), exist_ok=True)

# 加载 names.json（ID -> 姓名）
def load_names():
    if os.path.exists(NAMES_JSON):
        with open(NAMES_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # 默认保留 ID 0 和 1（可选）
        default = {"0": "unknown", "1": "admin"}
        save_names(default)
        return default

def save_names(names_dict):
    with open(NAMES_JSON, 'w', encoding='utf-8') as f:
        json.dump(names_dict, f, ensure_ascii=False, indent=4)

# 全局 NAMES 字典
NAMES = load_names()

# 加载人脸识别模型（可选）
recognizer = None
if os.path.exists(TRAINER_PATH):
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(TRAINER_PATH)
    except Exception as e:
        print("模型加载失败:", e)

cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
face_detector = cv2.CascadeClassifier(cascade_path)


class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("人脸识别系统")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        self.menu = TopMenu(self)
        self.root.config(menu=self.menu)

        self.video_label = tk.Label(root, bg='black')
        self.video_label.pack(expand=True, fill=tk.BOTH)

        self.is_running = False
        self.cap = None
        self.is_collecting = False
        self.collect_id = None
        self.collect_count = 0
        self.max_samples = 50

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
        self.is_collecting = False
        if self.cap:
            self.cap.release()
        self.video_label.config(image='')

    def start_face_collection(self):
        """自动分配 ID 并开始录入"""
        global NAMES
        # 自动计算下一个 ID（跳过 0，从 1 开始）
        existing_ids = [int(k) for k in NAMES.keys() if k.isdigit()]
        next_id = max(existing_ids) + 1 if existing_ids else 1

        name = simpledialog.askstring("录入人脸", f"将分配 ID: {next_id}\n请输入姓名：", parent=self.root)
        if not name or not name.strip():
            return
        name = name.strip()

        # 更新 NAMES 字典
        NAMES[str(next_id)] = name
        save_names(NAMES)

        # 创建数据目录
        user_dir = os.path.join(DATASET_PATH, str(next_id))
        os.makedirs(user_dir, exist_ok=True)

        # 开始采集
        self.is_collecting = True
        self.collect_id = next_id
        self.collect_count = 0
        if not self.is_running:
            self.start_recognition()
        messagebox.showinfo("提示", f"开始采集 {name} (ID={next_id}) 的人脸...\n将保存 {self.max_samples} 张图像。")

    def update_frame(self):
        if not self.is_running:
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5,
            minSize=(100, 100), maxSize=(300, 300)
        )

        for (x, y, w, h) in faces:
            center = (x + w // 2, y + h // 2)
            radius = w // 2
            color = (0, 255, 0)

            if self.is_collecting and self.collect_count < self.max_samples:
                face_img = gray[y:y+h, x:x+w]
                filename = os.path.join(DATASET_PATH, str(self.collect_id), f"{self.collect_count}.jpg")
                cv2.imwrite(filename, face_img)
                self.collect_count += 1
                color = (255, 0, 0)
                cv2.putText(frame, f"Collecting: {self.collect_count}/{self.max_samples}",
                            (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

                if self.collect_count >= self.max_samples:
                    self.is_collecting = False
                    messagebox.showinfo("完成", f"人脸采集完成！\n请使用“训练模型”更新识别器。")

            cv2.circle(frame, center, radius, color, 2)

            if not self.is_collecting and recognizer is not None:
                try:
                    ids, confidence = recognizer.predict(gray[y:y + h, x:x + w])
                    if confidence > 80:
                        text = "unknown"
                    else:
                        text = NAMES.get(str(ids), "unknown")
                    cv2.putText(frame, text, (x + 10, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                except Exception as e:
                    print("预测出错:", e)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

        self.video_label.after(20, self.update_frame)

    def open_user_manager(self):
        UserManagerWindow(self.root)


class UserManagerWindow:
    def __init__(self, parent):
        self.window = Toplevel(parent)
        self.window.title("用户管理")
        self.window.geometry("400x400")
        self.window.transient(parent)
        self.window.grab_set()

        # Treeview 显示用户
        columns = ("ID", "姓名")
        self.tree = ttk.Treeview(self.window, columns=columns, show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("姓名", text="姓名")
        self.tree.column("ID", width=80, anchor='center')
        self.tree.column("姓名", width=250, anchor='center')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 按钮
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="修改姓名", command=self.edit_name).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="删除用户", command=self.delete_user).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="关闭", command=self.window.destroy).pack(side=tk.LEFT, padx=5)

        self.load_users()

    def load_users(self):
        # 清空
        for item in self.tree.get_children():
            self.tree.delete(item)
        # 加载
        for id_str, name in sorted(NAMES.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999):
            if id_str == "0":  # 跳过 unknown
                continue
            self.tree.insert("", "end", values=(id_str, name))

    def edit_name(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一个用户")
            return
        item = self.tree.item(selected[0])
        old_id, old_name = item['values']
        new_name = simpledialog.askstring("修改姓名", f"ID {old_id} 当前姓名: {old_name}", initialvalue=old_name)
        if new_name and new_name.strip():
            global NAMES
            NAMES[str(old_id)] = new_name.strip()
            save_names(NAMES)
            self.load_users()
            messagebox.showinfo("成功", "姓名已更新")

    def delete_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一个用户")
            return
        item = self.tree.item(selected[0])
        user_id, name = item['values']
        if user_id == "0":
            return
        if messagebox.askyesno("确认删除", f"确定要删除用户 {user_id} ({name}) 吗？\n这将同时删除其人脸图像！"):
            global NAMES
            # 删除 dataset 中的文件夹
            user_dir = os.path.join(DATASET_PATH, str(user_id))
            if os.path.exists(user_dir):
                import shutil
                shutil.rmtree(user_dir)
            # 删除 names.json 中的记录
            NAMES.pop(str(user_id), None)
            save_names(NAMES)
            self.load_users()
            messagebox.showinfo("成功", "用户已删除")


class TopMenu(tk.Menu):
    def __init__(self, app: FaceRecognitionApp):
        super().__init__()
        self.app = app
        self.file_menu()
        self.operation_menu()
        self.user_menu()
        self.help_menu()

    def file_menu(self):
        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(label='退出', command=self.quit_app)
        self.add_cascade(label='文件', menu=file_menu)

    def operation_menu(self):
        op_menu = tk.Menu(self, tearoff=False)
        op_menu.add_command(label='启动识别', command=self.app.start_recognition)
        op_menu.add_command(label='停止识别', command=self.app.stop_recognition)
        op_menu.add_separator()
        op_menu.add_command(label='录入人脸', command=self.app.start_face_collection)
        op_menu.add_command(label='训练模型', command=self.train_model)
        self.add_cascade(label='操作', menu=op_menu)

    def user_menu(self):
        user_menu = tk.Menu(self, tearoff=False)
        user_menu.add_command(label='用户管理', command=self.app.open_user_manager)
        self.add_cascade(label='用户', menu=user_menu)

    def help_menu(self):
        help_menu = tk.Menu(self, tearoff=False)
        help_menu.add_command(label='关于', command=self.show_about)
        self.add_cascade(label='帮助', menu=help_menu)

    def quit_app(self):
        self.app.stop_recognition()
        self.app.root.quit()
        sys.exit()

    def show_about(self):
        messagebox.showinfo("关于", "人脸识别系统\n基于 OpenCV + LBPH\n作者：Zhu 😊")

    def train_model(self):
        from cv2 import face
        import numpy as np

        faces = []
        ids = []

        if not os.path.exists(DATASET_PATH):
            messagebox.showwarning("警告", "数据集目录不存在！")
            return

        for root, dirs, files in os.walk(DATASET_PATH):
            for file in files:
                if file.lower().endswith(('.jpg', '.png')):
                    path = os.path.join(root, file)
                    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                    id_ = int(os.path.basename(root))
                    faces.append(img)
                    ids.append(id_)

        if len(faces) == 0:
            messagebox.showwarning("警告", "未找到任何人脸图像！")
            return

        recognizer_train = face.LBPHFaceRecognizer_create()
        recognizer_train.train(faces, np.array(ids))
        recognizer_train.save(TRAINER_PATH)

        # 重新加载全局 recognizer
        global recognizer
        recognizer = face.LBPHFaceRecognizer_create()
        recognizer.read(TRAINER_PATH)

        messagebox.showinfo("成功", f"模型训练完成并已加载！\n共训练 {len(set(ids))} 个用户。")


# ======================
# 主程序入口
# ======================
if __name__ == '__main__':
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop_recognition)
    root.mainloop()