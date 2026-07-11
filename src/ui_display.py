# src/ui_display.py - Main dashboard GUI and video processing
import cv2
import customtkinter as ctk
from PIL import Image
from cvzone.FaceMeshModule import FaceMeshDetector
import time
import threading
import pygame

from src.camera_handler import get_clean_landmarks
from src.ai_logic import calculate_ear, calculate_mar, check_distraction

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
AUDIO_PATH = "assets/warnning_sound.mp3"

def play_warning_sound(audio_path, app_instance):
    """Play warning alarm loop that stops when safe state restored"""
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play(loops=-1)

        while pygame.mixer.music.get_busy():
            if (not app_instance.ALARM and not app_instance.DISTRACT_ALARM) or not app_instance.camera_running:
                pygame.mixer.music.stop()
                break
            time.sleep(0.1)
    except Exception as e:
        print(f"Error playing sound: {e}")
    finally:
        pygame.mixer.quit()


class MainDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Taxi Warning Vision - DMS System")
        self.root.geometry("980x620")
        self.root.configure(fg_color="#1e1e2e")

        # Camera & Detector setup
        self.detector = FaceMeshDetector(maxFaces=1)
        self.cap = cv2.VideoCapture(0)
        self.camera_running = False

        # Alert thresholds
        self.EAR_THRESHOLD = 0.25
        self.MAR_THRESHOLD = 0.50
        self.CLOSED_EYE_TIME = 2.0
        self.MAX_DISTRACTED_TIME = 2.0
        self.YAWN_DURATION_LIMIT = 1.5

        # State variables
        self.ALARM = False
        self.DISTRACT_ALARM = False
        self.eye_closed_start_time = None
        self.distracted_start_time = None
        self.yawn_start_time = None
        self.yawn_count = 0
        self.current_ear_value = 0.0
        self.current_mar_value = 0.0
        self.current_pose_status = "STRAIGHT"
        self.current_frame = None
        self.app_is_closing = False
        self.is_sound_playing = False

        # Calibration state
        self.is_calibrating = False
        self.calibration_start_time = None
        self.calibration_ears = []

        # GUI Layout
        self.sidebar_frame = ctk.CTkFrame(self.root, width=300, corner_radius=10, fg_color="#252538")
        self.sidebar_frame.pack(side="left", fill="y", padx=15, pady=15)
        self.sidebar_frame.pack_propagate(False)

        self.main_frame = ctk.CTkFrame(self.root, corner_radius=10, fg_color="#252538")
        self.main_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        # Sidebar components
        self.title_label = ctk.CTkLabel(self.sidebar_frame, text="BẢNG ĐIỀU KHIỂN DMS",
                                         font=("Arial", 16, "bold"), text_color="#00FFCC")
        self.title_label.pack(pady=20)

        self.ear_label = ctk.CTkLabel(self.sidebar_frame, text="EAR (Mắt): -- [OFF]",
                                       font=("Arial", 13, "bold"), text_color="#FFFFFF", anchor="w")
        self.ear_label.pack(pady=8, padx=25, fill="x")

        self.mar_label = ctk.CTkLabel(self.sidebar_frame, text="MAR (Miệng): -- [OFF]",
                                       font=("Arial", 13, "bold"), text_color="#FFFFFF", anchor="w")
        self.mar_label.pack(pady=8, padx=25, fill="x")

        self.pose_label = ctk.CTkLabel(self.sidebar_frame, text="HƯỚNG MẶT: -- [OFF]",
                                        font=("Arial", 13, "bold"), text_color="#FFFFFF", anchor="w")
        self.pose_label.pack(pady=8, padx=25, fill="x")

        self.yawn_counter_label = ctk.CTkLabel(self.sidebar_frame, text="SỐ LẦN NGÁP: 0",
                                                font=("Arial", 14, "bold"), text_color="#00FFCC", anchor="w")
        self.yawn_counter_label.pack(pady=15, padx=25, fill="x")

        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="Hệ thống: SẴN SÀNG",
                                          font=("Arial", 14, "bold"), text_color="#00FFCC")
        self.status_label.pack(pady=15)

        # Control buttons
        self.btn_start = ctk.CTkButton(self.sidebar_frame, text="▶ Bắt đầu giám sát",
                                         command=self.start_monitoring, fg_color="#2a9d8f",
                                         hover_color="#264653", font=("Arial", 13, "bold"), height=38)
        self.btn_start.pack(pady=12, padx=25, fill="x")

        self.btn_stop = ctk.CTkButton(self.sidebar_frame, text="🛑 Dừng giám sát",
                                        command=self.stop_monitoring, fg_color="#e63946",
                                        hover_color="#c1121f", font=("Arial", 13, "bold"), height=38)
        self.btn_stop.pack(pady=5, padx=25, fill="x")

        # Video display
        self.video_label = ctk.CTkLabel(self.main_frame,
                                         text="Hệ thống đang tạm dừng.\nNhấn 'Bắt đầu giám sát' để kích hoạt.",
                                         font=("Arial", 14))
        self.video_label.pack(fill="both", expand=True, padx=10, pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Start AI processing thread
        self.ai_thread = threading.Thread(target=self.video_processing_worker, daemon=True)
        self.ai_thread.start()
        self.update_gui_loop()

    def start_monitoring(self):
        if not self.camera_running:
            self.camera_running = True
            self.is_calibrating = True
            self.calibration_start_time = time.time()
            self.calibration_ears = []

    def stop_monitoring(self):
        if self.camera_running:
            self.camera_running = False
            self.is_calibrating = False
            self.eye_closed_start_time = None
            self.distracted_start_time = None
            self.yawn_start_time = None
            self.ALARM = False
            self.DISTRACT_ALARM = False
            self.video_label.configure(image="", text="Hệ thống giám sát đã TẠM DỪNG.")
            self.status_label.configure(text="Hệ thống: TẠM DỪNG", text_color="#FFCC00")

    def run_sound_thread(self):
        """Trigger warning alarm if danger detected"""
        if not self.is_sound_playing and (self.ALARM or self.DISTRACT_ALARM):
            self.is_sound_playing = True
            def wrapper():
                play_warning_sound(AUDIO_PATH, self)
                self.is_sound_playing = False
            threading.Thread(target=wrapper, daemon=True).start()

    def video_processing_worker(self):
        """AI processing loop - runs in background thread"""
        while not self.app_is_closing:
            if self.camera_running:
                ret, frame = self.cap.read()
                if ret:
                    frame = cv2.flip(frame, 1)
                    frame, faces = self.detector.findFaceMesh(frame, draw=False)

                    if faces:
                        single_face = faces[0]
                        payload = get_clean_landmarks(single_face)

                        # Draw landmarks on frame
                        for pt in payload:
                            cv2.circle(frame, (pt['x'], pt['y']), 1, (0, 255, 0), cv2.FILLED)

                        current_ear = calculate_ear(payload)

                        if current_ear is None:
                            self.current_ear_value = 0.0
                            self.eye_closed_start_time = None
                            self.distracted_start_time = None
                            self.current_pose_status = "LOST_FACE"
                        else:
                            self.current_ear_value = current_ear

                            # Auto-calibration phase (first 3 seconds)
                            if self.is_calibrating:
                                self.calibration_ears.append(current_ear)
                                elapsed_calib = time.time() - self.calibration_start_time
                                cv2.putText(frame, f"CALIBRATING... ({3 - int(elapsed_calib)}s)", (30, 40),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                                if elapsed_calib >= 3.0:
                                    if self.calibration_ears:
                                        avg_open_ear = sum(self.calibration_ears) / len(self.calibration_ears)
                                        self.EAR_THRESHOLD = avg_open_ear * 0.72
                                    self.is_calibrating = False
                            else:
                                # Drowsiness detection
                                if current_ear < self.EAR_THRESHOLD:
                                    if self.eye_closed_start_time is None:
                                        self.eye_closed_start_time = time.time()
                                    else:
                                        if time.time() - self.eye_closed_start_time > self.CLOSED_EYE_TIME:
                                            self.ALARM = True
                                            self.run_sound_thread()
                                else:
                                    self.eye_closed_start_time = None
                                    self.ALARM = False

                                # Yawn detection
                                current_mar = calculate_mar(payload)
                                self.current_mar_value = current_mar

                                if current_mar > self.MAR_THRESHOLD:
                                    if self.yawn_start_time is None:
                                        self.yawn_start_time = time.time()
                                    else:
                                        if time.time() - self.yawn_start_time > self.YAWN_DURATION_LIMIT:
                                            self.yawn_count += 1
                                            self.yawn_start_time = None
                                else:
                                    self.yawn_start_time = None

                                # Distraction detection
                                pose_res = check_distraction(payload)
                                self.current_pose_status = pose_res

                                if pose_res in ["LEFT", "RIGHT", "DOWN"]:
                                    if self.distracted_start_time is None:
                                        self.distracted_start_time = time.time()
                                    else:
                                        if time.time() - self.distracted_start_time > self.MAX_DISTRACTED_TIME:
                                            self.DISTRACT_ALARM = True
                                            self.run_sound_thread()
                                else:
                                    self.distracted_start_time = None
                                    self.DISTRACT_ALARM = False

                        # Overlay status on frame
                        text_eye = "CLOSED" if self.current_ear_value < self.EAR_THRESHOLD else "OPEN"
                        cv2.putText(frame, f"EAR: {self.current_ear_value:.3f} [{text_eye}]", (30, 40),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

                        # Use English text to avoid OpenCV font rendering issues with Vietnamese
                        if self.ALARM or self.DISTRACT_ALARM:
                            cv2.putText(frame, "!!! DANGER ALARM !!!", (30, 90),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 3)
                    else:
                        self.eye_closed_start_time = None
                        self.distracted_start_time = None
                        self.current_pose_status = "LOST_FACE"

                    self.current_frame = frame.copy()
            time.sleep(0.015)

    def update_gui_loop(self):
        """Update GUI display loop"""
        if self.camera_running and self.current_frame is not None:
            rgb_image = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_image)

            self.img_tk = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(620, 470))
            self.video_label.configure(image=self.img_tk, text="")

            if self.is_calibrating:
                self.ear_label.configure(text=f"EAR (Mắt): {self.current_ear_value:.2f} [CALIB]", text_color="#FFCC00")
                self.mar_label.configure(text="MAR (Miệng): Đang tính toán...", text_color="#FFCC00")
                self.pose_label.configure(text="HƯỚNG MẶT: Đang định vị...", text_color="#FFCC00")
                self.status_label.configure(text="Hệ thống: ĐANG CALIB...", text_color="#FFCC00")
            else:
                if self.current_pose_status == "LOST_FACE":
                    self.ear_label.configure(text="EAR (Mắt): MẤT DẤU", text_color="#FF9900")
                    self.mar_label.configure(text="MAR (Miệng): MẤT DẤU", text_color="#FF9900")
                    self.pose_label.configure(text="HƯỚNG MẶT: KHÔNG XÁC ĐỊNH", text_color="#FF9900")
                    self.status_label.configure(text="CẢNH BÁO: MẤT DẤU MẶT!", text_color="#FF9900")
                else:
                    if self.current_ear_value >= self.EAR_THRESHOLD:
                        self.ear_label.configure(text=f"EAR (Mắt): {self.current_ear_value:.2f} [OPEN]", text_color="#FFFFFF")
                    else:
                        self.ear_label.configure(text=f"EAR (Mắt): {self.current_ear_value:.2f} [CLOSED]", text_color="#FF3333")

                    text_mar_status = "YAWN" if self.current_mar_value > self.MAR_THRESHOLD else "NORMAL"
                    color_mar = "#FF9900" if text_mar_status == "YAWN" else "#FFFFFF"
                    self.mar_label.configure(text=f"MAR (Miệng): {self.current_mar_value:.2f} [{text_mar_status}]", text_color=color_mar)

                    # Mirror mode fix: AI returns LEFT/RIGHT from camera perspective,
                    # flip them for driver's mirror view
                    pose_vi_dict = {
                        "STRAIGHT": "NHÌN THẲNG",
                        "LEFT": "QUAY PHẢI",
                        "RIGHT": "QUAY TRÁI",
                        "DOWN": "CÚI ĐẦU"
                    }
                    text_pose = pose_vi_dict.get(self.current_pose_status, "NHÌN THẲNG")
                    color_pose = "#FF3333" if self.current_pose_status in ["LEFT", "RIGHT", "DOWN"] else "#FFFFFF"
                    self.pose_label.configure(text=f"HƯỚNG MẶT: {text_pose}", text_color=color_pose)

                    self.yawn_counter_label.configure(text=f"SỐ LẦN NGÁP: {self.yawn_count}")

                    if self.ALARM:
                        self.status_label.configure(text="CẢNH BÁO: NGỦ GẬT!", text_color="#FF3333")
                    elif self.DISTRACT_ALARM:
                        self.status_label.configure(text="CẢNH BÁO: MẤT TẬP TRUNG!", text_color="#FF3333")
                    else:
                        self.status_label.configure(text="Hệ thống: ĐANG GIÁM SÁT", text_color="#00FFCC")

        self.root.after(15, self.update_gui_loop)

    def on_closing(self):
        """Cleanup on application exit"""
        self.app_is_closing = True
        self.camera_running = False
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
        except:
            pass
        if self.cap.isOpened():
            self.cap.release()
        self.root.destroy()
