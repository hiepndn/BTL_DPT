# import struct
# import math

# def read_wav(file_path):
#     """Đọc file WAV 16-bit PCM chuẩn"""
#     try:
#         with open(file_path, 'rb') as f:
#             header = f.read(44)
#             if header[0:4] != b'RIFF' or header[8:12] != b'WAVE':
#                 return None, None
            
#             channels = struct.unpack('<H', header[22:24])[0]
#             sample_rate = struct.unpack('<I', header[24:28])[0]
#             bits_per_sample = struct.unpack('<H', header[34:36])[0]
            
#             if bits_per_sample != 16:
#                 return None, None

#             data = f.read()
#             count = len(data) // 2
#             format_str = '<' + ('h' * count)
#             samples = list(struct.unpack(format_str, data))
            
#             if channels == 2:
#                 samples = [(samples[i] + samples[i+1]) // 2 for i in range(0, len(samples), 2)]
                
#         return samples, sample_rate
#     except Exception as e:
#         print("Lỗi đọc file:", e)
#         return None, None

# def get_frames(samples, sample_rate, frame_duration=0.03):
#     """Chia khung tín hiệu (mặc định 30ms)"""
#     frame_len = int(sample_rate * frame_duration)
#     return [samples[i:i+frame_len] for i in range(0, len(samples), frame_len) if len(samples[i:i+frame_len]) == frame_len]

# def calculate_energy(frame):
#     """Tính năng lượng ngắn hạn"""
#     return sum(x*x for x in frame) / len(frame)

# def calculate_rms(frame):
#     """Tính giá trị hiệu dụng biên độ (Cường độ âm thanh thực)"""
#     return math.sqrt(sum(x*x for x in frame) / len(frame))

# def calculate_zcr(frame):
#     """Tính tỉ lệ qua điểm 0 (Zero Crossing Rate)"""
#     count = 0
#     for i in range(1, len(frame)):
#         if frame[i-1] * frame[i] < 0:
#             count += 1
#     return count / len(frame)

# def get_pitch(frame, sample_rate):
#     """Ước tính Pitch (F0) bằng Autocorrelation"""
#     n = len(frame)
#     min_lag, max_lag = int(sample_rate / 400), int(sample_rate / 50)
#     best_corr, best_lag = -1, -1
    
#     for lag in range(min_lag, max_lag):
#         corr = sum(frame[i] * frame[i+lag] for i in range(0, n - lag, 2))
#         if corr > best_corr:
#             best_corr, best_lag = corr, lag
            
#     return sample_rate / best_lag if best_lag > 0 and best_corr > 0 else 0

# def analyze_emotion_advanced(samples, sample_rate):
#     """Hàm phân tích tổng hợp 6 cảm xúc: SAD, ANG, DIS, FEA, HAP, NEU"""
#     frames = get_frames(samples, sample_rate)
#     energies, zcrs, pitches, rms_list = [], [], [], []
    
#     for frame in frames:
#         e = calculate_energy(frame)
#         energies.append(e)
#         rms_list.append(calculate_rms(frame))
#         # Chỉ tính Pitch/ZCR cho khung có âm thanh
#         if e > 800000:
#             pitches.append(get_pitch(frame, sample_rate))
#             zcrs.append(calculate_zcr(frame))
    
#     if not energies: return "Im lặng", {}

#     # Trích xuất đặc trưng trung bình
#     avg_energy = sum(energies) / len(energies)
#     avg_rms = sum(rms_list) / len(rms_list)
#     valid_pitches = [p for p in pitches if p > 60]
#     avg_pitch = sum(valid_pitches) / len(valid_pitches) if valid_pitches else 0
#     pitch_var = max(valid_pitches) - min(valid_pitches) if len(valid_pitches) > 1 else 0
#     avg_zcr = sum(zcrs) / len(zcrs) if zcrs else 0

#     # Logic phân loại 6 cảm xúc
#     result = "NEU (Neutral)"
    
#     # 1. Nhóm năng lượng thấp (SAD, DIS)
#     if avg_rms < 1500:
#         if avg_zcr > 0.15: result = "DIS (Disgust)" # Giọng gằn, khàn
#         else: result = "SAD (Sadness)" # Giọng trầm, mệt mỏi
    
#     # 2. Nhóm năng lượng cao (ANG, HAP, FEA)
#     elif avg_rms > 4000:
#         if avg_pitch > 250:
#             if pitch_var > 200: result = "HAP (Happy)" # Cao, luyến láy lớn
#             else: result = "FEA (Fear)" # Cao gắt, ít biến thiên hơn
#         else:
#             result = "ANG (Angry)" # To, gắt, dồn dập
            
#     # 3. Nhóm trung bình (NEU)
#     else:
#         result = "NEU (Neutral)"

#     stats = {
#         "Cường độ (RMS)": f"{int(avg_rms)}",
#         "Cao độ (Pitch)": f"{int(avg_pitch)} Hz",
#         "Biến thiên Pitch": f"{int(pitch_var)} Hz",
#         "Đặc trưng ZCR": f"{avg_zcr:.3f}"
#     }
#     return result, stats

import struct
import math
import os

# --- 1. CÁC HÀM CƠ BẢN (Giữ nguyên) ---
def read_wav(file_path):
    try:
        with open(file_path, 'rb') as f:
            header = f.read(44)
            if header[0:4] != b'RIFF' or header[8:12] != b'WAVE': return None, None
            channels = struct.unpack('<H', header[22:24])[0]
            sample_rate = struct.unpack('<I', header[24:28])[0]
            bits_per_sample = struct.unpack('<H', header[34:36])[0]
            if bits_per_sample != 16: return None, None
            data = f.read()
            count = len(data) // 2
            format_str = '<' + ('h' * count)
            samples = list(struct.unpack(format_str, data))
            if channels == 2:
                samples = [(samples[i] + samples[i+1]) // 2 for i in range(0, len(samples), 2)]
        return samples, sample_rate
    except Exception as e:
        print("Lỗi:", e); return None, None

def get_frames(samples, sample_rate, frame_duration=0.03):
    frame_len = int(sample_rate * frame_duration)
    return [samples[i:i+frame_len] for i in range(0, len(samples), frame_len) if len(samples[i:i+frame_len]) == frame_len]

def calculate_energy(frame):
    return sum(x*x for x in frame) / len(frame)

def calculate_rms(frame):
    return math.sqrt(sum(x*x for x in frame) / len(frame))

def calculate_zcr(frame):
    count = 0
    for i in range(1, len(frame)):
        if frame[i-1] * frame[i] < 0: count += 1
    return count / len(frame)

def calculate_teo(frame):
    """
    Tính Teager Energy Operator (TEO) trung bình của khung.
    Công thức: TEO[n] = x[n]^2 - x[n-1] * x[n+1]
    Đo độ 'căng' của giọng nói (Stress).
    """
    if len(frame) < 3: return 0
    
    teo_sum = 0
    # Chạy từ mẫu thứ 1 đến áp chót
    for i in range(1, len(frame) - 1):
        val = (frame[i] * frame[i]) - (frame[i-1] * frame[i+1])
        teo_sum += abs(val) # Lấy trị tuyệt đối
        
    return teo_sum / (len(frame) - 2)

# --- 2. HÀM TÍNH PITCH & JITTER ---
def get_pitch_details(frame, sample_rate):
    """Trả về Pitch (Hz) và độ trễ (Lag) để tính Jitter"""
    n = len(frame)
    min_lag = int(sample_rate / 400)
    max_lag = int(sample_rate / 50)
    best_corr = -1
    best_lag = -1
    
    # Bước nhảy 2 để tăng tốc độ
    for lag in range(min_lag, max_lag, 2):
        corr = sum(frame[i] * frame[i+lag] for i in range(0, n - lag, 2))
        if corr > best_corr:
            best_corr = corr
            best_lag = lag
            
    if best_lag > 0 and best_corr > 0:
        return sample_rate / best_lag, best_lag
    return 0, 0

def get_pitch(frame, sample_rate):
    p, _ = get_pitch_details(frame, sample_rate)
    return p

# --- 3. CÁC HÀM NÂNG CAO: JITTER & SHIMMER ---
def calculate_jitter(lags):
    """Jitter: Độ biến động tần số (Quan trọng để phân biệt giọng gằn/rung)"""
    if len(lags) < 2: return 0
    diffs = [abs(lags[i] - lags[i-1]) for i in range(1, len(lags))]
    avg_diff = sum(diffs) / len(diffs)
    avg_lag = sum(lags) / len(lags)
    # Nhân 100 để ra đơn vị % cho dễ đọc
    return (avg_diff / avg_lag) * 100 if avg_lag > 0 else 0

def calculate_shimmer(rmss):
    """Shimmer: Độ biến động biên độ (Quan trọng để phân biệt giọng hơi)"""
    if len(rmss) < 2: return 0
    diffs = [abs(rmss[i] - rmss[i-1]) for i in range(1, len(rmss))]
    avg_diff = sum(diffs) / len(diffs)
    avg_rms = sum(rmss) / len(rmss)
    # Nhân 100 để ra đơn vị %
    return (avg_diff / avg_rms) * 100 if avg_rms > 0 else 0

# --- 4. HÀM PHÂN TÍCH VỚI NGƯỠNG CHUẨN (DỰA TRÊN DATA CỦA BẠN) ---
def analyze_emotion_advanced(samples, sample_rate):
    # --- 1. TRÍCH XUẤT (Extraction Loop) ---
    frames = get_frames(samples, sample_rate)
    energies, rms_list, pitches, lags, zcrs, teo_list = [], [], [], [], [], []
    
    for frame in frames:
        e = calculate_energy(frame)
        rms = calculate_rms(frame)
        energies.append(e)
        rms_list.append(rms)
        teo_list.append(calculate_teo(frame)) # Tính TEO
        
        if e > 800000:
            p, lag = get_pitch_details(frame, sample_rate)
            if p > 0:
                pitches.append(p)
                lags.append(lag)
            zcrs.append(calculate_zcr(frame))
            
    if not energies: return "Im lặng", {}

    # --- 2. TỔNG HỢP SỐ LIỆU (Aggregation) ---
    avg_rms = sum(rms_list) / len(rms_list)
    avg_zcr = sum(zcrs) / len(zcrs) if zcrs else 0
    avg_teo = sum(teo_list) / len(teo_list) # TEO trung bình
    
    valid_pitches = [p for p in pitches if p > 60]
    avg_pitch = sum(valid_pitches) / len(valid_pitches) if valid_pitches else 0
    
    pitch_var = 0
    if len(valid_pitches) > 1:
        pitch_var = max(valid_pitches) - min(valid_pitches)
    
    jitter = calculate_jitter(lags)
    shimmer = calculate_shimmer(rms_list)

    # --- 3. LOGIC PHÂN LOẠI DỰA TRÊN DỮ LIỆU MỚI (CỰC CHUẨN) ---
    
    result = "NEU (Neutral)"

    # --- NHÁNH 1: SIÊU CĂNG THẲNG (ANG - Angry) ---
    # Dữ liệu: ANG TEO ~ 4.1 Triệu. Các cái khác < 900k.
    # Ngưỡng an toàn: 2 Triệu.
    if avg_teo > 2000000:
        result = "ANG (Angry)"

    # --- NHÁNH 2: NĂNG LƯỢNG THẤP (SAD - Sadness) ---
    # Dữ liệu: SAD RMS ~ 353, Pitch ~ 119.
    elif avg_rms < 420 and avg_pitch < 135:
        result = "SAD (Sadness)"

    # --- NHÁNH 3: NHÓM CAO ĐỘ (HAP vs FEA) ---
    # Dữ liệu: Pitch HAP~220, FEA~194 (Cao hơn DIS/NEU ~170)
    elif avg_pitch > 180:
        # HAP: Variance ~ 206, Jitter ~ 18.2 (Cao)
        # FEA: Variance ~ 128, Jitter ~ 11.6 (Thấp hơn)
        
        # Chiến thuật: Vui thì giọng nhảy nhót (Var cao) và rung nhiều (Jitter cao)
        if pitch_var > 165 or jitter > 15.0:
            result = "HAP (Happy)"
        else:
            # Sợ hãi: Pitch cao nhưng căng cứng, ít biến đổi
            result = "FEA (Fear)"

    # --- NHÁNH 4: NHÓM TRUNG BÌNH (DIS vs NEU) ---
    # RMS tầm 490-590. Pitch tầm 168-175. Rất khó phân biệt bằng 2 cái này.
    else:
        # Dữ liệu TEO: DIS ~ 337k, NEU ~ 93k (Gấp 3 lần!)
        # Dữ liệu Jitter: DIS ~ 16.6, NEU ~ 13.7
        
        # Nếu TEO cao bất thường (> 150k) ở mức nói chuyện thường -> Gằn giọng (DIS)
        if avg_teo > 150000 or jitter > 15.5:
            result = "DIS (Disgust)"
        else:
            result = "NEU (Neutral)"

    # Trả về kết quả
    stats = {
        "RMS": f"{int(avg_rms)}",
        "Pitch": f"{int(avg_pitch)} Hz",
        "Var": f"{int(pitch_var)} Hz",
        "Jitter": f"{jitter:.2f}%",
        "TEO": f"{int(avg_teo/1000)}k", # Hiển thị đơn vị Nghìn (k) cho gọn
        "ZCR": f"{avg_zcr:.3f}"
    }
    return result, stats