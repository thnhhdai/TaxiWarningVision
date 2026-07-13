# Taxi Warning Vision - Hệ thống Giám sát Tài xế (DMS)

Một hệ thống giám sát tài xế thời gian thực sử dụng computer vision để phát hiện các dấu hiệu mệt mỏi và mất tập trung, giúp giảm thiểu tai nạn giao thông.

## 📋 Giới thiệu

Taxi Warning Vision là giải pháp công nghệ hỗ trợ tài xế taxi và người lái xe đường dài bằng cách:

- **Phát hiện buồn ngủ**: Theo dõi mức độ nhắm mắt thông qua chỉ số EAR
- **Đếm ngáp**: Theo dõi mức độ há miệng để đánh giá mức độ mệt mỏi
- **Cảnh báo mất tập trung**: Phát hiện khi tài xế quay mặt hoặc cúi đầu
- **Còi hú tự động**: Kích hoạt âm thanh cảnh báo khi phát hiện nguy hiểm
- **Dashboard trực quan**: Hiển thị chỉ số sinh học thời gian thực

## 🛠️ Công nghệ sử dụng

- **Python 3.14+**
- **GUI**: customtkinter - Giao diện hiện đại, tối ưu cho màn hình retina
- **Computer Vision**: OpenCV, cvzone FaceMesh
- **Face Detection**: MediaPipe Face Mesh (468 điểm mốc khuôn mặt)
- **Audio**: Pygame mixer - Phát âm thanh cảnh báo

## 📁 Cấu trúc dự án

```
TaxiWarnningVision/
├── main.py                    # File khởi động ứng dụng
├── requirements.txt           # Danh sách thư viện cần thiết
├── face_landmarker.task       # Model nhận diện khuôn mặt MediaPipe
├── assets/
│   └── warnning_sound.mp3     # File âm thanh còi cảnh báo
└── src/
    ├── __init__.py
    ├── ui_display.py          # Giao diện chính & xử lý video
    ├── camera_handler.py      # Trích xuất điểm mốc khuôn mặt
    └── ai_logic.py            # Tính toán EAR, MAR, hướng đầu
```

## 📥 Tải xuống & Cài đặt

### Bước 1: Kiểm tra Python

Đảm bảo máy tính đã cài đặt Python 3.14 trở lên. Kiểm tra bằng lệnh:

```bash
python --version
# hoặc
python3 --version
```

Nếu chưa cài, tải Python từ: [python.org](https://www.python.org/downloads/)

---

### Bước 2: Clone dự án từ GitHub

Mở Terminal (Linux/Mac) hoặc Command Prompt/PowerShell (Windows) và chạy:

```bash
# Clone repository về máy
git clone https://github.com/thnhhdai/TaxiWarnningVision.git

# Di chuyển vào thư mục dự án
cd TaxiWarnningVision
```

---

### Bước 3: Tạo môi trường ảo (Virtual Environment)

Môi trường ảo giúp cô lập các thư viện của dự án, tránh xung đột với các project khác.

**Linux / macOS:**
```bash
# Tạo môi trường ảo
python3 -m venv .venv

# Kích hoạt môi trường ảo
source .venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
# Tạo môi trường ảo
python -m venv .venv

# Kích hoạt môi trường ảo
.venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
# Tạo môi trường ảo
python -m venv .venv

# Kích hoạt môi trường ảo
.venv\Scripts\Activate.ps1
```

> 💡 **Dấu hiệu đã kích hoạt thành công**: Terminal hiện prefix `(.venv)` trước dòng lệnh

---

### Bước 4: Cài đặt thư viện cần thiết

```bash
pip install -r requirements.txt
```

Quá trình này sẽ cài đặt:
- customtkinter (Giao diện)
- opencv-python, cvzone (Xử lý ảnh)
- mediapipe (Nhận diện khuôn mặt)
- pygame (Âm thanh)
- và các thư viện khác...

> ⏱️ **Thời gian cài đặt**: Khoảng 2-5 phút tùy tốc độ mạng

---

### Bước 5: Kiểm tra cài đặt

```bash
# Kiểm tra các thư viện chính
python -c "import cv2; import mediapipe; import customtkinter; print('Cài đặt thành công!')"
```

Nếu không có lỗi xuất hiện, bạn đã sẵn sàng chạy ứng dụng.

## 📖 Hướng dẫn sử dụng

### Khởi động ứng dụng

```bash
python main.py
```

> ⚠️ **Lưu ý**: Đảm bảo đã kích hoạt môi trường ảo trước khi chạy (có prefix `(.venv)`)

### Quy trình hoạt động

### Quy trình hoạt động

1. **Bắt đầu giám sát**: Nhấn nút **"▶ Bắt đầu giám sát"**
2. **Tự động hiệu chuẩn**: Hệ thống sẽ tự hiệu chuẩn trong 3 giây đầu (nhìn thẳng vào camera)
3. **Theo dõi chỉ số**: Các chỉ số hiển thị thời gian thực trên màn hình

### Các chỉ số hiển thị

| Chỉ số | Ý nghĩa | Trạng thái bình thường | Trạng thái cảnh báo |
|--------|---------|------------------------|---------------------|
| **EAR (Mắt)** | Mức độ mở mắt | > 0.25 | < 0.25 (Nhắm mắt) |
| **MAR (Miệng)** | Mức độ mở miệng | < 0.50 | > 0.50 (Đang ngáp) |
| **HƯỚNG MẶT** | Hướng xoay đầu | NHÌN THẲNG | QUAY TRÁI/PHẢI/CÚI |
| **SỐ LẦN NGÁP** | Tổng số lần ngáp | - | Tăng dần |

### Ngưỡng cảnh báo

- **Buồn ngủ**: Nhắm mắt liên tục > **2 giây**
- **Ngáp**: Há miệng > **1.5 giây** (tính 1 lần ngáp)
- **Mất tập trung**: Quay mặt hoặc cúi đầu > **2 giây**

### Trạng thái hệ thống

| Trạng thái | Màu sắc | Ý nghĩa |
|------------|---------|---------|
| SẴN SÀNG | 🟢 Xanh lá | Hệ thống sẵn sàng |
| ĐANG CALIB | 🟡 Vàng | Đang hiệu chuẩn (3s) |
| ĐANG GIÁM SÁT | 🟢 Xanh lá | Đang hoạt động bình thường |
| NGỦ GẬT! | 🔴 Đỏ | Phát hiện buồn ngủ |
| MẤT TẬP TRUNG! | 🔴 Đỏ | Phát hiện mất tập trung |
| MẤT DẤU MẶT! | 🟠 Cam | Không thấy khuôn mặt |

## 🔬 Giải thuật

### Eye Aspect Ratio (EAR) - Tỷ lệ mở mắt

```
EAR = (|p2-p6| + |p3-p5|) / (2 × |p1-p4|)
```

- Giá trị EAR cao = Mắt mở
- Giá trị EAR thấp = Mắt nhắm
- Ngưỡng tự động hiệu chỉnh: 72% mức mở mắt bình thường

### Mouth Aspect Ratio (MAR) - Tỷ lệ mở miệng

```
MAR = (v1 + v2 + v3) / (3 × h)
```

- Giá trị MAR cao = Đang ngáp
- Giá trị MAR thấp = Miệng đóng

### Head Pose Estimation - Ước lượng hướng đầu

Sử dụng tỷ lệ khoảng cách mũi-mắt để xác định:
- **Yaw**: Quay trái/phải (tỷ lệ khoảng cách mũi-mắt trái/phải)
- **Pitch**: Cúi đầu (độ lệch thẳng đứng của mũi so với mắt)

## 💻 Yêu cầu phần cứng

- **Camera**: Webcam (builtin hoặc USB) độ phân giải ≥ 720p
- **CPU**: Tối thiểu Dual-core 2.0GHz
- **RAM**: 4GB trở lên
- **Khuyến nghị**: Card GPU để xử lý video mượt hơn

## 🔧 Xử lý sự cố

### Camera không hoạt động

- Kiểm tra quyền truy cập camera
- Đảm bảo không có ứng dụng khác đang sử dụng camera
- Thử kết nối lại USB (nếu dùng camera rời)

### Thường xuyên báo "Mất dấu khuôn mặt"

- Cải thiện ánh sáng (tránh ánh sáng quá mạnh/quá yếu)
- Đặt camera ngang tầm mắt
- Tránh góc quay cực đoan

### Không có âm thanh cảnh báo

- Kiểm tra file `assets/warnning_sound.mp3` có tồn tại
- Kiểm tra cài đặt âm thanh hệ thống
- Tăng volume âm máy

## 📝 Nguồn tham khảo

- MediaPipe Face Mesh Documentation
- cvzone Face Detection Module
- customtkinter Documentation

## 📜 Giấy phép

Dự án này được tạo ra cho mục đích học tập và demonstrating.

---

**Lưu ý**: Hệ thống này là công cụ hỗ trợ, không thay thế hoàn toàn sự tập trung của tài xế khi lái xe.
