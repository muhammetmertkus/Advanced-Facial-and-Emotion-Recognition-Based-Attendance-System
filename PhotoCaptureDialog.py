import cv2
import os
from PySide6.QtCore import Qt, QTimer, QDir
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtGui import QPixmap, QImage
import face_recognition

class PhotoCaptureDialog(QDialog):
    def __init__(self, camera, lesson_name, student_name, student_id, base_directory="bitirme projesi", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fotoğraf Çek")
        self.setFixedSize(800, 600)
        self.camera = camera
        self.photo_count = 0
        self.photos = []

        # Öğrenci için kayıt dizini
        self.save_directory = os.path.join(base_directory, lesson_name, "student_photos", f"{student_id}_{student_name}")

        # Layout ve widget ayarları
        layout = QVBoxLayout()
        
        # Canlı kamera görüntüsü alanı
        self.main_photo_label = QLabel("Kamera Açılıyor...")
        self.main_photo_label.setFixedSize(640, 480)
        self.main_photo_label.setStyleSheet("border: 1px solid #555555;")
        self.main_photo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.main_photo_label)

        # Thumbnail (küçük resim) alanı
        self.thumbnail_layout = QHBoxLayout()
        layout.addLayout(self.thumbnail_layout)

        # Fotoğraf çekme ve kaydetme düğmeleri
        button_layout = QHBoxLayout()
        self.capture_button = QPushButton("Fotoğraf Çek")
        self.capture_button.clicked.connect(self.capture_photo)
        button_layout.addWidget(self.capture_button)

        self.save_button = QPushButton("Kaydet")
        self.save_button.clicked.connect(self.save_photos)
        self.save_button.setEnabled(False)  # Başlangıçta devre dışı
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Canlı kamera görüntüsü için QTimer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30ms’de bir kare güncellenir

    def update_frame(self):
        # Kameradan görüntüyü al ve göster
        ret, frame = self.camera.read()
        if ret:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.main_photo_label.setPixmap(QPixmap.fromImage(qt_image).scaled(640, 480, Qt.KeepAspectRatio))

    def capture_photo(self):
        # Fotoğraf çekme ve küçük resim olarak gösterme
        ret, frame = self.camera.read()
        if ret:
            self.photos.append(frame)
            self.photo_count += 1

            # Ana ekranda çekilen fotoğrafı göster
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.main_photo_label.setPixmap(QPixmap.fromImage(qt_image).scaled(640, 480, Qt.KeepAspectRatio))

            # Küçük resim olarak ekleyin
            thumbnail_label = QLabel()
            thumbnail_label.setPixmap(QPixmap.fromImage(qt_image).scaled(100, 75, Qt.KeepAspectRatio))
            self.thumbnail_layout.addWidget(thumbnail_label)

            # Kaydet butonunu etkinleştir
            self.save_button.setEnabled(True)

            # Üç fotoğraf çekildiğinde "Fotoğraf Çek" düğmesini devre dışı bırakın
            if self.photo_count >= 3:
                self.capture_button.setEnabled(False)

    def save_photos(self):
        # Öğrenci klasörünü oluşturma (mevcut değilse)
        os.makedirs(self.save_directory, exist_ok=True)

        # Fotoğrafları belirtilen klasöre kaydetme
        for idx, photo in enumerate(self.photos):
            file_path = os.path.join(self.save_directory, f"photo_{idx + 1}.jpg")
            cv2.imwrite(file_path, photo)
            print(f"{file_path} kaydedildi.")

        QMessageBox.information(self, "Başarılı", f"Fotoğraflar {self.save_directory} klasörüne kaydedildi.")
        self.accept()  # Diyaloğu kapat

    def closeEvent(self, event):
        # Kamera bağlantısını kapatma
        self.timer.stop()
        super().closeEvent(event)
