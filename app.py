import os
import subprocess
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class AudioConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("音频批量转换工具 - 16bit/单声道/8000Hz")
        self.root.geometry("700x700")
        
        # FFmpeg 路径配置
        # 使用当前目录下的 ffmpeg.exe
        current_dir = Path(__file__).parent
        ffmpeg_exe = current_dir / "ffmpeg.exe"
        self.ffmpeg_path = tk.StringVar(value=str(ffmpeg_exe))  # 默认使用当前目录下的ffmpeg.exe
        
        # 文件列表
        self.input_files = []
        
        # 输出目录
        self.output_dir = tk.StringVar()
        
        # 创建UI
        self.create_widgets()
        
    def create_widgets(self):
        # FFmpeg 路径设置区域
        ffmpeg_frame = tk.LabelFrame(self.root, text="FFmpeg 配置", padx=5, pady=5)
        ffmpeg_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(ffmpeg_frame, text="FFmpeg路径:").grid(row=0, column=0, sticky="w")
        tk.Entry(ffmpeg_frame, textvariable=self.ffmpeg_path, width=50).grid(row=0, column=1, padx=5)
        tk.Button(ffmpeg_frame, text="浏览", command=self.browse_ffmpeg).grid(row=0, column=2)
        
        # 输入文件区域
        input_frame = tk.LabelFrame(self.root, text="输入文件", padx=5, pady=5)
        input_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        tk.Button(input_frame, text="添加音频文件", command=self.add_files).pack(anchor="w", pady=2)
        tk.Button(input_frame, text="清空列表", command=self.clear_files).pack(anchor="w", pady=2)
        
        # 文件列表
        self.file_listbox = tk.Listbox(input_frame, selectmode=tk.EXTENDED, height=8)
        self.file_listbox.pack(fill="both", expand=True, pady=5)
        
        # 输出目录区域
        output_frame = tk.LabelFrame(self.root, text="输出目录", padx=5, pady=5)
        output_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Entry(output_frame, textvariable=self.output_dir, width=50).pack(side="left", padx=5)
        tk.Button(output_frame, text="选择目录", command=self.browse_output_dir).pack(side="left")
        
        # 转换参数显示
        param_frame = tk.LabelFrame(self.root, text="转换参数", padx=5, pady=5)
        param_frame.pack(fill="x", padx=10, pady=5)
        
        param_text = "采样率: 8000 Hz | 声道: 单声道 | 位深: 16-bit | 格式: WAV"
        tk.Label(param_frame, text=param_text, font=("Arial", 10, "bold")).pack()
        
        # 进度条
        self.progress = ttk.Progressbar(self.root, mode='determinate')
        self.progress.pack(fill="x", padx=10, pady=5)
        
        # 状态标签
        self.status_label = tk.Label(self.root, text="就绪", relief="sunken", anchor="w")
        self.status_label.pack(fill="x", padx=10, pady=5)
        
        # 转换按钮
        self.convert_btn = tk.Button(self.root, text="开始转换", command=self.start_conversion, 
                                     bg="green", fg="white", font=("Arial", 12, "bold"))
        self.convert_btn.pack(pady=10)
        
    def browse_ffmpeg(self):
        """浏览选择 ffmpeg 可执行文件"""
        filename = filedialog.askopenfilename(
            title="选择 ffmpeg 可执行文件",
            filetypes=[("FFmpeg", "ffmpeg.exe"), ("所有文件", "*.*")]
        )
        if filename:
            self.ffmpeg_path.set(filename)
            
    def add_files(self):
        """添加音频文件"""
        files = filedialog.askopenfilenames(
            title="选择音频文件",
            filetypes=[
                ("音频文件", "*.mp3 *.wav *.flac *.m4a *.aac *.ogg *.wma"),
                ("所有文件", "*.*")
            ]
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
            
    def convert_single_file(self, input_path, output_path):
        """转换单个文件"""
        try:
            # 构建 ffmpeg 命令
            cmd = [
                self.ffmpeg_path.get(),
                "-i", input_path,
                "-ar", "8000",           # 采样率 8000Hz
                "-ac", "1",              # 单声道
                "-sample_fmt", "s16",    # 16-bit PCM
                "-y",                    # 覆盖输出文件
                output_path
            ]
            
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 60秒超时
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
            subprocess.run([self.ffmpeg_path.get(), "-version"], 
                          capture_output=True, check=True)
        except:
            self.root.after(0, lambda: messagebox.showerror("错误", 
                "FFmpeg 未找到或无法运行！请检查 FFmpeg 路径。"))
            self.root.after(0, self.enable_ui)
            return
            
        # 检查输出目录
        if not self.output_dir.get():
            self.root.after(0, lambda: messagebox.showwarning("警告", "请选择输出目录！"))
            self.root.after(0, self.enable_ui)
            return
            
        # 检查输入文件
        if not self.input_files:
            self.root.after(0, lambda: messagebox.showwarning("警告", "请添加要转换的音频文件！"))
            self.root.after(0, self.enable_ui)
            return
            
        # 创建输出目录
        os.makedirs(self.output_dir.get(), exist_ok=True)
        
        # 设置进度条
        total = len(self.input_files)
        self.progress["maximum"] = total
        
        success_count = 0
        fail_count = 0
        
        for i, input_file in enumerate(self.input_files):
            # 生成输出文件名
            input_path = Path(input_file)
            output_name = f"{input_path.stem}_converted.wav"
            output_path = Path(self.output_dir.get()) / output_name
            
            # 更新状态
            self.status_label.config(text=f"正在转换: {input_path.name} ({i+1}/{total})")
            self.progress["value"] = i
            
            # 执行转换
            success, message = self.convert_single_file(input_file, str(output_path))
            
            if success:
                success_count += 1
            else:
                fail_count += 1
                print(f"转换失败: {input_path.name} - {message}")
                
        # 完成
        self.progress["value"] = total
        result_msg = f"转换完成！\n成功: {success_count} 个\n失败: {fail_count} 个"
        self.root.after(0, lambda: messagebox.showinfo("完成", result_msg))
        self.status_label.config(text=f"转换完成 - 成功: {success_count}, 失败: {fail_count}")
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