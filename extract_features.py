# import os
# import csv
# import utils 
# from utils import get_frames, calculate_energy, calculate_rms, get_pitch_details, calculate_zcr, calculate_jitter, calculate_shimmer

# # Cấu hình đường dẫn (Giữ nguyên như file gốc của bạn)
# DATASET_PATH = "./data_tets/Crema"
# OUTPUT_FILE = "features_dataset.csv"

# EMOTION_MAP = {
#     "ANG": "ANG (Angry)",
#     "DIS": "DIS (Disgust)",
#     "FEA": "FEA (Fear)",
#     "HAP": "HAP (Happy)",
#     "NEU": "NEU (Neutral)",
#     "SAD": "SAD (Sadness)"
# }

# def extract_features_from_folder(folder_path, output_csv):
#     with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
#         writer = csv.writer(file)
#         # Thêm cột Jitter và Shimmer vào tiêu đề
#         header = ["Filename", "RMS_Energy", "Avg_Pitch", "Pitch_Variance", "Avg_ZCR", "Jitter", "Shimmer", "Label"]
#         writer.writerow(header)
        
#         print(f"Đang bắt đầu xử lý các file trong {folder_path}...")
        
#         if not os.path.exists(folder_path):
#             print(f"Lỗi: Không tìm thấy thư mục {folder_path}")
#             return

#         files = [f for f in os.listdir(folder_path) if f.endswith('.wav')]
#         total_files = len(files)
        
#         for i, filename in enumerate(files):
#             file_path = os.path.join(folder_path, filename)
#             samples, sr = utils.read_wav(file_path)
            
#             if samples is None: continue

#             # 1. TRÍCH CHỌN
#             frames = get_frames(samples, sr)
#             energies, rms_list, pitches, lags, zcrs = [], [], [], [], []
            
#             for frame in frames:
#                 e = calculate_energy(frame)
#                 energies.append(e)
#                 rms_list.append(calculate_rms(frame))
                
#                 if e > 800000:
#                     # Dùng hàm mới get_pitch_details để lấy cả Lag
#                     p, lag = get_pitch_details(frame, sr)
#                     if p > 0:
#                         pitches.append(p)
#                         lags.append(lag)
#                     zcrs.append(calculate_zcr(frame))
            
#             if not energies: continue

#             # 2. TỔNG HỢP
#             avg_rms = sum(rms_list) / len(rms_list)
#             avg_zcr = sum(zcrs) / len(zcrs) if zcrs else 0
            
#             valid_pitches = [p for p in pitches if p > 60]
#             avg_pitch = sum(valid_pitches) / len(valid_pitches) if valid_pitches else 0
            
#             pitch_var = 0
#             if len(valid_pitches) > 1:
#                 pitch_var = max(valid_pitches) - min(valid_pitches)
                
#             # Tính Jitter và Shimmer
#             jitter = calculate_jitter(lags)
#             shimmer = calculate_shimmer(rms_list)

#             # 3. NHÃN
#             try:
#                 parts = filename.split('_')
#                 emotion_code = parts[2]
#                 label = EMOTION_MAP.get(emotion_code, "UNKNOWN")
#             except:
#                 label = "UNKNOWN"

#             # 4. GHI CSV
#             writer.writerow([
#                 filename, 
#                 int(avg_rms), 
#                 int(avg_pitch), 
#                 int(pitch_var), 
#                 round(avg_zcr, 4), 
#                 round(jitter, 2),  # Cột mới
#                 round(shimmer, 2), # Cột mới
#                 label
#             ])
            
#             if i % 100 == 0:
#                 print(f"Đã xử lý {i}/{total_files} file...")

#     print(f"✅ Hoàn tất! Dữ liệu đã lưu tại: {output_csv}")

# if __name__ == "__main__":
#     extract_features_from_folder(DATASET_PATH, OUTPUT_FILE)

import os
import csv
import utils 
# Nhớ import thêm calculate_teo
from utils import get_frames, calculate_energy, calculate_rms, get_pitch_details, calculate_zcr, calculate_jitter, calculate_shimmer, calculate_teo

# Cấu hình đường dẫn
DATASET_PATH = "./data_tets/Crema"
OUTPUT_FILE = "features_dataset.csv"

EMOTION_MAP = {
    "ANG": "ANG (Angry)", "DIS": "DIS (Disgust)", "FEA": "FEA (Fear)",
    "HAP": "HAP (Happy)", "NEU": "NEU (Neutral)", "SAD": "SAD (Sadness)"
}

def extract_features_from_folder(folder_path, output_csv):
    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # THÊM CỘT "TEO" VÀO HEADER
        header = ["Filename", "RMS", "Pitch", "Var", "ZCR", "Jitter", "Shimmer", "TEO", "Label"]
        writer.writerow(header)
        
        print(f"Đang xử lý dữ liệu tại {folder_path}...")
        files = [f for f in os.listdir(folder_path) if f.endswith('.wav')]
        
        for i, filename in enumerate(files):
            file_path = os.path.join(folder_path, filename)
            samples, sr = utils.read_wav(file_path)
            if samples is None: continue

            # 1. TRÍCH XUẤT
            frames = get_frames(samples, sr)
            energies, rms_list, pitches, lags, zcrs, teo_list = [], [], [], [], [], []
            
            for frame in frames:
                e = calculate_energy(frame)
                energies.append(e)
                rms_list.append(calculate_rms(frame))
                teo_list.append(calculate_teo(frame)) # <--- TÍNH TEO
                
                if e > 800000:
                    p, lag = get_pitch_details(frame, sr)
                    if p > 0:
                        pitches.append(p)
                        lags.append(lag)
                    zcrs.append(calculate_zcr(frame))
            
            if not energies: continue

            # 2. TỔNG HỢP
            avg_rms = sum(rms_list) / len(rms_list)
            avg_teo = sum(teo_list) / len(teo_list) # <--- TEO TRUNG BÌNH
            avg_zcr = sum(zcrs) / len(zcrs) if zcrs else 0
            
            valid_pitches = [p for p in pitches if p > 60]
            avg_pitch = sum(valid_pitches) / len(valid_pitches) if valid_pitches else 0
            
            pitch_var = 0
            if len(valid_pitches) > 1:
                pitch_var = max(valid_pitches) - min(valid_pitches)
                
            jitter = calculate_jitter(lags)
            shimmer = calculate_shimmer(rms_list)

            # 3. NHÃN
            try:
                parts = filename.split('_')
                emotion_code = parts[2]
                label = EMOTION_MAP.get(emotion_code, "UNKNOWN")
            except:
                label = "UNKNOWN"

            # 4. GHI CSV (Thêm avg_teo vào)
            writer.writerow([
                filename, 
                int(avg_rms), int(avg_pitch), int(pitch_var), round(avg_zcr, 4), 
                round(jitter, 2), round(shimmer, 2), 
                int(avg_teo), # <--- GHI TEO
                label
            ])
            
            if i % 100 == 0: print(f"Đã xong {i} file...")

    print(f"✅ Xong! File CSV mới đã có cột TEO.")

if __name__ == "__main__":
    extract_features_from_folder(DATASET_PATH, OUTPUT_FILE)