import struct
import math
import json
import os

# ==========================================
# PHẦN 1: DỮ LIỆU MẪU (24 LOẠI CẢM XÚC)
# ==========================================
EMOTION_PROFILES = {
    "FEA_XX": { "RMS": 772, "Pitch": 188, "Var": 324, "ZCR": 0.0812, "Jitter": 30.98, "Shimmer": 28.39, "TEO": 497768, "DisplayLabel": "FEA (Sợ hãi)" },
    "ANG_HI": { "RMS": 3844, "Pitch": 229, "Var": 331, "ZCR": 0.1182, "Jitter": 24.86, "Shimmer": 31.72, "TEO": 15102455, "DisplayLabel": "ANG (Giận dữ tột độ)" },
    "SAD_XX": { "RMS": 366, "Pitch": 171, "Var": 322, "ZCR": 0.0721, "Jitter": 35.76, "Shimmer": 24.26, "TEO": 37022, "DisplayLabel": "SAD (Buồn bã)" },
    "DIS_XX": { "RMS": 548, "Pitch": 176, "Var": 330, "ZCR": 0.0883, "Jitter": 36.27, "Shimmer": 25.98, "TEO": 188592, "DisplayLabel": "DIS (Ghê tởm)" },
    "HAP_XX": { "RMS": 938, "Pitch": 196, "Var": 329, "ZCR": 0.0864, "Jitter": 30.17, "Shimmer": 30.91, "TEO": 510464, "DisplayLabel": "HAP (Hạnh phúc)" },
    "ANG_XX": { "RMS": 1799, "Pitch": 202, "Var": 330, "ZCR": 0.1074, "Jitter": 28.04, "Shimmer": 31.88, "TEO": 2787828, "DisplayLabel": "ANG (Giận dữ)" },
    "NEU_XX": { "RMS": 487, "Pitch": 174, "Var": 324, "ZCR": 0.0775, "Jitter": 35.75, "Shimmer": 26.99, "TEO": 69044, "DisplayLabel": "NEU (Bình thường)" },
    "DIS_HI": { "RMS": 929, "Pitch": 186, "Var": 326, "ZCR": 0.0859, "Jitter": 34.04, "Shimmer": 28.07, "TEO": 1020434, "DisplayLabel": "DIS (Ghê tởm cực độ)" },
    "DIS_MD": { "RMS": 804, "Pitch": 183, "Var": 327, "ZCR": 0.0836, "Jitter": 34.03, "Shimmer": 27.61, "TEO": 707319, "DisplayLabel": "DIS (Ghê tởm)" },
    "DIS_LO": { "RMS": 347, "Pitch": 171, "Var": 323, "ZCR": 0.0700, "Jitter": 39.31, "Shimmer": 24.90, "TEO": 48156, "DisplayLabel": "DIS (Ghê tởm nhẹ)" },
    "ANG_LO": { "RMS": 976, "Pitch": 188, "Var": 321, "ZCR": 0.0841, "Jitter": 31.93, "Shimmer": 30.09, "TEO": 674549, "DisplayLabel": "ANG (Giận dữ kìm nén)" },
    "ANG_MD": { "RMS": 1581, "Pitch": 204, "Var": 327, "ZCR": 0.0918, "Jitter": 27.99, "Shimmer": 32.28, "TEO": 2209248, "DisplayLabel": "ANG (Giận dữ)" },
    "FEA_LO": { "RMS": 330, "Pitch": 169, "Var": 312, "ZCR": 0.0667, "Jitter": 36.44, "Shimmer": 25.09, "TEO": 28346, "DisplayLabel": "FEA (Lo âu nhẹ)" },
    "FEA_MD": { "RMS": 514, "Pitch": 174, "Var": 318, "ZCR": 0.0705, "Jitter": 36.47, "Shimmer": 26.59, "TEO": 233299, "DisplayLabel": "FEA (Sợ hãi)" },
    "FEA_HI": { "RMS": 1986, "Pitch": 210, "Var": 328, "ZCR": 0.0940, "Jitter": 28.52, "Shimmer": 32.26, "TEO": 4367393, "DisplayLabel": "FEA (Sợ hãi tột độ)" },
    "HAP_HI": { "RMS": 1665, "Pitch": 207, "Var": 327, "ZCR": 0.0955, "Jitter": 28.76, "Shimmer": 32.55, "TEO": 2860750, "DisplayLabel": "HAP (Cực kỳ vui sướng)" },
    "HAP_LO": { "RMS": 529, "Pitch": 179, "Var": 318, "ZCR": 0.0702, "Jitter": 35.51, "Shimmer": 29.25, "TEO": 290736, "DisplayLabel": "HAP (Vui nhẹ)" },
    "HAP_MD": { "RMS": 678, "Pitch": 180, "Var": 326, "ZCR": 0.0800, "Jitter": 34.79, "Shimmer": 28.68, "TEO": 332612, "DisplayLabel": "HAP (Hạnh phúc)" },
    "SAD_MD": { "RMS": 272, "Pitch": 165, "Var": 310, "ZCR": 0.0601, "Jitter": 39.54, "Shimmer": 23.66, "TEO": 18530, "DisplayLabel": "SAD (Buồn)" },
    "SAD_HI": { "RMS": 317, "Pitch": 170, "Var": 320, "ZCR": 0.0620, "Jitter": 39.43, "Shimmer": 24.55, "TEO": 90604, "DisplayLabel": "SAD (Đau khổ)" },
    "SAD_LO": { "RMS": 255, "Pitch": 163, "Var": 314, "ZCR": 0.0595, "Jitter": 40.87, "Shimmer": 23.00, "TEO": 8822, "DisplayLabel": "SAD (Rất buồn)" },
    "SAD_X":  { "RMS": 241, "Pitch": 166, "Var": 340, "ZCR": 0.0530, "Jitter": 46.92, "Shimmer": 27.47, "TEO": 4858, "DisplayLabel": "SAD (Buồn)" }
}

# ==========================================
# PHẦN 2: CÁC HÀM XỬ LÝ TÍN HIỆU (CODE CŨ CỦA BẠN - GIỮ NGUYÊN 100%)
# ==========================================

def read_wav(file_path):
    try:
        with open(file_path, 'rb') as f:
            # 1. Kiểm tra Header cơ bản (12 byte đầu)
            header = f.read(12)
            if header[0:4] != b'RIFF' or header[8:12] != b'WAVE':
                return None, None

            # 2. Đi tìm chunk 'fmt ' để lấy sample_rate
            # và chunk 'data' để lấy âm thanh
            sample_rate = 0
            samples = []
            
            while True:
                # Đọc tên chunk (4 byte) và kích thước chunk (4 byte)
                chunk_id = f.read(4)
                if len(chunk_id) < 4: break # Hết file
                
                # struct.unpack('<I', ...) để đọc số nguyên 4 byte (Little Endian)
                chunk_size = struct.unpack('<I', f.read(4))[0]
                
                if chunk_id == b'fmt ':
                    # Đọc thông tin format
                    fmt_data = f.read(chunk_size)
                    sample_rate = struct.unpack('<I', fmt_data[4:8])[0]
                    # Nếu file không phải PCM (mã 1) thì code này chưa xử lý được, nhưng bài tập chắc chỉ dùng PCM thôi
                    
                elif chunk_id == b'data':
                    # ĐÂY RỒI! Dữ liệu âm thanh nằm ở đây
                    raw_data = f.read(chunk_size) # Chỉ đọc đúng chunk_size byte
                    count = len(raw_data) // 2
                    format_str = '<' + ('h' * count)
                    samples = list(struct.unpack(format_str, raw_data))
                    
                    # Đọc xong data là đủ, thoát luôn, không đọc phần rác phía sau nữa
                    break 
                else:
                    # Nếu gặp chunk lạ (Metadata, LIST, INFO...), bỏ qua nó
                    f.seek(chunk_size, 1) # Nhảy qua chunk_size byte
                    
            return samples, sample_rate
    except Exception as e:
        print("Lỗi đọc file:", e)
        return None, None

def get_frames(samples, sample_rate, frame_duration=0.02):
    frame_size = int(sample_rate * frame_duration)
    return [samples[i:i+frame_size] for i in range(0, len(samples), frame_size)]

def calculate_energy(frame):
    # Trả về 1 số float (năng lượng của frame đó)
    return sum(s*s for s in frame) / len(frame)

def calculate_rms(frame):
    if not frame: return 0
    sum_sq = sum(s**2 for s in frame)
    return math.sqrt(sum_sq / len(frame))

def calculate_zcr(frame):
    zcr = 0
    for i in range(1, len(frame)):
        if (frame[i] >= 0 and frame[i-1] < 0) or (frame[i] < 0 and frame[i-1] >= 0):
            zcr += 1
    return zcr / len(frame)

def calculate_teo(frame):
    total_teo = 0
    count = 0
    for i in range(1, len(frame)-1):
        val = frame[i]**2 - frame[i-1]*frame[i+1]
        total_teo += val
        count += 1
    return total_teo / count if count > 0 else 0

def get_pitch_details(frame, sample_rate):
    n = len(frame)
    if n == 0: return 0, 0
    
    min_lag = int(sample_rate / 400)
    max_lag = int(sample_rate / 50)
    
    best_corr = -1
    best_lag = -1
    
    for lag in range(min_lag, min(max_lag, n)):
        corr = 0
        for i in range(n - lag):
            corr += frame[i] * frame[i+lag]
        if corr > best_corr:
            best_corr = corr
            best_lag = lag
            
    if best_lag > 0:
        return sample_rate / best_lag, best_lag
    return 0, 0

def calculate_jitter(pitches):
    if len(pitches) < 2: return 0
    diffs = [abs(pitches[i] - pitches[i-1]) for i in range(1, len(pitches))]
    avg_pitch = sum(pitches) / len(pitches)
    if avg_pitch == 0: return 0
    return (sum(diffs) / len(diffs)) / avg_pitch * 100

def calculate_shimmer(rms_list):
    if len(rms_list) < 2: return 0
    diffs = [abs(rms_list[i] - rms_list[i-1]) for i in range(1, len(rms_list))]
    avg_rms = sum(rms_list) / len(rms_list)
    if avg_rms == 0: return 0
    return (sum(diffs) / len(diffs)) / avg_rms * 100

# ==========================================
# PHẦN 3: THUẬT TOÁN NHẬN DIỆN MỚI (PHẦN NÀY LÀ MỚI)
# ==========================================

def calculate_weighted_distance(input_feats, profile_feats):
    score = 0
    
    # Cập nhật trọng số dựa trên dữ liệu mới:
    # - RMS và TEO vẫn là quan trọng nhất.
    # - Pitch và Jitter giờ đây phân loại tốt hơn (SAD Jitter cao, ANG Jitter thấp).
    # - Var (Biến thiên) gần như giống nhau ở mọi cảm xúc (toàn 310-330), nên giảm trọng số cực thấp.
    weights = {
        "RMS": 3.0,     # Quan trọng nhất
        "TEO": 2.5,     # Quan trọng nhì
        "Pitch": 1.5,   
        "Jitter": 1.0,  # Dữ liệu mới cho thấy Jitter phân loại khá tốt
        "ZCR": 1.0,
        "Shimmer": 0.5,
        "Var": 0.1      # Var bị nhiễu, không phân biệt được nhiều -> Giảm trọng số
    }
    
    for key, weight in weights.items():
        val_input = input_feats.get(key, 0)
        val_profile = profile_feats.get(key, 0)
        
        if val_profile == 0: continue
        
        # % Sai lệch: |Input - Mẫu| / Mẫu
        diff_percent = abs(val_input - val_profile) / val_profile
        score += diff_percent * weight
        
    return score

def analyze_emotion_advanced(file_path):
    # 1. Đọc file
    samples, sr = read_wav(file_path)
    if not samples: return "Error", {}
    
    frames = get_frames(samples, sr)
    rms_list = []
    pitches = []
    zcrs = []
    teo_list = []
    
    # Vòng lặp tính toán (đã fix lỗi gọi hàm)
    for frame in frames:
        e = calculate_energy(frame) # Hàm nhận 1 frame -> Trả về float -> OK
        rms = calculate_rms(frame)
        teo = calculate_teo(frame)
        
        rms_list.append(rms)
        teo_list.append(teo)
        
        # Ngưỡng năng lượng 800
        if e > 800: 
            p, _ = get_pitch_details(frame, sr)
            if p > 50: pitches.append(p)
            zcrs.append(calculate_zcr(frame))

    if not rms_list: return "Silence", {}

    # Tổng hợp Input
    avg_rms = sum(rms_list) / len(rms_list)
    avg_teo = sum(teo_list) / len(teo_list)
    avg_pitch = sum(pitches) / len(pitches) if pitches else 0
    avg_zcr = sum(zcrs) / len(zcrs) if zcrs else 0
    
    pitch_var = (max(pitches) - min(pitches)) if len(pitches) > 1 else 0
    jitter = calculate_jitter(pitches if pitches else [0])
    shimmer = calculate_shimmer(rms_list)

    input_feats = {
        "RMS": avg_rms, "Pitch": avg_pitch, "Var": pitch_var,
        "ZCR": avg_zcr, "Jitter": jitter, "Shimmer": shimmer, "TEO": avg_teo
    }

    print(f"File: {os.path.basename(file_path)}")
    print(f" -> Input: RMS={int(avg_rms)}, Pitch={int(avg_pitch)}, Jitter={jitter:.2f}")

    # 2. So khớp mẫu
    best_label = "UNKNOWN"
    min_score = float('inf')
    best_profile_key = ""

    if avg_rms < 50: 
        return "Silence/Noise", input_feats

    for key, profile in EMOTION_PROFILES.items():
        score = calculate_weighted_distance(input_feats, profile)
        if score < min_score:
            min_score = score
            best_label = profile["DisplayLabel"]
            best_profile_key = key
            
    print(f" -> Khớp nhất: {best_profile_key} (Score: {min_score:.2f})")
    
    return best_label, input_feats