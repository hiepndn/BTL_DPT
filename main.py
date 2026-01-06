import tkinter as tk
from tkinter import filedialog, messagebox
import threading # Để không bị đơ giao diện khi xử lý file nặng

from utils import read_wav, analyze_emotion_advanced

class EmotionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Phân tích Cảm xúc Âm thanh (No Libraries)")
        self.root.geometry("700x500")
        
        # Tiêu đề
        lbl_title = tk.Label(root, text="BTL Đa Phương Tiện - Nhóm XX", font=("Arial", 16, "bold"), fg="#333")
        lbl_title.pack(pady=10)

        # Canvas vẽ sóng
        self.canvas = tk.Canvas(root, width=650, height=200, bg="black")
        self.canvas.pack(pady=10)
        self.canvas.create_text(325, 100, text="Sóng âm thanh sẽ hiện ở đây", fill="gray")

        # Nút bấm
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        
        btn_load = tk.Button(btn_frame, text="1. Chọn File WAV", command=self.load_file, width=15, height=2, bg="#ddd")
        btn_load.pack(side=tk.LEFT, padx=10)
        
        self.btn_analyze = tk.Button(btn_frame, text="2. Phân tích", command=self.start_analysis, width=15, height=2, bg="#4CAF50", fg="white", state=tk.DISABLED)
        self.btn_analyze.pack(side=tk.LEFT, padx=10)

        # Khu vực hiển thị kết quả
        self.lbl_result = tk.Label(root, text="Kết quả: ---", font=("Arial", 18, "bold"), fg="blue")
        self.lbl_result.pack(pady=10)

        # Khu vực hiển thị thông số kỹ thuật (Stats)
        self.stats_text = tk.Text(root, height=5, width=60, font=("Courier", 10), bg="#f0f0f0")
        self.stats_text.pack(pady=5)
        self.stats_text.insert(tk.END, "Thông số chi tiết sẽ hiện ở đây...")
        self.stats_text.config(state=tk.DISABLED)

        self.current_samples = None
        self.current_sr = None

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if not file_path: return
        
        # Đọc file
        samples, sr = read_wav(file_path)
        if samples is None:
            messagebox.showerror("Lỗi", "Không đọc được file! Vui lòng chọn file WAV 16-bit chuẩn.")
            return

        self.current_samples = samples
        self.current_sr = sr
        
        # Vẽ sóng (Downsampling để vẽ nhanh hơn)
        self.draw_waveform(samples)
        self.btn_analyze.config(state=tk.NORMAL)
        self.lbl_result.config(text="Đã tải file. Nhấn Phân tích.")
        self.update_stats("Chờ xử lý...")

    def draw_waveform(self, samples):
        self.canvas.delete("all")
        w = 650
        h = 200
        mid = h // 2
        
        # Tối ưu: Chỉ lấy tối đa 2000 điểm để vẽ cho mượt
        step = max(1, len(samples) // w)
        points = []
        
        for i in range(w):
            idx = i * step
            if idx < len(samples):
                # Chuẩn hóa giá trị 16-bit (-32768 đến 32767) về chiều cao canvas
                val = samples[idx]
                y = mid - (val / 32768) * (mid - 10) # -10 để chừa lề
                points.append((i, y))
        
        if points:
            self.canvas.create_line(points, fill="#00ff00")

    def start_analysis(self):
        if self.current_samples is None: return

        self.lbl_result.config(text="Đang phân tích kỹ thuật số...", fg="orange")
        self.root.update()
        
        # Gọi hàm phân tích mới
        emotion, stats = analyze_emotion_advanced(self.current_samples, self.current_sr)
        
        # Xử lý kết quả trả về
        if emotion == "NOT_HUMAN":
            self.lbl_result.config(text="⚠️ KHÔNG PHẢI GIỌNG NGƯỜI", fg="red")
            messagebox.showwarning("Cảnh báo", f"Hệ thống phát hiện đây không phải giọng nói con người.\n\nLý do: {stats.get('Nguyên nhân')}")
        elif emotion == "Lỗi file":
            self.lbl_result.config(text="Lỗi File", fg="red")
        else:
            # Map màu sắc cho đẹp
            color_map = {
                "Giận dữ (Angry)": "red",
                "Buồn (Sad)": "blue",
                "Vui vẻ / Hạnh phúc": "#FFD700",
                "Sợ hãi (Fear)": "purple",
                "Bình thường (Neutral)": "green"
            }
            color = color_map.get(emotion, "black")
            self.lbl_result.config(text=f"Cảm xúc: {emotion}", fg=color)
        
        # Hiển thị bảng thông số
        stat_str = "THÔNG SỐ KỸ THUẬT (DSP):\n"
        for k, v in stats.items():
            stat_str += f"- {k}: {v}\n"
        self.update_stats(stat_str)

    def update_stats(self, text):
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, text)
        self.stats_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = EmotionApp(root)
    root.mainloop()