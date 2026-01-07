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