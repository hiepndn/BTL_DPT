import os
import csv
import glob
import time
import concurrent.futures
import utils 
from utils import (
    read_wav, get_frames, calculate_energy, calculate_rms, 
    get_pitch_details, calculate_zcr, calculate_jitter, 
    calculate_shimmer, calculate_teo
)


DATASET_PATH = "./data_tets/Crema" 
OUTPUT_FILE = "features_dataset.csv"
MAX_WORKERS = os.cpu_count() 

ENERGY_THRESHOLD = 800 

EMOTION_MAP = {
    "ANG": "ANG (Angry)", "DIS": "DIS (Disgust)", "FEA": "FEA (Fear)",
    "HAP": "HAP (Happy)", "NEU": "NEU (Neutral)", "SAD": "SAD (Sadness)"
}

def process_single_file(file_path):
    try:
        filename = os.path.basename(file_path)
        
        samples, sr = read_wav(file_path)
        if not samples: return None
        
        frames = get_frames(samples, sr)
        if not frames: return None

        rms_list = []
        pitches = []
        lags = []
        zcrs = []
        teo_list = []

        for frame in frames:
            
            e = calculate_energy(frame)
            rms = calculate_rms(frame)
            teo = calculate_teo(frame)
            
            rms_list.append(rms)
            teo_list.append(teo)
            
            if e > ENERGY_THRESHOLD:
                p, lag = get_pitch_details(frame, sr)
                if p > 50: 
                    pitches.append(p)
                    lags.append(lag)
                zcrs.append(calculate_zcr(frame))

        if not rms_list: return None

        
        avg_rms = sum(rms_list) / len(rms_list)
        avg_teo = sum(teo_list) / len(teo_list)
        
        avg_zcr = sum(zcrs) / len(zcrs) if zcrs else 0
        avg_pitch = sum(pitches) / len(pitches) if pitches else 0
        
        pitch_var = 0
        if len(pitches) > 1:
            pitch_var = max(pitches) - min(pitches)
        
        jitter = calculate_jitter(pitches if pitches else [0])
        shimmer = calculate_shimmer(rms_list)

       
        label = "UNKNOWN"
        try:
            name_clean = os.path.splitext(filename)[0] 
            parts = name_clean.split('_') 
            if len(parts) >= 3:
                emotion_code = parts[2]
                label = EMOTION_MAP.get(emotion_code, "UNKNOWN")
        except:
            label = "UNKNOWN"

       
        return [
            filename, 
            int(avg_rms), int(avg_pitch), int(pitch_var), round(avg_zcr, 4), 
            round(jitter, 2), round(shimmer, 2), int(avg_teo), 
            label
        ]
        
    except Exception as e:
        
        return None

def extract_features_turbo(folder_path, output_csv):
    
    files = glob.glob(os.path.join(folder_path, "*.wav"))
    
    if not files:
        print(f"Không tìm thấy file .wav nào trong {folder_path}")
        return

    total_files = len(files)
    print(f"🚀 Tìm thấy {total_files} file.")
    print(f"⚡ Đang trích xuất đặc trưng (Turbo Mode - {MAX_WORKERS} Cores)...")

    start_time = time.time()
    processed_count = 0

    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        writer.writerow(["Filename", "RMS", "Pitch", "Var", "ZCR", "Jitter", "Shimmer", "TEO", "Label"])
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(process_single_file, f): f for f in files}
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    writer.writerow(result)
                
                processed_count += 1
                
                if processed_count % 100 == 0:
                    percent = (processed_count / total_files) * 100
                    print(f"\r✅ Tiến độ: {processed_count}/{total_files} ({percent:.1f}%)", end="")

    total_time = time.time() - start_time
    print(f"\n\n🎉 XONG! Dữ liệu đã lưu vào {output_csv}")
    print(f"Thời gian xử lý: {int(total_time//60)} phút {int(total_time%60)} giây.")

if __name__ == "__main__":
    extract_features_turbo(DATASET_PATH, OUTPUT_FILE)