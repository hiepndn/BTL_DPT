import streamlit as st
import os
import shutil

# Import các hàm xử lý
from utils import read_wav, analyze_emotion_advanced
from media_utils import convert_to_wav

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
    .stMetric { background-color: #0e1117; border: 1px solid #303030; padding: 10px; border-radius: 5px; }
    div[data-testid="stMetricValue"] { font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎧 BTL Đa Phương Tiện - Nhận diện Cảm xúc")
st.caption("Hỗ trợ: WAV, MP3, MP4, M4A. Hệ thống sử dụng Pattern Matching đa tầng.")
st.markdown("---")

# ==============================
# UPLOAD FILE
# ==============================
uploaded_file = st.file_uploader(
    "📂 Chọn file âm thanh/video",
    type=["wav", "mp3", "mp4", "m4a"]
)

if uploaded_file:
    file_name = uploaded_file.name
    ext = os.path.splitext(file_name)[1].lower()

    # 1. Lưu file tạm
    temp_input_path = f"temp_input{ext}"
    with open(temp_input_path, "wb") as f:
        f.write(uploaded_file.read())

    # 2. Xử lý chuyển đổi sang WAV
    wav_path = "temp_final.wav"
    
    with st.spinner("🔄 Đang chuẩn hóa định dạng âm thanh..."):
        if ext == ".wav":
            shutil.copy(temp_input_path, wav_path)
        else:
            converted_file = convert_to_wav(temp_input_path, wav_path)
            if converted_file is None:
                st.error("❌ Lỗi: Không thể chuyển đổi file này.")
                st.stop()
    
    # Xóa file gốc cho nhẹ
    if os.path.exists(temp_input_path):
        os.remove(temp_input_path)

    # 3. Đọc để vẽ biểu đồ (Chỉ dùng để vẽ, không dùng để phân tích nữa)
    samples, sr = read_wav(wav_path)

    if samples is None:
        st.error("❌ Lỗi đọc tín hiệu (File hỏng hoặc sai định dạng PCM).")
        st.stop()

    st.success(f"✅ Đã tải: {file_name}")

    # 4. Vẽ biểu đồ sóng
    st.subheader("📊 Biểu đồ Sóng âm")
    # Downsample để vẽ cho nhanh (lấy 1 mẫu mỗi 500 mẫu)
    step = max(1, len(samples) // 1000) 
    st.line_chart(samples[::step], use_container_width=True)

    st.markdown("---")

    # ==============================
    # 5. PHÂN TÍCH CẢM XÚC
    # ==============================
    if st.button("🔍 PHÂN TÍCH CẢM XÚC (DSP)", type="primary"):
        
        with st.spinner("Đang tính toán RMS, Pitch, TEO và so khớp mẫu..."):
            # --- SỬA Ở ĐÂY: TRUYỀN ĐƯỜNG DẪN FILE THAY VÌ SAMPLES ---
            emotion, stats = analyze_emotion_advanced(wav_path)

        st.subheader("🎯 Kết quả Nhận diện")

        # Xử lý hiển thị
        if "Silence" in emotion or "Error" in emotion:
            st.warning(f"⚠️ {emotion}")
        else:
            # Map màu sắc (Cập nhật theo tên tiếng Việt trong utils.py)
            color_map = {
                "ANG (Giận dữ)": ("#FF4B4B", "😡"),
                "ANG (Giận dữ tột độ)": ("#D50000", "🤬"), # Đỏ đậm
                "ANG (Giận dữ kìm nén)": ("#B71C1C", "😤"),
                
                "HAP (Hạnh phúc)": ("#FFC107", "😂"),
                "HAP (Cực kỳ vui sướng)": ("#FFD600", "🤣"),
                "HAP (Vui nhẹ)": ("#FFECB3", "😊"),

                "SAD (Buồn bã)": ("#2196F3", "😢"),
                "SAD (Đau khổ)": ("#0D47A1", "😭"),
                "SAD (Rất buồn)": ("#1565C0", "💧"),
                "SAD (Buồn)": ("#64B5F6", "☹️"),

                "FEA (Sợ hãi)": ("#9C27B0", "😱"),
                "FEA (Sợ hãi tột độ)": ("#4A148C", "💀"),
                "FEA (Lo âu nhẹ)": ("#E1BEE7", "😨"),

                "DIS (Ghê tởm)": ("#795548", "🤢"),
                "DIS (Ghê tởm cực độ)": ("#3E2723", "🤮"),
                "DIS (Ghê tởm nhẹ)": ("#D7CCC8", "😖"),

                "NEU (Bình thường)": ("#4CAF50", "😐")
            }
            
            # Lấy màu và icon, mặc định là màu đen nếu không tìm thấy
            color, icon = color_map.get(emotion, ("#607D8B", "🤔"))

            st.markdown(
                f"""
                <div style="background-color: {color}; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
                    <h1 style="color: white; margin: 0; text-shadow: 2px 2px 4px #000000;">{icon} {emotion}</h1>
                </div>
                """, 
                unsafe_allow_html=True
            )

            # Hiển thị thông số chi tiết
            st.markdown("### 📈 Chi tiết Đặc trưng Âm thanh")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Năng lượng (RMS)", int(stats.get("RMS", 0)))
            c2.metric("Cao độ (Pitch Hz)", int(stats.get("Pitch", 0)))
            c3.metric("Stress (TEO)", int(stats.get("TEO", 0)))

            c4, c5, c6 = st.columns(3)
            c4.metric("Biến thiên (Var)", int(stats.get("Var", 0)))
            c5.metric("Jitter (%)", f"{stats.get('Jitter', 0):.2f}")
            c6.metric("Shimmer (%)", f"{stats.get('Shimmer', 0):.2f}")

            # Thêm debug nhỏ ở dưới để thầy cô thấy mình có tính toán thật
            with st.expander("Xem dữ liệu thô (JSON)"):
                st.json(stats)

    # Không xóa file wav vội để người dùng có thể bấm phân tích lại nếu muốn
    # (Streamlit sẽ tự clean khi reload session)