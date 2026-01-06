# import csv
# import json

# # Cấu hình
# INPUT_CSV = "features_dataset.csv"
# OUTPUT_MODEL = "emotion_model.json" # File này dùng để lưu lại các thông số chuẩn

# def calculate_average_features():
#     print(f"Đang đọc dữ liệu từ {INPUT_CSV}...")
    
#     # Từ điển lưu trữ dữ liệu
#     data_storage = {}
    
#     try:
#         with open(INPUT_CSV, mode='r', encoding='utf-8') as f:
#             reader = csv.DictReader(f)
            
#             for row in reader:
#                 label = row['Label']
#                 if label == "UNKNOWN": continue
                
#                 if label not in data_storage:
#                     data_storage[label] = {
#                         "RMS": [], "Pitch": [], "Var": [], "ZCR": [],
#                         "Jitter": [], "Shimmer": [] # Thêm 2 cột mới
#                     }
                
#                 # Gom dữ liệu (Chuyển từ string sang float)
#                 data_storage[label]["RMS"].append(float(row['RMS_Energy']))
#                 data_storage[label]["Pitch"].append(float(row['Avg_Pitch']))
#                 data_storage[label]["Var"].append(float(row['Pitch_Variance']))
#                 data_storage[label]["ZCR"].append(float(row['Avg_ZCR']))
#                 data_storage[label]["Jitter"].append(float(row['Jitter']))   # Mới
#                 data_storage[label]["Shimmer"].append(float(row['Shimmer'])) # Mới
                
#         # Tính trung bình (Centroids)
#         model = {}
        
#         # In tiêu đề bảng
#         print("\n" + "="*85)
#         print(f"{'Label':<15} {'RMS':<8} {'Pitch':<8} {'Var':<8} {'ZCR':<8} {'Jitter':<8} {'Shimmer':<8}")
#         print("-" * 85)
        
#         for label, feats in data_storage.items():
#             count = len(feats["RMS"])
#             if count == 0: continue
            
#             # Tính trung bình cộng
#             avg_vals = {k: sum(v)/count for k, v in feats.items()}
            
#             # Lưu vào model (làm tròn số cho đẹp)
#             model[label] = avg_vals
            
#             print(f"{label:<15} {int(avg_vals['RMS']):<8} {int(avg_vals['Pitch']):<8} "
#                   f"{int(avg_vals['Var']):<8} {avg_vals['ZCR']:.3f}   "
#                   f"{avg_vals['Jitter']:.2f}%    {avg_vals['Shimmer']:.2f}%")

#         print("="*85)

#         # (Tùy chọn) Lưu ra file JSON nếu sau này muốn dùng code tự động so sánh
#         with open(OUTPUT_MODEL, 'w', encoding='utf-8') as f:
#             json.dump(model, f, indent=4)
#             print(f"\n✅ Đã lưu bộ thông số chuẩn vào: {OUTPUT_MODEL}")

#     except FileNotFoundError:
#         print(f"❌ Lỗi: Không tìm thấy file {INPUT_CSV}. Hãy chạy extract_features.py trước!")
#     except KeyError as e:
#         print(f"❌ Lỗi dữ liệu: File CSV thiếu cột {e}. Hãy chạy lại extract_features.py để cập nhật cột mới.")

# if __name__ == "__main__":
#     calculate_average_features()

import csv
import json

# Cấu hình
INPUT_CSV = "features_dataset.csv"
OUTPUT_MODEL = "emotion_model.json" # File kết quả sẽ được lưu ở đây

def calculate_average_features():
    print(f"Đang phân tích dữ liệu từ {INPUT_CSV}...")
    data = {}
    
    # 1. ĐỌC DỮ LIỆU TỪ CSV
    try:
        with open(INPUT_CSV, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                lbl = row['Label']
                if lbl == "UNKNOWN": continue
                
                # Khởi tạo list nếu chưa có
                if lbl not in data: 
                    data[lbl] = {"RMS": [], "Pitch": [], "Var": [], "Jitter": [], "Shimmer": [], "TEO": []}
                
                # Gom dữ liệu vào list
                data[lbl]["RMS"].append(float(row['RMS']))
                data[lbl]["Pitch"].append(float(row['Pitch']))
                data[lbl]["Var"].append(float(row['Var']))
                data[lbl]["Jitter"].append(float(row['Jitter']))
                data[lbl]["Shimmer"].append(float(row['Shimmer']))
                data[lbl]["TEO"].append(float(row['TEO']))

        # 2. TÍNH TRUNG BÌNH & IN RA MÀN HÌNH
        final_model = {} # Biến để lưu dữ liệu xuất file
        
        print("\n" + "="*105)
        print(f"{'Label':<15} {'RMS':<8} {'Pitch':<8} {'Var':<8} {'Jitter':<8} {'Shimmer':<8} {'TEO (Triệu)':<12}")
        print("-" * 105)
        
        for lbl, feats in data.items():
            count = len(feats["RMS"])
            if count == 0: continue
            
            # Tính trung bình cộng cho từng đặc trưng
            avg = {k: sum(v)/count for k, v in feats.items()}
            
            # Lưu vào biến tổng hợp để xuất file
            final_model[lbl] = avg
            
            # In ra màn hình cho dễ nhìn (TEO chia 1 triệu)
            print(f"{lbl:<15} {int(avg['RMS']):<8} {int(avg['Pitch']):<8} {int(avg['Var']):<8} "
                  f"{avg['Jitter']:.2f}%   {avg['Shimmer']:.2f}%   {int(avg['TEO']/1000000)}M")
            
        print("="*105)

        # 3. XUẤT RA FILE JSON (QUAN TRỌNG)
        with open(OUTPUT_MODEL, 'w', encoding='utf-8') as f:
            json.dump(final_model, f, indent=4)
            
        print(f"\n✅ Đã xuất file mô hình chuẩn ra: {OUTPUT_MODEL}")
        print("Bạn hãy mở file này lên để xem chính xác con số TEO trung bình nhé!")

    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy file {INPUT_CSV}. Hãy chạy extract_features.py trước.")
    except KeyError as e:
        print(f"❌ Lỗi dữ liệu: File CSV thiếu cột {e}. Hãy chạy lại extract_features.py.")

if __name__ == "__main__":
    calculate_average_features()