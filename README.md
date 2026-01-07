- run code: streamlit run index.py
- các file đang dùng:
    - giao diện: index.py
    - logic: utils.py
    - xử lý âm thanh kp wav: media_utils.py
    - trích chọn đặc trưng: extract_features.py
    - trung bình đặc trưng: avg_features.py

- hiện tại đang có 6 đặc trưng là: RMS, Pitch, Var, Jitter, Shimmer, TEO
- và 24 cảm xúc bao gồm: ANG, DIS, FEA, HAP, NEU, SAD và 4 tone XX, HI, LO, MD (6x4=24)

- file trung bình đặc trưng là file emotion_model.json dùng để làm thông số so sánh vs âm thanh truyền vào

- thiếu thư viện thì tải thêm nhé, thường thiếu 2 cái là:
    - pip install moviepy   
    - pip install streamlit

===========================================================================================================================
GEMINI giải thích
===========================================================================================================================

1. RMS (Root Mean Square) - Năng lượng/Độ to
    - Nó đo cái gì? Độ to, âm lượng trung bình của giọng nói.
    - Cơ sở vật lý: Khi bạn kích động, phổi đẩy luồng hơi ra cực mạnh làm biên độ sóng âm lớn lên.
    - Tại sao chọn? Đây là cách dễ nhất để phân biệt nhóm "Năng lượng cao" (Vui, Giận) và "Năng lượng thấp" (Buồn, Bình thường).
    - Ví dụ: Giận dữ (RMS ~1800) > Buồn (RMS ~300).

2. Pitch (F0) - Cao độ
    - Nó đo cái gì? Độ trầm hay bổng của giọng nói (Tần số rung của dây thanh quản).
    - Cơ sở vật lý: Khi căng thẳng hoặc phấn khích, cơ dây thanh quản co rút lại -> Dây thanh rung nhanh hơn -> Giọng cao hơn. Khi buồn, cơ thả lỏng -> Giọng trầm xuống.
    - Tại sao chọn? Để phân biệt Nam/Nữ và phân biệt Vui/Sợ (giọng cao) với Buồn/Bình thường (giọng trầm).
    - Ví dụ: Sợ hãi (Pitch ~260Hz) cao hơn hẳn Bình thường (Pitch ~174Hz).

3. Var (Pitch Variance) - Độ biến thiên cao độ
    - Nó đo cái gì? Giọng nói đều đều (monotone) hay lên xuống thất thường.
    - Cơ sở vật lý: Khi vui vẻ, chúng ta hay luyến láy ("Á ha!", "Thật á?"). Khi buồn hoặc chán nản, giọng cứ đều đều một tông.
    - Tại sao chọn? Để phân biệt cảm xúc "Có sắc thái" (Happy) với cảm xúc "Vô hồn" (Sad/Neutral).
    - Lưu ý: Trong dữ liệu của bạn chỉ số này hơi giống nhau, nên mình đã giảm trọng số của nó xuống.

4. ZCR (Zero Crossing Rate) - Tốc độ qua điểm 0
    - Nó đo cái gì? Độ "nhám", độ nhiễu hoặc các âm gió (xuỵt xoạt) trong giọng nói.
    - Cơ sở vật lý: Khi giận dữ hoặc ghê tởm, người ta hay nghiến răng hoặc bật hơi mạnh (âm vô thanh), tạo ra tín hiệu thay đổi dấu +/- liên tục.
    - Tại sao chọn? Rất tốt để phát hiện sự Ghê tởm (Disgust) hoặc Giận dữ (tiếng rít qua kẽ răng).

5. Jitter - Độ rung của cao độ (Micro-tremor)
    - Nó đo cái gì? Sự không ổn định của tần số dây thanh quản (giọng bị run).
    - Cơ sở vật lý: Khi bạn khóc (Buồn) hoặc run rẩy (Sợ), bạn không kiểm soát được hơi thở ổn định -> Dây thanh quản rung lỗi nhịp -> Jitter tăng cao. Ngược lại, khi Giận dữ, bạn gồng mình kiểm soát giọng rất chặt -> Jitter thấp.
    - Tại sao chọn? Đây là "vũ khí" để phân biệt Buồn/Sợ (Run rẩy) với Giận/Bình thường (Ổn định).
    - Dữ liệu của bạn: SAD (Jitter ~40) > ANG (Jitter ~24). Rất chuẩn!

6. Shimmer - Độ rung của âm lượng
    - Nó đo cái gì? Giống Jitter nhưng đo sự thay đổi về độ to nhỏ liên tục (lúc to lúc bé trong tích tắc).
    - Cơ sở vật lý: Hơi thở bị ngắt quãng, không đều (nấc, nghẹn ngào).
    - Tại sao chọn? Bổ trợ cho Jitter để phát hiện các cảm xúc tiêu cực như Đau khổ, Sợ hãi.

7. TEO (Teager Energy Operator) - Độ căng cơ/Stress (QUAN TRỌNG NHẤT)
    - Nó đo cái gì? Năng lượng thực sự cần thiết để tạo ra âm thanh (áp lực luồng khí + độ căng cứng của cơ).
    - Cơ sở vật lý: Đây là đặc trưng phi tuyến tính.
    - Khi Vui (Happy): Bạn cười to, RMS lớn, nhưng cơ cổ họng thả lỏng.
    - Khi Giận (Angry): Bạn hét to, RMS cũng lớn, NHƯNG cơ cổ họng thắt chặt lại, luồng hơi bị nén cực mạnh.

Tại sao chọn?
    - RMS không thể phân biệt được Vui và Giận (vì cả 2 đều to).
    - TEO chính là chìa khóa: Giận dữ có TEO cao gấp 5-10 lần Vui vẻ vì sự "căng cứng" của cơ thể.

    - Dữ liệu của bạn: ANG (TEO ~2.7 triệu) >> HAP (TEO ~500k). Khác biệt một trời một vực!

Tóm lại: Chiến thuật nhận diện của chúng ta
Việc kết hợp 7 chỉ số này tạo ra một "bản đồ" nhận diện hoàn hảo:
    - RMS: Phân loại sơ bộ (Nhóm Mạnh vs Nhóm Yếu).
    - Pitch: Phân loại Cao độ (Nhóm Cao vs Nhóm Trầm).
    - TEO: Phân biệt "Căng thẳng" (Giận) vs "Thoải mái" (Vui).
    - Jitter/Shimmer: Phân biệt "Run rẩy" (Buồn/Sợ) vs "Ổn định" (Bình thường).
