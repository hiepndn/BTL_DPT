import struct
import math

def read_wav(file_path):
    try:
        with open(file_path, 'rb') as f:
            header = f.read(44)
            # Kiểm tra định dạng WAV
            if header[0:4] != b'RIFF' or header[8:12] != b'WAVE':
                return None, None
            
            channels = struct.unpack('<H', header[22:24])[0]
            sample_rate = struct.unpack('<I', header[24:28])[0]
            bits_per_sample = struct.unpack('<H', header[34:36])[0]
            
            # Chỉ xử lý file 16-bit để đơn giản hóa logic (phổ biến nhất)
            if bits_per_sample != 16:
                return None, None

            data = f.read()
            count = len(data) // 2
            format_str = '<' + ('h' * count)
            samples = list(struct.unpack(format_str, data))
            
            # Nếu là stereo (2 kênh), lấy trung bình cộng để thành mono
            if channels == 2:
                samples = [(samples[i] + samples[i+1]) // 2 for i in range(0, len(samples), 2)]
                
        return samples, sample_rate
    except Exception as e:
        print("Lỗi đọc file:", e)
        return None, None

def get_frames(samples, sample_rate, frame_duration=0.03):
    """Chia âm thanh thành các khung (frames), mặc định 30ms mỗi khung"""
    frame_len = int(sample_rate * frame_duration)
    frames = []
    for i in range(0, len(samples), frame_len):
        frame = samples[i:i+frame_len]
        if len(frame) == frame_len:
            frames.append(frame)
    return frames

def calculate_energy(frame):
    """Tính năng lượng ngắn hạn (Short-time Energy)"""
    return sum(x*x for x in frame) / len(frame)

def calculate_zcr(frame):
    """Tính Zero Crossing Rate"""
    count = 0
    for i in range(1, len(frame)):
        if frame[i-1] * frame[i] < 0:
            count += 1
    return count / len(frame)

def get_pitch(frame, sample_rate):
    """
    Ước tính cao độ (Pitch/F0) dùng thuật toán Autocorrelation đơn giản.
    Phạm vi tìm kiếm: 50Hz - 400Hz (giọng người).
    """
    n = len(frame)
    # Giới hạn tìm kiếm (lag) tương ứng với 50Hz - 400Hz
    min_lag = int(sample_rate / 400)
    max_lag = int(sample_rate / 50)
    
    best_corr = -1
    best_lag = -1
    
    # Tính tự tương quan
    for lag in range(min_lag, max_lag):
        corr = 0
        # Tối ưu hóa: chỉ tính toán một phần mẫu để tăng tốc độ (giảm độ phức tạp O(N^2))
        for i in range(0, n - lag, 2): 
            corr += frame[i] * frame[i+lag]
            
        if corr > best_corr:
            best_corr = corr
            best_lag = lag
            
    if best_lag > 0 and best_corr > 0: # Cần thêm ngưỡng năng lượng để tránh nhiễu
        return sample_rate / best_lag
    return 0

def analyze_emotion_advanced(samples, sample_rate):
    frames = get_frames(samples, sample_rate)
    
    energies = []
    zcrs = []
    pitches = []
    
    # Phân tích từng khung
    for frame in frames:
        e = calculate_energy(frame)
        energies.append(e)
        
        # Chỉ tính pitch cho các khung có tiếng nói
        if e > 1000000:
            pitches.append(get_pitch(frame, sample_rate))
            zcrs.append(calculate_zcr(frame))
    
    if not energies: return "Im lặng", {}

    avg_energy = sum(energies) / len(energies)
    valid_pitches = [p for p in pitches if p > 0]
    avg_pitch = sum(valid_pitches) / len(valid_pitches) if valid_pitches else 0
    pitch_variance = max(valid_pitches) - min(valid_pitches) if valid_pitches else 0
    avg_zcr = sum(zcrs) / len(zcrs) if zcrs else 0

    # --- LOGIC QUYẾT ĐỊNH CẢM XÚC ĐÃ TINH CHỈNH ---
    
    # 1. Kiểm tra bộ lọc giọng người/tiếng động lạ trước
    if avg_pitch < 60 or avg_pitch > 600 or avg_zcr > 0.4:
        return "NOT_HUMAN", {"Nguyên nhân": "Không phải giọng người hoặc quá nhiễu"}

    # 2. Phân loại chi tiết
    result = "Bình thường"
    
    # Các ngưỡng thực tế dựa trên dữ liệu bạn cung cấp
    is_very_high_pitch = avg_pitch > 280      # 335 Hz của bạn là rất cao
    is_extreme_varying = pitch_variance > 250 # 310 Hz của bạn là biến thiên cực lớn
    is_loud = avg_energy > 2000000            # Hạ ngưỡng to từ 50tr xuống 2tr để khớp file 4.3tr
    
    if avg_energy < 500000:
        result = "Buồn / Chán nản"
    
    # Ưu tiên nhận diện TIẾNG KHÓC (Pitch cực cao + Biến thiên cực lớn)
    elif is_very_high_pitch and is_extreme_varying:
        if avg_energy > 20000000: # Chỉ khi hét cực to mới là Giận dữ
            result = "Giận dữ (Angry)"
        else:
            result = "Đau khổ / Khóc (Distress)"
            
    # Nhận diện TIẾNG CƯỜI/VUI VẺ (Pitch cao nhưng biến thiên ổn định hơn tiếng khóc)
    elif is_loud and avg_pitch > 180:
        if pitch_variance > 100:
            result = "Vui vẻ / Hạnh phúc"
        else:
            result = "Bình thường (Neutral)"
    else:
        result = "Bình thường (Neutral)"

    stats = {
        "Năng lượng TB": f"{int(avg_energy):,}",
        "Cao độ TB (Pitch)": f"{int(avg_pitch)} Hz",
        "Biến thiên Pitch": f"{int(pitch_variance)} Hz",
        "Tỉ lệ qua điểm 0": f"{avg_zcr:.3f}"
    }
    return result, stats
