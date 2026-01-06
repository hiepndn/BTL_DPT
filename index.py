import streamlit as st
import os
import shutil

# Import các hàm xử lý
from utils import read_wav, analyze_emotion_advanced
from media_utils import convert_to_wav  # <--- IMPORT MỚI TỪ FILE VỪA TẠO

# ==============================
# CẤU HÌNH TRANG
# ==============================
st.set_page_config(
    page_title="DSP Emotion Recognition",
    page_icon="🎧",
    layout="centered"
)

# CSS làm đẹp
st.markdown("""
    <style>
    .stMetric { background-color: #000000; padding: 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎧 BTL Đa Phương Tiện - Nhận diện Cảm xúc")
st.caption("Hỗ trợ: WAV, MP3, MP4, M4A (Tự động chuyển đổi)")
st.markdown("---")

# ==============================
# UPLOAD FILE
# ==============================
uploaded_file = st.file_uploader(
    "📂 Chọn file âm thanh/video",
    type=["wav", "mp3", "mp4", "m4a"] # <--- ĐÃ MỞ RỘNG ĐỊNH DẠNG
)

if uploaded_file:
    file_name = uploaded_file.name
    ext = os.path.splitext(file_name)[1].lower()

    # 1. Lưu file gốc tạm thời xuống ổ đĩa
    # (MoviePy cần đường dẫn file thực tế chứ không đọc được từ RAM)
    temp_input_path = f"temp_input{ext}"
    with open(temp_input_path, "wb") as f:
        f.write(uploaded_file.read())

    # 2. Xử lý chuyển đổi sang WAV
    wav_path = "temp_final.wav" # File kết quả cuối cùng để phân tích
    
    with st.spinner("🔄 Đang xử lý định dạng file..."):
        if ext == ".wav":
            # Nếu là wav thì copy sang tên chuẩn
            shutil.copy(temp_input_path, wav_path)
        else:
            # Nếu là mp3/mp4... thì gọi hàm convert
            converted_file = convert_to_wav(temp_input_path, wav_path)
            if converted_file is None:
                st.error("❌ Lỗi: Không thể chuyển đổi file này.")
                st.stop()
    
    # Xóa file gốc ban đầu cho nhẹ máy (chỉ giữ file wav đã convert)
    if os.path.exists(temp_input_path):
        os.remove(temp_input_path)

    # ==============================
    # 3. ĐỌC FILE WAV ĐÃ CHUẨN HÓA
    # ==============================
    samples, sr = read_wav(wav_path)

    if samples is None:
        st.error("❌ Lỗi đọc tín hiệu (File hỏng hoặc sai định dạng PCM).")
        st.stop()

    st.success(f"✅ Đã tải: {file_name} -> Đã convert sang WAV ({sr}Hz)")

    # 4. Vẽ biểu đồ sóng
    st.subheader("📊 Biểu đồ Sóng âm")
    step = max(1, len(samples) // 2000) 
    st.line_chart(samples[::step], use_container_width=True)

    st.markdown("---")

    # ==============================
    # 5. PHÂN TÍCH CẢM XÚC
    # ==============================
    if st.button("🔍 PHÂN TÍCH CẢM XÚC (DSP)", type="primary"):
        
        with st.spinner("Đang trích xuất đặc trưng: TEO, Jitter, Shimmer..."):
            emotion, stats = analyze_emotion_advanced(samples, sr)

        st.subheader("🎯 Kết quả Nhận diện")

        if emotion == "Im lặng":
            st.warning("⚠️ File âm thanh quá nhỏ hoặc im lặng.")
        else:
            # Map màu sắc
            color_map = {
                "ANG (Angry)": ("#FF4B4B", "😡"),
                "HAP (Happy)": ("#FFC107", "😂"),
                "SAD (Sadness)": ("#2196F3", "😢"),
                "FEA (Fear)": ("#9C27B0", "😱"),
                "DIS (Disgust)": ("#795548", "🤢"),
                "NEU (Neutral)": ("#4CAF50", "😐")
            }
            color, icon = color_map.get(emotion, ("#000000", "🎵"))

            st.markdown(
                f"""
                <div style="background-color: {color}; padding: 20px; border-radius: 10px; text-align: center;">
                    <h1 style="color: white; margin: 0;">{icon} {emotion}</h1>
                </div>
                """, 
                unsafe_allow_html=True
            )

            # Hiển thị thông số
            st.markdown("### 📈 Chi tiết Đặc trưng Âm thanh")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Cường độ (RMS)", stats.get("RMS"))
            c2.metric("Cao độ (Pitch)", stats.get("Pitch"))
            c3.metric("Biến thiên (Var)", stats.get("Var"))

            c4, c5, c6 = st.columns(3)
            c4.metric("Jitter", stats.get("Jitter"))
            c5.metric("Shimmer", stats.get("Shimmer"))
            c6.metric("Nhiễu (ZCR)", stats.get("ZCR"))

            st.markdown("#### ⚡ Stress Level (TEO)")
            st.metric("TEO Energy", stats.get("TEO"))

            # Dọn dẹp file wav cuối cùng sau khi phân tích xong
            if os.path.exists(wav_path):
                os.remove(wav_path)