import csv
import json


INPUT_CSV = "features_dataset.csv"
OUTPUT_MODEL = "emotion_model.json"

EMOTION_DISPLAY_MAP = {
    "ANG": "ANG",
    "DIS": "DIS",
    "FEA": "FEA",
    "HAP": "HAP",
    "NEU": "NEU",
    "SAD": "SAD"
}

def calculate_average_features():
    print(f"Đang đọc dữ liệu từ {INPUT_CSV} và tạo model chi tiết...")
    
    data_storage = {}
    
    try:
        with open(INPUT_CSV, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                label_full = row['Label'] 
                filename = row['Filename'] 
                
                if label_full == "UNKNOWN": continue
                
                
                emo_code = list(EMOTION_DISPLAY_MAP.keys())
                current_code = "NEU"
                for code in emo_code:
                    if code in label_full:
                        current_code = code
                        break
                
                try:
                    parts = filename.replace(".wav", "").split('_')
                    if len(parts) >= 4:
                        intensity = parts[3] 
                    else:
                        intensity = "XX"
                except:
                    intensity = "XX"

                
                unique_key = f"{current_code}_{intensity}"
                
                if unique_key not in data_storage:
                    data_storage[unique_key] = {
                        "RMS": [], "Pitch": [], "Var": [], "ZCR": [],
                        "Jitter": [], "Shimmer": [], "TEO": []
                    }
                
                
                data_storage[unique_key]["RMS"].append(float(row['RMS']))
                data_storage[unique_key]["Pitch"].append(float(row['Pitch']))
                data_storage[unique_key]["Var"].append(float(row['Var']))
                data_storage[unique_key]["ZCR"].append(float(row['ZCR']))
                data_storage[unique_key]["Jitter"].append(float(row['Jitter']))
                data_storage[unique_key]["Shimmer"].append(float(row['Shimmer']))
                data_storage[unique_key]["TEO"].append(float(row['TEO']))

        
        final_model = {}
        
        print("\n" + "="*60)
        print(f"{'Key Model':<15} {'Count':<8} {'RMS':<8} {'Pitch':<8}")
        print("-" * 60)
        
        for key, feats in data_storage.items():
            count = len(feats["RMS"])
            if count == 0: continue
            
           
            avg_profile = {k: sum(v)/count for k, v in feats.items()}
            
            
            original_code = key.split('_')[0]
            avg_profile["DisplayLabel"] = EMOTION_DISPLAY_MAP.get(original_code, label_full)
            
            final_model[key] = avg_profile
            
            print(f"{key:<15} {count:<8} {int(avg_profile['RMS']):<8} {int(avg_profile['Pitch']):<8}")
            
        
        with open(OUTPUT_MODEL, 'w', encoding='utf-8') as f:
            json.dump(final_model, f, indent=4)
            
        print("\n" + "="*60)
        print(f"Đã lưu {len(final_model)} mẫu model vào '{OUTPUT_MODEL}'")
        print("Model đã sẵn sàng cho phương pháp Pattern Matching (So khớp mẫu).")

    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    calculate_average_features()