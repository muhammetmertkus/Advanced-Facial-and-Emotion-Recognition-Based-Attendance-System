import sys
import cv2
import os
import threading
import numpy as np
import pickle
import pandas as pd
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QThread
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog, QMessageBox,
    QTableWidgetItem, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout,
    QFormLayout, QSpinBox, QTableWidget, QTextEdit, QComboBox, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QColor, QImage, QPixmap, QIcon
from datetime import datetime
import face_recognition
from deepface import DeepFace
from login import Ui_Login
from ui_main import Ui_AttendanceSystem
from ui_splash_screen import Ui_SplashScreen 
from PhotoCaptureDialog import PhotoCaptureDialog

# VideoThread sınıfı burada tanımlanır
class VideoThread(QThread):
    change_pixmap_signal = Signal(QImage)
    attendance_signal = Signal(str)
    frame_available = Signal(np.ndarray)  # En son çerçeveyi yayınlamak için yeni sinyal

    def __init__(self, known_face_encodings, known_face_names):
        super().__init__()
        self._run_flag = True
        self.known_face_encodings = known_face_encodings
        self.known_face_names = known_face_names
        self.frame_count = 0  # Yüz tanıma sıklığını kontrol etmek için
        self.process_attendance = False  # Yoklama işlemi aktif mi
        self.latest_frame = None  # En son çerçeveyi saklamak için

    def run(self):
        # Kamerayı başlatma (DirectShow kullanarak daha stabil olabilir)
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            print("Kamera açılamadı.")
            return

        print("VideoThread başlatıldı.")
        while self._run_flag:
            ret, frame = self.cap.read()
            if ret:
                self.latest_frame = frame.copy()
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                if self.process_attendance:
                    self.frame_count += 1
                    if self.frame_count % 5 == 0:  # Her 5 çerçevede bir yüz tanıma
                        face_locations = face_recognition.face_locations(rgb_frame)
                        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                            name = "Unknown"

                            if True in matches:
                                first_match_index = matches.index(True)
                                name = self.known_face_names[first_match_index]
                                # Yoklamayı işaretleme
                                self.attendance_signal.emit(name)

                            # Yüzün etrafına kare çizme
                            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                            # Öğrenci numarası ve ismini yazma
                            student_info = name.replace('_', ' ')
                            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                            font = cv2.FONT_HERSHEY_DUPLEX
                            cv2.putText(frame, student_info, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

                # Çerçeveyi RGB'den BGR'ye dönüştürerek QImage'e çevirme
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                convert_to_qt_format = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                scaled_image = convert_to_qt_format.scaled(640, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.change_pixmap_signal.emit(scaled_image)

                # En son çerçeveyi yayınla
                self.frame_available.emit(self.latest_frame)

        print("VideoThread durduruldu.")
        self.cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()

    def set_process_attendance(self, flag: bool):
        self.process_attendance = flag
        if not flag:
            self.frame_count = 0  # Yoklama işlemi durdurulduğunda frame sayısını sıfırla

class SplashScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self)

        # Remove title bar and set background translucent
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Start timer to control splash screen duration
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.counter = 0  # For progress bar update
        self.timer.start(30)  # Milliseconds between each progress update

        # Show splash screen
        self.show()

    def update_progress(self):
        self.counter += 1
        self.ui.labelPercentage.setText(f"<p><span style='font-size:68pt;'>{self.counter}</span><span style='font-size:58pt; vertical-align:super;'>%</span></p>")
        self.update_progress_bar(self.counter)

        if self.counter >= 100:
            self.timer.stop()
            self.open_login()

    def update_progress_bar(self, value):
        # Update the circular progress bar
        progress = (100 - value) / 100.0
        stop_1 = str(max(0, min(progress - 0.001, 1)))
        stop_2 = str(max(0, min(progress, 1)))
        styleSheet = f"""
        QFrame {{
            border-radius: 150px;
            background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{stop_1} rgba(255, 0, 127, 0), stop:{stop_2} rgba(85, 170, 255, 255));
        }}
        """
        self.ui.circularProgress.setStyleSheet(styleSheet)

    def open_login(self):
        self.login_window = LoginUI()
        self.login_window.show()
        self.close()  # Close splash screen

# Login UI Class
class LoginUI(QMainWindow):
    def __init__(self):
        super(LoginUI, self).__init__()
        self.ui = Ui_Login()
        self.ui.setupUi(self)

        # Remove window frame
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Connect buttons
        self.ui.close_button.clicked.connect(self.close)
        self.ui.minimize_button.clicked.connect(self.showMinimized)
        self.ui.login_button.clicked.connect(self.check_login)

    def check_login(self):
        # Fixed username and password
        username = self.ui.lineEdit.text()
        password = self.ui.lineEdit_2.text()

        if username == "admin" and password == "admin123":
            self.open_main_window()
        else:
            QMessageBox.warning(self, "Giriş Başarısız", "Yanlış kullanıcı adı veya şifre!")

    def open_main_window(self):
        self.main_window = AttendanceSystem()
        self.main_window.show()
        self.close()  # Close the login window

class AttendanceSystem(QWidget):
    update_info_signal = Signal(str)  # Var olan sinyal

    def __init__(self):
        super().__init__()
        self.ui = Ui_AttendanceSystem()
        self.ui.setup_ui(self)

        self.known_face_encodings = []
        self.known_face_names = []
        self.attendance_data = {}
        self.lesson_list = []
        self.lesson_details = {}
        self.current_photo = None
        self.unidentified_faces = []
        self.latest_frame = None  # En son çerçeveyi saklamak için

        # Load data
        self.load_lessons()
        self.load_known_faces()
        self.load_attendance_data()
        self.load_students()

        # Connect signals and slots
        self.ui.capture_btn.clicked.connect(self.take_attendance)
        self.ui.add_student_btn.clicked.connect(self.add_student)
        self.ui.add_manual_btn.clicked.connect(self.add_manual_student)
        self.ui.show_history_btn.clicked.connect(self.display_attendance_history)
        self.ui.calculate_btn.clicked.connect(self.calculate_absenteeism)
        self.ui.photo_select_btn.clicked.connect(self.select_photo)
        self.ui.photo_capture_btn.clicked.connect(self.capture_photo)
        self.ui.add_lesson_btn.clicked.connect(self.add_lesson)
        self.ui.remove_lesson_btn.clicked.connect(self.remove_lesson)
        self.ui.lesson_selector.currentTextChanged.connect(self.update_lesson_details)
        self.ui.show_photo_btn.clicked.connect(self.display_photo)
        self.ui.photo_capture_btn.clicked.connect(self.open_photo_capture_dialog)
        
        # Bağlantı: Canlı Kamera Yoklama butonu
        self.ui.live_attendance_btn.clicked.connect(self.toggle_live_attendance)

        # Connect update signal
        self.update_info_signal.connect(self.update_info_text)

        # VideoThread değişkeni
        self.video_thread = None

        # Start video feed on startup
        self.start_video_feed()

    def start_video_feed(self):
        # Start VideoThread for video display
        self.video_thread = VideoThread(self.known_face_encodings, self.known_face_names)
        self.video_thread.change_pixmap_signal.connect(self.update_image)
        self.video_thread.attendance_signal.connect(self.mark_attendance)
        self.video_thread.frame_available.connect(self.store_latest_frame)  # En son çerçeveyi sakla
        self.video_thread.start()

    def toggle_live_attendance(self):
        if self.video_thread is None:
            # VideoThread başlatılmamışsa başlat
            self.start_video_feed()

        if not self.video_thread.process_attendance:
            # Canlı yoklamayı başlat
            self.start_live_attendance()
        else:
            # Canlı yoklamayı durdur
            self.stop_live_attendance()

    def start_live_attendance(self):
        lesson = self.ui.lesson_selector.currentText().strip()
        if not lesson:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir ders seçin.")
            return

        self.video_thread.set_process_attendance(True)

        # Buton metnini ve ikonunu güncelle
        self.ui.live_attendance_btn.setText("Canlı Yoklamayı Durdur")
        self.ui.live_attendance_btn.setIcon(QIcon("icons/stop_camera.png"))

    def stop_live_attendance(self):
        self.video_thread.set_process_attendance(False)

        # Buton metnini ve ikonunu güncelle
        self.ui.live_attendance_btn.setText("Canlı Kamera Yoklama")
        self.ui.live_attendance_btn.setIcon(QIcon("icons/live_camera.png"))

    @Slot(QImage)
    def update_image(self, qimage):
        # Resize the image to fit the label
        label_size = self.ui.image_label.size()
        pixmap = QPixmap.fromImage(qimage).scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.image_label.setPixmap(pixmap)

    @Slot(str)
    def mark_attendance(self, name):
        # Yoklama işlemi burada yapılır
        lesson = self.ui.lesson_selector.currentText().strip()
        week = self.ui.week_selector.value()
        lesson_number = self.ui.lesson_number_selector.value()

        if not lesson:
            self.update_info_signal.emit("Lütfen bir ders seçin.")
            return

        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Yoklama verisini güncelleme
        new_data = {
            'Tarih': date,
            'Ders': lesson,
            'Hafta': week,
            'Ders Numarası': lesson_number,
            'Öğrenci': name,
            'Durum': '+'
        }

        if lesson not in self.attendance_data:
            self.attendance_data[lesson] = pd.DataFrame(columns=['Tarih', 'Ders', 'Hafta', 'Ders Numarası', 'Öğrenci', 'Durum'])

        self.attendance_data[lesson] = pd.concat([self.attendance_data[lesson], pd.DataFrame([new_data])], ignore_index=True)

        try:
            self.attendance_data[lesson].to_csv(f'{lesson}_yoklama.csv', index=False)
            self.update_info_signal.emit(f"{name.replace('_', ' ')} yoklamaya eklendi.")
        except Exception as e:
            self.update_info_signal.emit(f"Yoklama verileri kaydedilemedi: {str(e)}")

    @Slot(np.ndarray)
    def store_latest_frame(self, frame):
        self.latest_frame = frame.copy()

    def take_attendance(self):
        if self.latest_frame is None:
            QMessageBox.warning(self, "Uyarı", "Henüz bir kare alınmadı. Lütfen biraz bekleyin.")
            return

        self.ui.capture_btn.setEnabled(False)
        threading.Thread(target=self.process_attendance).start()

    def process_attendance(self):
        try:
            lesson = self.ui.lesson_selector.currentText().strip()
            week = self.ui.week_selector.value()
            lesson_number = self.ui.lesson_number_selector.value()

            if not lesson:
                self.update_info_signal.emit("Lütfen bir ders seçin.")
                return

            frame = self.latest_frame.copy()
            if frame is None:
                self.update_info_signal.emit("Kamera görüntüsü alınamadı.")
                return

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            present_students = []
            self.unidentified_faces = []
            emotions_detected = []
            age_gender_race_info = []

            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                name = "Unknown"

                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.known_face_names[first_match_index]
                    present_students.append(name)
                else:
                    self.unidentified_faces.append(face_encoding)

                # DeepFace ile yaş, cinsiyet, ırk ve duyguları analiz edelim
                top, right, bottom, left = face_location
                face_image = rgb_frame[top:bottom, left:right]
                try:
                    # DeepFace ile çoklu analiz (yaş, cinsiyet, ırk ve duygular)
                    analysis = DeepFace.analyze(face_image, actions=['age', 'gender', 'race', 'emotion'], enforce_detection=False)
                    if isinstance(analysis, list):
                        analysis = analysis[0]

                    # Yaş, cinsiyet, ırk bilgisi
                    age = analysis.get('age', 'Unknown')
                    gender = analysis.get('gender', 'Unknown')
                    dominant_race = analysis.get('dominant_race', 'Unknown')
                    age_gender_race_info.append((name.replace('_', ' '), age, gender, dominant_race))

                    # Duygusal analiz
                    dominant_emotion = analysis.get('dominant_emotion', 'Unknown')
                    emotions_detected.append((name.replace('_', ' '), dominant_emotion))

                except Exception as e:
                    age_gender_race_info.append((name.replace('_', ' '), 'Unknown', 'Unknown', 'Unknown'))
                    emotions_detected.append((name.replace('_', ' '), 'Unknown'))

            # Tarih, ders ve diğer bilgileri güncelleme
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_data = []

            for student in self.known_face_names:
                status = '+' if student in present_students else '-'
                new_data.append({
                    'Tarih': date,
                    'Ders': lesson,
                    'Hafta': week,
                    'Ders Numarası': lesson_number,
                    'Öğrenci': student,
                    'Durum': status
                })

            if lesson not in self.attendance_data:
                self.attendance_data[lesson] = pd.DataFrame(columns=['Tarih', 'Ders', 'Hafta', 'Ders Numarası', 'Öğrenci', 'Durum'])

            self.attendance_data[lesson] = pd.concat([self.attendance_data[lesson], pd.DataFrame(new_data)], ignore_index=True)

            try:
                self.attendance_data[lesson].to_csv(f'{lesson}_yoklama.csv', index=False)
            except Exception as e:
                self.update_info_signal.emit(f"Yoklama verileri kaydedilemedi: {str(e)}")
                return

            present_count = len(present_students)
            total_faces = len(face_locations)
            unidentified_count = len(self.unidentified_faces)

            # Bilgi mesajını güncelleme
            info = f"Tarih: {date}\nDers: {lesson}\nHafta: {week}\nDers Numarası: {lesson_number}\n"
            info += f"Sınıftaki toplam kişi sayısı: {total_faces}\n"
            info += f"Tanımlanabilen öğrenci sayısı: {present_count}\n"
            info += f"Tanımlanamayan kişi sayısı: {unidentified_count}\n"

            # Yaş, cinsiyet ve ırk bilgilerini ekleyelim
            age_gender_race_info_text = "\n".join([f"{name}: Yaş: {age}, Cinsiyet: {gender}, Irk: {race}" for name, age, gender, race in age_gender_race_info])
            info += f"\nYaş, Cinsiyet ve Irk Bilgileri:\n{age_gender_race_info_text}"

            # Duygusal bilgiler
            emotion_info = "\n".join([f"{name}: {emotion}" for name, emotion in emotions_detected])
            info += f"\nÖğrenci Duyguları:\n{emotion_info}"

            self.update_info_signal.emit(info)

            # Fotoğrafı kaydetme
            photo_dir = os.path.join(lesson, 'attendance_photos')
            os.makedirs(photo_dir, exist_ok=True)
            photo_path = os.path.join(photo_dir, f"{date.replace(':', '-')}_{lesson}_Hafta{week}_Ders{lesson_number}.jpg")
            cv2.imwrite(photo_path, frame)
        except Exception as e:
            self.update_info_signal.emit(f"Yoklama işlemi sırasında bir hata oluştu: {str(e)}")
        finally:
            self.ui.capture_btn.setEnabled(True)

    @Slot(str)
    def update_info_text(self, info):
        self.ui.info_text.setText(info)

    def select_photo(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Öğrenci Fotoğrafı Seç", "", "Image Files (*.png *.jpg *.bmp)")
        if file_name:
            self.ui.photo_path.setText(file_name)
            self.current_photo = cv2.imread(file_name)

    def capture_photo(self):
        # VideoThread zaten kamerayı yönetiyor, bu yüzden en son çerçeveyi kullanın
        if self.latest_frame is not None:
            self.current_photo = self.latest_frame.copy()
            self.ui.photo_path.setText("Kameradan çekildi")
        else:
            QMessageBox.warning(self, "Uyarı", "Henüz bir kare alınmadı. Lütfen biraz bekleyin.")

    def open_photo_capture_dialog(self):
        # Öğrenci bilgilerini al
        student_name = self.ui.student_name.text().strip()
        student_id = self.ui.student_id.text().strip()

        # Öğrenci bilgileri kontrolü
        if not student_name or not student_id:
            QMessageBox.warning(self, "Eksik Bilgi", "Öğrenci adı ve numarasını giriniz.")
            return

        # Kamera bağlantısının kontrolü
        if self.video_thread is None or not self.video_thread.isRunning():
            QMessageBox.critical(self, "Kamera Hatası", "Canlı yoklama başlatılmadı!")
            return

        # Fotoğraf çekim penceresini aç
        dialog = PhotoCaptureDialog(self.latest_frame, save_directory="student_photos", student_name=student_name, student_id=student_id, parent=self)

        # Dialog başarıyla tamamlandığında fotoğrafların kaydedildiğini bildir
        if dialog.exec_() == QDialog.Accepted:
            print(f"{student_name} ({student_id}) için fotoğraflar kaydedildi.")

    def add_student(self):
        name = self.ui.student_name.text()
        student_id = self.ui.student_id.text()
        selected_lesson = self.ui.lesson_selector_for_student.currentText()
        photo_path = self.ui.photo_path.text()

        if not (name and student_id and selected_lesson and (self.current_photo is not None or photo_path)):
            QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurun.")
            return

        lesson_student_photos_path = os.path.join(selected_lesson, 'student_photos')
        new_photo_path = os.path.join(lesson_student_photos_path, f"{student_id}_{name.replace(' ', '_')}.jpg")
        os.makedirs(lesson_student_photos_path, exist_ok=True)

        try:
            if self.current_photo is not None:
                cv2.imwrite(new_photo_path, self.current_photo)
                image = self.current_photo
            else:
                image = face_recognition.load_image_file(photo_path)
                cv2.imwrite(new_photo_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

            face_locations = face_recognition.face_locations(image)
            if not face_locations:
                QMessageBox.warning(self, "Uyarı", "Seçilen fotoğrafta yüz tespit edilemedi.")
                return

            face_encodings = face_recognition.face_encodings(image, face_locations)
            if not face_encodings:
                QMessageBox.warning(self, "Uyarı", "Yüz verisi alınamadı.")
                return

            face_encoding = face_encodings[0]
            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(f"{student_id}_{name}")

            QMessageBox.information(self, "Bilgi", "Öğrenci başarıyla eklendi.")
            self.ui.student_name.clear()
            self.ui.student_id.clear()
            self.ui.photo_path.clear()
            self.current_photo = None

            self.update_student_list()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Öğrenci eklenirken bir hata oluştu: {str(e)}")

    def update_student_list(self):
        students = [name.replace('_', ' ') for name in self.known_face_names]
        self.ui.student_list.setText("\n".join(students))

    def display_attendance_history(self):
        selected_lesson = self.ui.history_lesson_selector.currentText()
        if selected_lesson in self.attendance_data:
            df = self.attendance_data[selected_lesson]
            students = df['Öğrenci'].unique()
            weeks = sorted(df['Hafta'].unique())

            self.ui.attendance_table.setColumnCount(2 + len(weeks))
            self.ui.attendance_table.setRowCount(len(students))
            headers = ['Öğrenci Numarası', 'Öğrenci Adı'] + [f'Hafta {week}' for week in weeks]
            self.ui.attendance_table.setHorizontalHeaderLabels(headers)

            for row, student in enumerate(students):
                parts = student.split('_', 1)
                if len(parts) == 2:
                    student_number, student_name = parts
                else:
                    student_number = "N/A"
                    student_name = student

                self.ui.attendance_table.setItem(row, 0, QTableWidgetItem(student_number))
                self.ui.attendance_table.setItem(row, 1, QTableWidgetItem(student_name))

                for col, week in enumerate(weeks):
                    status = df[(df['Öğrenci'] == student) & (df['Hafta'] == week)]['Durum'].values
                    cell_item = QTableWidgetItem(status[0] if len(status) > 0 else 'N/A')
                    self.ui.attendance_table.setItem(row, 2 + col, cell_item)

    def calculate_absenteeism(self):
        selected_lesson = self.ui.absenteeism_lesson_selector.currentText()
        if selected_lesson not in self.attendance_data or self.attendance_data[selected_lesson].empty:
            self.ui.absenteeism_text.setText("Seçilen ders için yoklama verisi bulunamadı.")
            return

        absence_limit = self.ui.absence_limit.value()
        absence_hours = self.attendance_data[selected_lesson][self.attendance_data[selected_lesson]['Durum'] == '-'].groupby('Öğrenci').size()
        failed_students = absence_hours[absence_hours > absence_limit]
        
        if failed_students.empty:
            self.ui.absenteeism_text.setText(f"Devamsızlık sınırını ({absence_limit} saat) aşan öğrenci bulunmamaktadır.")
        else:
            result = "Devamsızlıktan Kalan Öğrenciler:\n\n"
            for student, hours in failed_students.items():
                result += f"{student.replace('_', ' ')}: {hours} saat devamsızlık\n"
            self.ui.absenteeism_text.setText(result)

    def add_manual_student(self):
        student_id = self.ui.manual_student_id.text().strip()
        if not student_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen öğrenci numarasını girin.")
            return

        lesson = self.ui.lesson_selector.currentText().strip()
        week = self.ui.week_selector.value()
        lesson_number = self.ui.lesson_number_selector.value()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        matching_students = [name for name in self.known_face_names if name.startswith(student_id)]
        if matching_students:
            student_name = matching_students[0].split('_', 1)[1]
            student_full_name = f"{student_id}_{student_name}"
        else:
            QMessageBox.warning(self, "Uyarı", "Girilen numaraya ait öğrenci bulunamadı.")
            return

        new_data = {
            'Tarih': date,
            'Ders': lesson,
            'Hafta': week,
            'Ders Numarası': lesson_number,
            'Öğrenci': student_full_name,
            'Durum': '+'
        }

        if lesson not in self.attendance_data:
            self.attendance_data[lesson] = pd.DataFrame(columns=['Tarih', 'Ders', 'Hafta', 'Ders Numarası', 'Öğrenci', 'Durum'])
        
        self.attendance_data[lesson] = pd.concat([self.attendance_data[lesson], pd.DataFrame([new_data])], ignore_index=True)

        try:
            self.attendance_data[lesson].to_csv(f'{lesson}_yoklama.csv', index=False)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Yoklama verileri kaydedilemedi: {str(e)}")
            return

        QMessageBox.information(self, "Bilgi", "Öğrenci manuel olarak eklendi.")
        self.ui.manual_student_id.clear()

    def add_lesson(self):
        new_lesson = self.ui.new_lesson_input.text().strip()
        lessons_per_week = self.ui.lessons_per_week.text().strip()

        if not new_lesson:
            QMessageBox.warning(self, "Uyarı", "Ders adı boş olamaz.")
            return

        if new_lesson in self.lesson_list:
            QMessageBox.warning(self, "Uyarı", "Bu ders zaten mevcut.")
            return

        try:
            lessons_per_week_int = int(lessons_per_week)
            if lessons_per_week_int < 1:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Uyarı", "Geçerli bir haftalık ders sayısı girin.")
            return

        self.lesson_list.append(new_lesson)
        self.ui.lesson_selector.addItem(new_lesson)
        self.ui.history_lesson_selector.addItem(new_lesson)
        self.ui.absenteeism_lesson_selector.addItem(new_lesson)
        self.ui.lesson_list_selector.addItem(new_lesson)
        self.ui.lesson_selector_for_student.addItem(new_lesson)

        self.lesson_details[new_lesson] = {
            'weeks': self.ui.week_count.value(),
            'lessons_per_week': lessons_per_week_int
        }

        os.makedirs(f'{new_lesson}/attendance_photos', exist_ok=True)
        os.makedirs(f'{new_lesson}/student_photos', exist_ok=True)

        self.save_lessons()
        QMessageBox.information(self, "Bilgi", "Ders başarıyla eklendi.")

    def remove_lesson(self):
        selected_lesson = self.ui.lesson_list_selector.currentText()
        if selected_lesson:
            self.lesson_list.remove(selected_lesson)
            self.ui.lesson_selector.removeItem(self.ui.lesson_selector.findText(selected_lesson))
            self.ui.history_lesson_selector.removeItem(self.ui.history_lesson_selector.findText(selected_lesson))
            self.ui.absenteeism_lesson_selector.removeItem(self.ui.absenteeism_lesson_selector.findText(selected_lesson))
            self.ui.lesson_list_selector.removeItem(self.ui.lesson_list_selector.findText(selected_lesson))
            self.ui.lesson_selector_for_student.removeItem(self.ui.lesson_selector_for_student.findText(selected_lesson))
            del self.lesson_details[selected_lesson]
            self.save_lessons()
            QMessageBox.information(self, "Bilgi", "Ders başarıyla kaldırıldı.")
        else:
            QMessageBox.warning(self, "Uyarı", "Kaldırmak için bir ders seçin.")

    def update_lesson_details(self):
        selected_lesson = self.ui.lesson_selector.currentText()
        if selected_lesson in self.lesson_details:
            weeks = self.lesson_details[selected_lesson].get('weeks', 14)
            lessons_per_week = self.lesson_details[selected_lesson].get('lessons_per_week', 1)

            try:
                lessons_per_week_int = int(lessons_per_week)
            except ValueError:
                QMessageBox.warning(self, "Uyarı", "Haftalık ders sayısı geçersiz. Varsayılan değer olan 1 kullanılıyor.")
                lessons_per_week_int = 1

            self.ui.week_selector.setMaximum(weeks)
            self.ui.lesson_number_selector.setMaximum(lessons_per_week_int)

    def load_known_faces(self):
        self.known_face_encodings = []
        self.known_face_names = []
        for lesson in self.lesson_list:
            student_photos_path = os.path.join(lesson, 'student_photos')
            if os.path.exists(student_photos_path):
                for filename in os.listdir(student_photos_path):
                    if filename.endswith('.jpg') or filename.endswith('.png'):
                        try:
                            image = face_recognition.load_image_file(os.path.join(student_photos_path, filename))
                            encodings = face_recognition.face_encodings(image)
                            if encodings:
                                encoding = encodings[0]
                                self.known_face_encodings.append(encoding)
                                self.known_face_names.append(filename.split('.')[0])
                        except Exception as e:
                            print(f"{filename} yüz verisi yüklenirken hata oluştu: {str(e)}")

    def load_attendance_data(self):
        for lesson in self.lesson_list:
            csv_file = f'{lesson}_yoklama.csv'
            if os.path.exists(csv_file):
                self.attendance_data[lesson] = pd.read_csv(csv_file)
            else:
                self.attendance_data[lesson] = pd.DataFrame(columns=['Tarih', 'Ders', 'Hafta', 'Ders Numarası', 'Öğrenci', 'Durum'])

    def load_lessons(self):
        if os.path.exists('lessons.txt'):
            lessons = []  # photo_lesson_selector için dersleri toplamak amacıyla liste
            with open('lessons.txt', 'r') as file:
                for line in file.readlines():
                    parts = line.strip().split(',')
                    if len(parts) == 3:
                        lesson, weeks, lessons_per_week = parts
                        self.lesson_list.append(lesson)
                        self.lesson_details[lesson] = {'weeks': int(weeks), 'lessons_per_week': int(lessons_per_week)}
                        
                        # Dersleri uygun UI bileşenlerine ekleyin
                        self.ui.lesson_selector.addItem(lesson)
                        self.ui.history_lesson_selector.addItem(lesson)
                        self.ui.absenteeism_lesson_selector.addItem(lesson)
                        self.ui.lesson_list_selector.addItem(lesson)
                        self.ui.lesson_selector_for_student.addItem(lesson)
                        
                        # photo_lesson_selector için dersleri listeye ekleyin
                        lessons.append(lesson)
            
            # Tüm dersleri topluca photo_lesson_selector'a ekleyin
            self.ui.photo_lesson_selector.clear()
            self.ui.photo_lesson_selector.addItems(lessons)
        else:
            print("lessons.txt dosyası bulunamadı.")

    def save_lessons(self):
        with open('lessons.txt', 'w') as file:
            for lesson, details in self.lesson_details.items():
                file.write(f"{lesson},{details['weeks']},{details['lessons_per_week']}\n")

    def save_students(self):
        with open('students.pkl', 'wb') as file:
            pickle.dump({
                'known_face_encodings': self.known_face_encodings,
                'known_face_names': self.known_face_names
            }, file)

    def load_students(self):
        if os.path.exists('students.pkl'):
            with open('students.pkl', 'rb') as file:
                data = pickle.load(file)
                self.known_face_encodings = data.get('known_face_encodings', [])
                self.known_face_names = data.get('known_face_names', [])
                # Öğrencileri güncelle
                self.update_student_list()
        else:
            print("students.pkl dosyası bulunamadı.")

    def display_photo(self):
        # Kullanıcının seçtiği ders, hafta ve ders numarasını al
        lesson = self.ui.photo_lesson_selector.currentText()
        week = self.ui.photo_week_selector.value()
        lesson_number = self.ui.photo_lesson_number_selector.value()

        # Fotoğrafların kaydedildiği klasörü ayarla
        photo_dir = os.path.join(lesson, "attendance_photos")

        # Dosya adını arama kriterine uygun olarak ayarla
        search_pattern = f"Hafta{week}_Ders{lesson_number}.jpg"
        matching_photos = [f for f in os.listdir(photo_dir) if search_pattern in f]

        if matching_photos:
            # İlk eşleşen fotoğrafı seç
            photo_path = os.path.join(photo_dir, matching_photos[0])
            pixmap = QPixmap(photo_path)
            self.ui.photo_display_label.setPixmap(pixmap.scaled(self.ui.photo_display_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            QMessageBox.warning(self, "Uyarı", f"{lesson} dersi, Hafta {week} ve Ders {lesson_number} için fotoğraf bulunamadı.")

    def closeEvent(self, event):
        self.save_lessons()  # Dersleri kaydet
        self.save_students()  # Öğrencileri kaydet
        if self.video_thread:
            self.video_thread.stop()  # VideoThread'ı durdur
        # Kamera serbest bırakma işlemi VideoThread tarafından yapılıyor
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Show splash screen first
    splash = SplashScreen()
    splash.show()

    sys.exit(app.exec())
