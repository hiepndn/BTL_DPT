import os
import csv
import utils  # Import file utils.py của bạn
from utils import get_frames, calculate_energy, calculate_rms, get_pitch, calculate_zcr

# Cấu hình đường dẫn
DATASET_PATH = "./data_tets/Crema"
OUTPUT_FILE = "features_dataset.csv"

# Bảng map nhãn của CREMA-D sang nhãn của bạn
EMOTION_MAP = {
    "ANG": "ANG (Angry)",
    "DIS": "DIS (Disgust)",
    "FEA": "FEA (Fear)",
    "HAP": "HAP (Happy)",
    "NEU": "NEU (Neutral)",
    "SAD": "SAD (Sadness)"
}

def extract_features_from_folder(folder_path, output_csv):
    # Tạo file CSV và viết tiêu đề cột
    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Các cột dữ liệu chúng ta muốn thu thập
        header = ["Filename", "RMS_Energy", "Avg_Pitch", "Pitch_Variance", "Avg_ZCR", "Label"]
        writer.writerow(header)
        
        print(f"Đang bắt đầu xử lý các file trong {folder_path}...")
        
        # Duyệt qua tất cả các file trong thư mục
        files = [f for f in os.listdir(folder_path) if f.endswith('.wav')]
        total_files = len(files)
        
        for i, filename in enumerate(files):
            file_path = os.path.join(folder_path, filename)
            
            # 1. Đọc file bằng hàm trong utils
            samples, sr = utils.read_wav(file_path)
            
            # Bỏ qua nếu lỗi đọc file (do khác định dạng hoặc nén)
            if samples is None:
                continue

            # 2. TRÍCH CHỌN ĐẶC TRƯNG (Gọi lại logic từ utils)
            frames = get_frames(samples, sr)
            
            energies = []
            rms_list = []
            pitches = []
            zcrs = []
            
            for frame in frames:
                e = calculate_energy(frame)
                energies.append(e)
                rms_list.append(calculate_rms(frame))
                
                # Chỉ tính Pitch/ZCR nếu khung có tiếng nói
                if e > 800000:
                    pitches.append(get_pitch(frame, sr))
                    zcrs.append(calculate_zcr(frame))
            
            # Nếu file im lặng hoàn toàn, bỏ qua
            if not energies: continue

            # 3. Tổng hợp thống kê (Feature Aggregation)
            avg_rms = sum(rms_list) / len(rms_list)
            
            valid_pitches = [p for p in pitches if p > 60] # Lọc nhiễu
            avg_pitch = sum(valid_pitches) / len(valid_pitches) if valid_pitches else 0
            
            # Tính biến thiên (Variance)
            pitch_var = 0
            if len(valid_pitches) > 1:
                pitch_var = max(valid_pitches) - min(valid_pitches)
                
            avg_zcr = sum(zcrs) / len(zcrs) if zcrs else 0

            # 4. Lấy nhãn cảm xúc từ tên file
            # Cấu trúc CREMA-D: 1001_DFA_ANG_XX.wav -> Lấy phần thứ 3 (index 2)
            try:
                parts = filename.split('_')
                emotion_code = parts[2] # Ví dụ: ANG
                label = EMOTION_MAP.get(emotion_code, "UNKNOWN")
            except:
                label = "UNKNOWN"

            # 5. Ghi vào CSV
            writer.writerow([filename, int(avg_rms), int(avg_pitch), int(pitch_var), round(avg_zcr, 4), label])
            
            # In tiến độ
            if i % 100 == 0:
                print(f"Đã xử lý {i}/{total_files} file...")

    print(f"✅ Hoàn tất! Dữ liệu đã lưu tại: {output_csv}")

if __name__ == "__main__":
    extract_features_from_folder(DATASET_PATH, OUTPUT_FILE)