import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import threading
import os


class App:
    def __init__(self, root):
        self.root = root
        self.root.title('遥感图像语义分割系统')
        self.root.geometry('830x500')

        self.frame_login = tk.Frame(self.root)
        self.frame_main = tk.Frame(self.root)
        self.images_frame = None  # 用于展示图像的框架
        self.system_title = tk.Label(self.root, text='遥感图像语义分割系统', font=('SimHei', 42), fg='black')
        self.system_title.pack(padx=20, pady=20)
        self.create_login_widgets()

    def create_login_widgets(self):
        self.frame_login = tk.Frame(self.root, pady=20)
        self.frame_login.pack()

        tk.Label(self.frame_login, text='用户名:').grid(row=1, column=0, pady=5)
        self.username_entry = tk.Entry(self.frame_login)
        self.username_entry.grid(row=1, column=1)
        tk.Label(self.frame_login, text='密码:').grid(row=2, column=0, pady=5)
        self.password_entry = tk.Entry(self.frame_login, show='*')
        self.password_entry.grid(row=2, column=1)
        tk.Button(self.frame_login, text='登录', command=self.login).grid(row=3, column=0, columnspan=2, pady=10)

    def create_main_widgets(self):
        self.frame_main.pack(fill=tk.BOTH, expand=1)
        tk.Button(self.frame_main, text='上传图像', command=self.upload_image).pack(pady=10)

        self.status_label = tk.Label(self.frame_main, text='就绪')
        self.status_label.pack()

    def login(self):
        if self.username_entry.get() == 'admin' and self.password_entry.get() == 'admin':
            self.frame_login.pack_forget()
            self.create_main_widgets()
        else:
            messagebox.showerror('错误', '用户名或密码错误')

    def upload_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.process_image(file_path)

    def process_image(self, file_path):
        self.status_label.config(text='处理中……（图像越大耗时越久，请耐心等待）……')
        self.root.update_idletasks()

        def run_processing_commands():
            model1_path = 'models/model-m-dice.pth'
            model2_path = 'models/model-m-crosse.pth'
            output1_path = 'output/output_dice.png'
            output2_path = 'output/output_crosse.png'

            command1 = ['python', 'predict.py', '--model', model1_path, '--input', file_path, '--output', output1_path]
            command2 = ['python', 'predict.py', '--model', model2_path, '--input', file_path, '--output', output2_path]

            result1 = subprocess.run(command1, capture_output=True, text=True)
            result2 = subprocess.run(command2, capture_output=True, text=True)

            if result1.returncode == 0 and result2.returncode == 0:
                # 在主线程中更新GUI
                self.root.after(0, self.show_images, file_path, output1_path, output2_path)
                self.root.after(0, self.status_label.config, {'text': '处理完成'})
            else:
                error_message = "处理失败:"
                if result1.returncode != 0:
                    error_message += f"\n{result1.stderr}"
                if result2.returncode != 0:
                    error_message += f"\n{result2.stderr}"
                print(error_message)
                self.root.after(0, self.status_label.config, {'text': '处理失败'})

        # 创建并启动处理线程
        processing_thread = threading.Thread(target=run_processing_commands)
        processing_thread.start()

    def show_images(self, original_path, result_path1, result_path2):
        if self.images_frame:
            self.images_frame.destroy()
        self.images_frame = tk.Frame(self.frame_main)
        self.images_frame.pack(fill=tk.BOTH, expand=1)

        # 加载并准备图像
        images_paths = [original_path, result_path1, result_path2]
        images_titles = ['输入图像', '输出1：使用DICE损失', '输出2：使用交叉熵损失']
        for path, title in zip(images_paths, images_titles):
            image = Image.open(path)
            image = image.resize((250, 250), Image.Resampling.LANCZOS)
            tk_image = ImageTk.PhotoImage(image)

            # 为每张图片创建一个框架
            frame = tk.Frame(self.images_frame)
            frame.pack(side=tk.LEFT, padx=10, pady=10)

            label_image = tk.Label(frame, image=tk_image)
            label_image.image = tk_image  # 防止图像被垃圾回收
            label_image.pack(side=tk.TOP)

            label_text = tk.Label(frame, text=title)
            label_text.pack(side=tk.BOTTOM)


if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
