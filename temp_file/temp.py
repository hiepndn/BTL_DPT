def calculate_energy(frames):
    return [sum(abs(s) for s in frame) for frame in frames]

def calculate_rms(frames):
    rms_list = []
    for frame in frames:
        if not frame: continue
        sum_sq = sum(s**2 for s in frame)
        rms = math.sqrt(sum_sq / len(frame))
        rms_list.append(rms)
    return rms_list

def calculate_zcr(frames):
    total_zcr = 0
    for frame in frames:
        zcr = 0
        for i in range(1, len(frame)):
            if (frame[i] >= 0 and frame[i-1] < 0) or (frame[i] < 0 and frame[i-1] >= 0):
                zcr += 1
        total_zcr += zcr / len(frame)
    return total_zcr / len(frames) if frames else 0

def get_pitch_details(frames, sample_rate):
    pitches = []
    for frame in frames:
        # Autocorrelation đơn giản để tìm Pitch
        n = len(frame)
        corr = [sum(frame[i] * frame[i+lag] for i in range(n-lag)) for lag in range(n)]
        
        # Tìm đỉnh đầu tiên sau 0
        peak_idx = -1
        for i in range(1, len(corr)-1):
            if corr[i] > corr[i-1] and corr[i] > corr[i+1]:
                if i > sample_rate / 400: # Lọc tần số quá cao (>400Hz)
                    peak_idx = i
                    break
        
        if peak_idx != -1:
            pitch = sample_rate / peak_idx
            pitches.append(pitch)
    return pitches

def calculate_jitter(pitches):
    if len(pitches) < 2: return 0
    diffs = [abs(pitches[i] - pitches[i-1]) for i in range(1, len(pitches))]
    return (sum(diffs) / len(diffs)) / (sum(pitches) / len(pitches)) * 100

def calculate_shimmer(rms_list):
    if len(rms_list) < 2: return 0
    diffs = [abs(rms_list[i] - rms_list[i-1]) for i in range(1, len(rms_list))]
    avg_amp = sum(rms_list) / len(rms_list)
    if avg_amp == 0: return 0
    return (sum(diffs) / len(diffs)) / avg_amp * 100

def calculate_teo(frames):
    # Teager Energy Operator
    total_teo = 0
    count = 0
    for frame in frames:
        for i in range(1, len(frame)-1):
            val = frame[i]**2 - frame[i-1]*frame[i+1]
            total_teo += val
            count += 1
    return total_teo / count if count > 0 else 0