import struct
import math

def read_wav(file_path):
    """Đọc file WAV 16-bit PCM chuẩn"""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(44)
            if header[0:4] != b'RIFF' or header[8:12] != b'WAVE':
                return None, None
            
            channels = struct.unpack('<H', header[22:24])[0]
            sample_rate = struct.unpack('<I', header[24:28])[0]
            bits_per_sample = struct.unpack('<H', header[34:36])[0]
            
            if bits_per_sample != 16:
                return None, None

            data = f.read()
            count = len(data) // 2
            format_str = '<' + ('h' * count)
            samples = list(struct.unpack(format_str, data))
            
            if channels == 2:
                samples = [(samples[i] + samples[i+1]) // 2 for i in range(0, len(samples), 2)]
                
        return samples, sample_rate
    except Exception as e:
        print("Lỗi đọc file:", e)
        return None, None

def get_frames(samples, sample_rate, frame_duration=0.03):
    """Chia khung tín hiệu (mặc định 30ms)"""
    frame_len = int(sample_rate * frame_duration)
    return [samples[i:i+frame_len] for i in range(0, len(samples), frame_len) if len(samples[i:i+frame_len]) == frame_len]

def calculate_energy(frame):
    """Tính năng lượng ngắn hạn"""
    return sum(x*x for x in frame) / len(frame)

def calculate_rms(frame):
    """Tính giá trị hiệu dụng biên độ (Cường độ âm thanh thực)"""
    return math.sqrt(sum(x*x for x in frame) / len(frame))

def calculate_zcr(frame):
    """Tính tỉ lệ qua điểm 0 (Zero Crossing Rate)"""
    count = 0
    for i in range(1, len(frame)):
        if frame[i-1] * frame[i] < 0:
            count += 1
    return count / len(frame)

def get_pitch(frame, sample_rate):
    """Ước tính Pitch (F0) bằng Autocorrelation"""
    n = len(frame)
    min_lag, max_lag = int(sample_rate / 400), int(sample_rate / 50)
    best_corr, best_lag = -1, -1
    
    for lag in range(min_lag, max_lag):
        corr = sum(frame[i] * frame[i+lag] for i in range(0, n - lag, 2))
        if corr > best_corr:
            best_corr, best_lag = corr, lag
            
    return sample_rate / best_lag if best_lag > 0 and best_corr > 0 else 0

def analyze_emotion_advanced(samples, sample_rate):
    """Hàm phân tích tổng hợp 6 cảm xúc: SAD, ANG, DIS, FEA, HAP, NEU"""
    frames = get_frames(samples, sample_rate)
    energies, zcrs, pitches, rms_list = [], [], [], []
    
    for frame in frames:
        e = calculate_energy(frame)
        energies.append(e)
        rms_list.append(calculate_rms(frame))
        # Chỉ tính Pitch/ZCR cho khung có âm thanh
        if e > 800000:
            pitches.append(get_pitch(frame, sample_rate))
            zcrs.append(calculate_zcr(frame))
    
    if not energies: return "Im lặng", {}

    # Trích xuất đặc trưng trung bình
    avg_energy = sum(energies) / len(energies)
    avg_rms = sum(rms_list) / len(rms_list)
    valid_pitches = [p for p in pitches if p > 60]
    avg_pitch = sum(valid_pitches) / len(valid_pitches) if valid_pitches else 0
    pitch_var = max(valid_pitches) - min(valid_pitches) if len(valid_pitches) > 1 else 0
    avg_zcr = sum(zcrs) / len(zcrs) if zcrs else 0

    # Logic phân loại 6 cảm xúc
    result = "NEU (Neutral)"
    
    # 1. Nhóm năng lượng thấp (SAD, DIS)
    if avg_rms < 1500:
        if avg_zcr > 0.15: result = "DIS (Disgust)" # Giọng gằn, khàn
        else: result = "SAD (Sadness)" # Giọng trầm, mệt mỏi
    
    # 2. Nhóm năng lượng cao (ANG, HAP, FEA)
    elif avg_rms > 4000:
        if avg_pitch > 250:
            if pitch_var > 200: result = "HAP (Happy)" # Cao, luyến láy lớn
            else: result = "FEA (Fear)" # Cao gắt, ít biến thiên hơn
        else:
            result = "ANG (Angry)" # To, gắt, dồn dập
            
    # 3. Nhóm trung bình (NEU)
    else:
        result = "NEU (Neutral)"

    stats = {
        "Cường độ (RMS)": f"{int(avg_rms)}",
        "Cao độ (Pitch)": f"{int(avg_pitch)} Hz",
        "Biến thiên Pitch": f"{int(pitch_var)} Hz",
        "Đặc trưng ZCR": f"{avg_zcr:.3f}"
    }
    return result, stats