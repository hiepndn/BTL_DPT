import streamlit as st
import os
from media_utils import convert_to_wav
from utils import read_wav, analyze_emotion_advanced

# ==============================
# CẤU HÌNH TRANG
# ==============================
st.set_page_config(
    page_title="Phân tích Cảm xúc Âm thanh",
    layout="centered"
)

st.title("🎧 BTL Đa Phương Tiện - Phân tích Cảm xúc Âm thanh")
st.markdown("**Không dùng thư viện AI – Phân tích bằng Xử lý tín hiệu số (DSP)**")
st.divider()

# ==============================
# UPLOAD FILE
# ==============================
uploaded_file = st.file_uploader(
    "📂 Chọn file WAV / MP3 / MP4 / M4A",
    type=["wav", "mp3", "mp4", "m4a"]
)

if uploaded_file:
    file_name = uploaded_file.name
    ext = os.path.splitext(file_name)[1].lower()

    # Lưu file upload
    with open(file_name, "wb") as f:
        f.write(uploaded_file.read())

    st.success(f"✅ Đã tải file: {file_name}")

    # ==============================
    # CHUYỂN ĐỔI VỀ WAV
    # ==============================
    if ext == ".wav":
        wav_path = file_name
    else:
        st.info("🎧 Đang chuyển đổi về WAV chuẩn...")
        wav_path = convert_to_wav(file_name, "temp.wav")

    if wav_path is None:
        st.error("❌ Không thể xử lý file âm thanh")
        st.stop()

    # ==============================
    # ĐỌC FILE WAV
    # ==============================
    samples, sr = read_wav(wav_path)

    if samples is None:
        st.error("❌ File WAV không hợp lệ (chỉ hỗ trợ PCM 16-bit)")
        st.stop()

    st.success("✅ Âm thanh sẵn sàng để phân tích")

    # ==============================
    # VẼ SÓNG ÂM THANH
    # ==============================
    st.subheader("📊 Sóng âm thanh")

    step = max(1, len(samples) // 2000)
    waveform = samples[::step]

    st.line_chart(waveform)

    st.divider()

    # ==============================
    # PHÂN TÍCH CẢM XÚC
    # ==============================
    if st.button("🔍 Phân tích cảm xúc"):
        with st.spinner("Đang phân tích tín hiệu số (DSP)..."):
            emotion, stats = analyze_emotion_advanced(samples, sr)

        st.subheader("🎯 Kết quả")

        if emotion == "NOT_HUMAN":
            st.warning("⚠️ KHÔNG PHẢI GIỌNG NGƯỜI")
            st.write(f"**Nguyên nhân:** {stats.get('Nguyên nhân', 'Không rõ')}")

        elif emotion == "Lỗi file":
            st.error("❌ Lỗi file âm thanh")

        else:
            icon_map = {
                "ANG (Angry)": "🔴",
                "SAD (Sadness)": "🔵",
                "HAP (Happy)": "🟡",
                "FEA (Fear)": "🟣",
                "NEU (Neutral)": "🟢",
                "DIS (Disgust)": "🟤"
            }
            icon = icon_map.get(emotion, "🎵")
            st.success(f"{icon} **Cảm xúc phát hiện:** {emotion}")

        # ==============================
        # THÔNG SỐ DSP
        # ==============================
        st.subheader("📈 Thông số kỹ thuật (DSP)")
        st.json(stats)

else:
    st.info("👆 Vui lòng upload file âm thanh để bắt đầu")
