import os
import subprocess
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class AudioConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("音频批量转换工具")
        self.root.geometry("850x850")

        # FFmpeg 路径配置
        current_dir = Path(__file__).parent
        ffmpeg_exe = current_dir / "ffmpeg.exe"
        self.ffmpeg_path = tk.StringVar(
            value=str(ffmpeg_exe) if ffmpeg_exe.exists() else "ffmpeg"
        )

        # 文件列表
        self.input_files = []

        # 输出目录
        self.output_dir = tk.StringVar()

        # 转换参数
        self.sample_rate = tk.StringVar(value="8000")
        self.channels = tk.StringVar(value="1")
        self.bit_depth = tk.StringVar(value="s16")
        self.output_format = tk.StringVar(value="wav")

        # 文件名选项
        self.keep_original_name = tk.BooleanVar(
            value=False
        )  # False=添加后缀，True=保持原名称
        self.overwrite = tk.BooleanVar(value=False)  # 是否覆盖已存在的文件

        # 声道处理模式
        self.channel_mode = tk.StringVar(value="mix")  # mix, left, right

        # 创建UI（带滚动条）
        self.create_scrollable_ui()

    def create_scrollable_ui(self):
        """创建带滚动条的UI"""
        # 创建主画布和滚动条
        self.canvas = tk.Canvas(self.root, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(
            self.root, orient="vertical", command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # 创建内部框架（所有内容都放在这个框架中）
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        # 将框架放入画布
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw",
            width=self.canvas.winfo_reqwidth(),
        )

        # 布局画布和滚动条
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 绑定画布大小变化
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # 绑定鼠标滚轮事件
        self.bind_mousewheel()

        # 在滚动框架中创建所有控件
        self.create_widgets_in_scrollable_frame()

    def on_canvas_configure(self, event):
        """当画布大小改变时，调整内部框架宽度"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def bind_mousewheel(self):
        """绑定鼠标滚轮事件"""

        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def bind_wheel_recursive(widget):
            """递归绑定所有子控件的滚轮事件"""
            widget.bind_all("<MouseWheel>", on_mousewheel)
            for child in widget.winfo_children():
                bind_wheel_recursive(child)

        bind_wheel_recursive(self.scrollable_frame)

    def create_widgets_in_scrollable_frame(self):
        """在可滚动框架中创建所有控件"""
        # 主框架
        main_frame = self.scrollable_frame

        # FFmpeg 路径设置区域
        ffmpeg_frame = tk.LabelFrame(main_frame, text="FFmpeg 配置", padx=5, pady=5)
        ffmpeg_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(ffmpeg_frame, text="FFmpeg路径:").grid(row=0, column=0, sticky="w")
        tk.Entry(ffmpeg_frame, textvariable=self.ffmpeg_path, width=60).grid(
            row=0, column=1, padx=5
        )
        tk.Button(ffmpeg_frame, text="浏览", command=self.browse_ffmpeg).grid(
            row=0, column=2
        )

        # 转换参数设置区域
        param_frame = tk.LabelFrame(main_frame, text="转换参数设置", padx=5, pady=5)
        param_frame.pack(fill="x", padx=10, pady=5)

        # 第一行：采样率和声道
        row1 = tk.Frame(param_frame)
        row1.pack(fill="x", pady=2)

        tk.Label(row1, text="采样率 (Hz):").pack(side="left", padx=5)
        sample_rates = ["8000", "16000", "22050", "44100", "48000"]
        self.sample_rate_combo = ttk.Combobox(
            row1, textvariable=self.sample_rate, values=sample_rates, width=10
        )
        self.sample_rate_combo.pack(side="left", padx=5)

        tk.Label(row1, text="声道:").pack(side="left", padx=5)
        channels = ["1", "2"]
        self.channels_combo = ttk.Combobox(
            row1, textvariable=self.channels, values=channels, width=5
        )
        self.channels_combo.pack(side="left", padx=5)
        tk.Label(row1, text="(1=单声道, 2=立体声)").pack(side="left", padx=2)

        # 第二行：位深和格式
        row2 = tk.Frame(param_frame)
        row2.pack(fill="x", pady=2)

        tk.Label(row2, text="位深:").pack(side="left", padx=5)
        bit_depths = ["s16", "s32", "u8", "flt"]
        bit_depth_names = {
            "s16": "16-bit",
            "s32": "32-bit",
            "u8": "8-bit",
            "flt": "32-bit float",
        }
        self.bit_depth_combo = ttk.Combobox(
            row2, textvariable=self.bit_depth, values=bit_depths, width=10
        )
        self.bit_depth_combo.pack(side="left", padx=5)

        tk.Label(row2, text="输出格式:").pack(side="left", padx=5)
        formats = ["wav", "mp3", "flac", "m4a"]
        self.format_combo = ttk.Combobox(
            row2, textvariable=self.output_format, values=formats, width=8
        )
        self.format_combo.pack(side="left", padx=5)

        # 第三行：声道处理模式
        row3 = tk.Frame(param_frame)
        row3.pack(fill="x", pady=2)

        tk.Label(row3, text="声道处理:").pack(side="left", padx=5)
        tk.Radiobutton(
            row3, text="混合为单声道", variable=self.channel_mode, value="mix"
        ).pack(side="left", padx=5)
        tk.Radiobutton(
            row3, text="只保留左声道", variable=self.channel_mode, value="left"
        ).pack(side="left", padx=5)
        tk.Radiobutton(
            row3, text="只保留右声道", variable=self.channel_mode, value="right"
        ).pack(side="left", padx=5)

        # 文件名选项区域
        name_frame = tk.LabelFrame(main_frame, text="文件名选项", padx=5, pady=5)
        name_frame.pack(fill="x", padx=10, pady=5)

        tk.Checkbutton(
            name_frame,
            text="保持原文件名（不添加后缀）",
            variable=self.keep_original_name,
        ).pack(anchor="w", pady=2)
        tk.Checkbutton(
            name_frame,
            text="覆盖已存在的文件（如果不勾选，自动添加序号）",
            variable=self.overwrite,
        ).pack(anchor="w", pady=2)

        # 输入文件区域
        input_frame = tk.LabelFrame(main_frame, text="输入文件", padx=5, pady=5)
        input_frame.pack(fill="both", expand=True, padx=10, pady=5)

        btn_frame = tk.Frame(input_frame)
        btn_frame.pack(fill="x", pady=2)
        tk.Button(btn_frame, text="添加音频文件", command=self.add_files).pack(
            side="left", padx=2
        )
        tk.Button(btn_frame, text="清空列表", command=self.clear_files).pack(
            side="left", padx=2
        )
        tk.Button(btn_frame, text="移除选中", command=self.remove_selected).pack(
            side="left", padx=2
        )

        # 文件列表（带滚动条）
        list_frame = tk.Frame(input_frame)
        list_frame.pack(fill="both", expand=True, pady=5)

        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, height=8)
        list_scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.file_listbox.yview
        )
        self.file_listbox.configure(yscrollcommand=list_scrollbar.set)

        self.file_listbox.pack(side="left", fill="both", expand=True)
        list_scrollbar.pack(side="right", fill="y")

        # 输出目录区域
        output_frame = tk.LabelFrame(main_frame, text="输出目录", padx=5, pady=5)
        output_frame.pack(fill="x", padx=10, pady=5)

        output_entry_frame = tk.Frame(output_frame)
        output_entry_frame.pack(fill="x")
        tk.Entry(output_entry_frame, textvariable=self.output_dir, width=70).pack(
            side="left", padx=5, fill="x", expand=True
        )
        tk.Button(
            output_entry_frame, text="选择目录", command=self.browse_output_dir
        ).pack(side="right", padx=5)

        # 当前参数显示
        param_display_frame = tk.LabelFrame(
            main_frame, text="当前转换参数", padx=5, pady=5
        )
        param_display_frame.pack(fill="x", padx=10, pady=5)

        self.param_label = tk.Label(
            param_display_frame, text="", font=("Arial", 9, "bold"), fg="blue"
        )
        self.param_label.pack(pady=5)
        self.update_param_display()

        # 绑定参数变化事件
        self.sample_rate.trace_add("write", lambda *args: self.update_param_display())
        self.channels.trace_add("write", lambda *args: self.update_param_display())
        self.bit_depth.trace_add("write", lambda *args: self.update_param_display())
        self.output_format.trace_add("write", lambda *args: self.update_param_display())

        # 进度条
        progress_frame = tk.LabelFrame(main_frame, text="转换进度", padx=5, pady=5)
        progress_frame.pack(fill="x", padx=10, pady=5)

        self.progress = ttk.Progressbar(progress_frame, mode="determinate")
        self.progress.pack(fill="x", padx=5, pady=5)

        # 状态标签
        self.status_label = tk.Label(
            progress_frame, text="就绪", relief="sunken", anchor="w"
        )
        self.status_label.pack(fill="x", padx=5, pady=5)

        # 转换按钮
        self.convert_btn = tk.Button(
            main_frame,
            text="开始转换",
            command=self.start_conversion,
            bg="green",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2,
        )
        self.convert_btn.pack(pady=10, padx=10, fill="x")

        # 添加一些底部空白
        tk.Frame(main_frame, height=20).pack()

    def remove_selected(self):
        """移除选中的文件"""
        selected = self.file_listbox.curselection()
        # 从后往前删除，避免索引变化
        for index in reversed(selected):
            del self.input_files[index]
            self.file_listbox.delete(index)

    def update_param_display(self):
        """更新参数显示"""
        bit_depth_names = {
            "s16": "16-bit",
            "s32": "32-bit",
            "u8": "8-bit",
            "flt": "32-bit float",
        }
        bit_display = bit_depth_names.get(self.bit_depth.get(), self.bit_depth.get())

        channel_text = "单声道" if self.channels.get() == "1" else "立体声"

        param_text = f"采样率: {self.sample_rate.get()} Hz | 声道: {channel_text} | 位深: {bit_display} | 格式: {self.output_format.get().upper()}"
        self.param_label.config(text=param_text)

    def browse_ffmpeg(self):
        """浏览选择 ffmpeg 可执行文件"""
        filename = filedialog.askopenfilename(
            title="选择 ffmpeg 可执行文件",
            filetypes=[("FFmpeg", "ffmpeg.exe"), ("所有文件", "*.*")],
        )
        if filename:
            self.ffmpeg_path.set(filename)

    def add_files(self):
        """添加音频文件"""
        files = filedialog.askopenfilenames(
            title="选择音频文件",
            filetypes=[
                ("音频文件", "*.mp3 *.wav *.flac *.m4a *.aac *.ogg *.wma *.m4a"),
                ("所有文件", "*.*"),
            ],
        )
        for file in files:
            if file not in self.input_files:
                self.input_files.append(file)
                self.file_listbox.insert(tk.END, Path(file).name)

    def clear_files(self):
        """清空文件列表"""
        self.input_files.clear()
        self.file_listbox.delete(0, tk.END)

    def browse_output_dir(self):
        """选择输出目录"""
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir.set(directory)

    def generate_output_path(self, input_path, output_dir):
        """生成输出文件路径，处理重名情况"""
        input_path = Path(input_path)
        output_dir = Path(output_dir)

        # 基础文件名
        if self.keep_original_name.get():
            base_name = input_path.stem
        else:
            base_name = f"{input_path.stem}_converted"

        # 输出文件扩展名
        extension = self.output_format.get().lower()
        if extension.startswith("."):
            extension = extension[1:]

        # 尝试使用原文件名
        output_path = output_dir / f"{base_name}.{extension}"

        # 如果文件已存在且不允许覆盖，添加序号
        if output_path.exists() and not self.overwrite.get():
            counter = 1
            while output_path.exists():
                output_path = output_dir / f"{base_name}_{counter}.{extension}"
                counter += 1
            self.status_label.config(
                text=f"注意: {input_path.name} 已存在，保存为 {output_path.name}"
            )

        return output_path

    def convert_single_file(self, input_path, output_path):
        """转换单个文件"""
        try:
            # 构建 ffmpeg 命令
            cmd = [self.ffmpeg_path.get(), "-i", input_path]

            # 添加声道处理参数
            if self.channel_mode.get() == "left":
                cmd.extend(["-map_channel", "0.0.0"])
            elif self.channel_mode.get() == "right":
                cmd.extend(["-map_channel", "0.0.1"])
            # "mix" 模式不需要额外参数

            # 添加音频参数
            cmd.extend(
                [
                    "-ar",
                    self.sample_rate.get(),  # 采样率
                    "-ac",
                    self.channels.get(),  # 声道数
                    "-sample_fmt",
                    self.bit_depth.get(),  # 位深
                    "-y" if self.overwrite.get() else "-n",  # 覆盖或跳过
                    output_path,
                ]
            )

            # 如果是 mp3 格式，添加额外参数
            if self.output_format.get().lower() == "mp3":
                cmd.insert(-1, "-b:a")
                cmd.insert(-1, "192k")  # MP3 码率

            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 120秒超时
                creationflags=subprocess.CREATE_NO_WINDOW,  # 隐藏窗口输出
            )

            if result.returncode != 0:
                return False, result.stderr
            return True, "转换成功"

        except subprocess.TimeoutExpired:
            return False, "转换超时"
        except Exception as e:
            return False, str(e)

    def convert_all(self):
        """批量转换主逻辑（在子线程中运行）"""
        # 检查 FFmpeg
        try:
            subprocess.run(
                [self.ffmpeg_path.get(), "-version"], capture_output=True, check=True
            )
        except:
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "错误", "FFmpeg 未找到或无法运行！请检查 FFmpeg 路径。"
                ),
            )
            self.root.after(0, self.enable_ui)
            return

        # 检查输出目录
        if not self.output_dir.get():
            self.root.after(
                0, lambda: messagebox.showwarning("警告", "请选择输出目录！")
            )
            self.root.after(0, self.enable_ui)
            return

        # 检查输入文件
        if not self.input_files:
            self.root.after(
                0, lambda: messagebox.showwarning("警告", "请添加要转换的音频文件！")
            )
            self.root.after(0, self.enable_ui)
            return

        # 创建输出目录
        os.makedirs(self.output_dir.get(), exist_ok=True)

        # 设置进度条
        total = len(self.input_files)
        self.progress["maximum"] = total

        success_count = 0
        fail_count = 0
        skip_count = 0

        for i, input_file in enumerate(self.input_files):
            # 生成输出文件路径
            output_path = self.generate_output_path(input_file, self.output_dir.get())

            # 如果输出文件已存在且不覆盖，跳过
            if output_path.exists() and not self.overwrite.get():
                skip_count += 1
                self.status_label.config(
                    text=f"跳过: {Path(input_file).name} (文件已存在)"
                )
                self.progress["value"] = i + 1
                continue

            # 更新状态
            self.status_label.config(
                text=f"正在转换: {Path(input_file).name} ({i + 1}/{total})"
            )
            self.progress["value"] = i

            # 执行转换
            success, message = self.convert_single_file(input_file, str(output_path))

            if success:
                success_count += 1
                self.status_label.config(text=f"完成: {Path(input_file).name}")
            else:
                fail_count += 1
                print(f"转换失败: {Path(input_file).name} - {message}")

            self.progress["value"] = i + 1

        # 完成
        result_msg = f"转换完成！\n成功: {success_count} 个\n跳过: {skip_count} 个\n失败: {fail_count} 个"
        self.root.after(0, lambda: messagebox.showinfo("完成", result_msg))
        self.status_label.config(
            text=f"转换完成 - 成功: {success_count}, 跳过: {skip_count}, 失败: {fail_count}"
        )
        self.root.after(0, self.enable_ui)

    def start_conversion(self):
        """启动转换（在后台线程中运行）"""
        # 禁用UI元素
        self.convert_btn.config(state="disabled", text="转换中...")
        self.status_label.config(text="正在转换，请稍候...")

        # 启动转换线程
        thread = threading.Thread(target=self.convert_all)
        thread.daemon = True
        thread.start()

    def enable_ui(self):
        """恢复UI元素"""
        self.convert_btn.config(state="normal", text="开始转换")


def main():
    root = tk.Tk()
    app = AudioConverter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
