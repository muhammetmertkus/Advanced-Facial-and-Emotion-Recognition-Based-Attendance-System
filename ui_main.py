from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QTextEdit, QLineEdit, QFileDialog, QTabWidget, QMessageBox,
    QFormLayout, QSpinBox, QTableWidget, QTableWidgetItem
)
from PySide6.QtGui import QIcon, QFont, QPixmap
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
import cv2
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QMessageBox
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QTimer
import cv2
import os


class Ui_AttendanceSystem(object):
    def setup_ui(self, AttendanceSystem):
        # Ana pencere özelliklerini ayarlayın
        AttendanceSystem.setObjectName("AttendanceSystem")
        AttendanceSystem.setWindowTitle("Gelişmiş Yüz ve Duygu Tanıma Tabanlı Yoklama Sistemi")
        AttendanceSystem.resize(1200, 800)
        AttendanceSystem.setWindowIcon(QIcon("icons/app_icon.png"))

        # Ana düzen
        self.main_layout = QVBoxLayout(AttendanceSystem)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Sekme widget'ı
        self.tabs = QTabWidget(AttendanceSystem)
        self.main_layout.addWidget(self.tabs)

        # Sekmeleri oluşturun
        self.create_attendance_tab()
        self.create_student_management_tab()
        self.create_attendance_history_tab()
        self.create_absenteeism_tab()
        self.create_lesson_management_tab()
        self.create_photo_history_tab()  # Yeni sekme eklendi

        # Stil uygulama
        self.apply_styles(AttendanceSystem)

    def apply_styles(self, parent):
        # Tema ve stil ayarları
        stylesheet = """
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QTabWidget::pane {
                border: 1px solid #444444;
                background-color: #333333;
            }
            QTabBar::tab {
                background: #444444;
                padding: 10px;
                margin: 2px;
                border-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #555555;
            }
            QPushButton {
                background-color: #555555;
                border: none;
                padding: 10px 20px;
                color: #ffffff;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QLabel {
                color: #ffffff;
                font-weight: bold;
            }
            QLineEdit, QComboBox, QTextEdit, QSpinBox {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                color: #ffffff;
                border-radius: 4px;
                padding: 5px;
            }
            QTableWidget {
                background-color: #3c3c3c;
                color: #ffffff;
                gridline-color: #555555;
                border: 1px solid #555555;
            }
            QTableWidget::item:selected {
                background-color: #555555;
            }
        """
        parent.setStyleSheet(stylesheet)

    def create_attendance_tab(self):
        # Yoklama sekmesi
        self.attendance_tab = QWidget()
        attendance_layout = QVBoxLayout()

        # Kamera görüntüsü için alan
        self.image_label = QLabel(self.attendance_tab)
        self.image_label.setMinimumSize(640, 480)
        self.image_label.setStyleSheet("border: 1px solid #555555;")
        self.image_label.setAlignment(Qt.AlignCenter)
        attendance_layout.addWidget(self.image_label, alignment=Qt.AlignCenter)

        # Ders ve hafta seçicileri
        controls_layout = QHBoxLayout()
        self.lesson_selector = QComboBox(self.attendance_tab)
        self.lesson_selector.setMinimumWidth(150)
        controls_layout.addWidget(self.lesson_selector)

        self.week_selector = QSpinBox(self.attendance_tab)
        self.week_selector.setMinimum(1)
        self.week_selector.setPrefix("Hafta: ")
        controls_layout.addWidget(self.week_selector)

        self.lesson_number_selector = QSpinBox(self.attendance_tab)
        self.lesson_number_selector.setMinimum(1)
        self.lesson_number_selector.setPrefix("Ders: ")
        controls_layout.addWidget(self.lesson_number_selector)

        # Yoklama al düğmesi
        self.capture_btn = QPushButton("Yoklama Al", self.attendance_tab)
        self.capture_btn.setIcon(QIcon("icons/camera.png"))
        controls_layout.addWidget(self.capture_btn)

        # Canlı Kamera Yoklama Butonu
        self.live_attendance_btn = QPushButton("Canlı Kamera Yoklama", self.attendance_tab)
        self.live_attendance_btn.setIcon(QIcon("icons/live_camera.png"))
        controls_layout.addWidget(self.live_attendance_btn)

        attendance_layout.addLayout(controls_layout)

        # Manuel öğrenci ekleme
        manual_layout = QHBoxLayout()
        self.manual_student_id = QLineEdit(self.attendance_tab)
        self.manual_student_id.setPlaceholderText("Okul Numarası Gir")
        manual_layout.addWidget(self.manual_student_id)

        self.add_manual_btn = QPushButton("Manuel Ekle", self.attendance_tab)
        manual_layout.addWidget(self.add_manual_btn)
        attendance_layout.addLayout(manual_layout)

        # Bilgi metin alanı
        self.info_text = QTextEdit(self.attendance_tab)
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("background-color: #3c3c3c;")
        attendance_layout.addWidget(self.info_text)

        # Sekmeye ekleme
        self.attendance_tab.setLayout(attendance_layout)
        self.tabs.addTab(self.attendance_tab, "Yoklama")

    def create_student_management_tab(self):
        # Öğrenci yönetimi sekmesi
        self.student_management_tab = QWidget()
        layout = QVBoxLayout()

        # Öğrenci bilgileri formu
        form_layout = QFormLayout()
        self.student_name = QLineEdit(self.student_management_tab)
        form_layout.addRow("Öğrenci Adı Soyadı:", self.student_name)

        self.student_id = QLineEdit(self.student_management_tab)
        form_layout.addRow("Okul Numarası:", self.student_id)

        self.lesson_selector_for_student = QComboBox(self.student_management_tab)
        form_layout.addRow("Ders Seç:", self.lesson_selector_for_student)

        # Fotoğraf seçimi ve çekimi
        self.photo_path = QLineEdit(self.student_management_tab)
        self.photo_path.setReadOnly(True)
        self.photo_select_btn = QPushButton("Fotoğraf Seç", self.student_management_tab)
        self.photo_capture_btn = QPushButton("Fotoğraf Çek", self.student_management_tab)

        photo_layout = QHBoxLayout()
        photo_layout.addWidget(self.photo_path)
        photo_layout.addWidget(self.photo_select_btn)
        photo_layout.addWidget(self.photo_capture_btn)
        form_layout.addRow("Öğrenci Fotoğrafı:", photo_layout)
        
        layout.addLayout(form_layout)

        # Öğrenci ekle düğmesi ve mevcut öğrenci listesi
        self.add_student_btn = QPushButton("Öğrenci Ekle", self.student_management_tab)
        layout.addWidget(self.add_student_btn)

        self.student_list_label = QLabel("Mevcut Öğrenciler:")
        layout.addWidget(self.student_list_label)

        self.student_list = QTextEdit(self.student_management_tab)
        self.student_list.setReadOnly(True)
        layout.addWidget(self.student_list)

        self.student_management_tab.setLayout(layout)
        self.tabs.addTab(self.student_management_tab, "Öğrenci Yönetimi")

    def create_attendance_history_tab(self):
        # Yoklama geçmişi sekmesi
        self.attendance_history_tab = QWidget()
        layout = QVBoxLayout()

        # Ders seçici ve tablo görüntüleme
        self.history_lesson_selector = QComboBox(self.attendance_history_tab)
        layout.addWidget(self.history_lesson_selector)

        self.attendance_table = QTableWidget(self.attendance_history_tab)
        layout.addWidget(self.attendance_table)

        self.show_history_btn = QPushButton("Yoklama Geçmişini Göster", self.attendance_history_tab)
        layout.addWidget(self.show_history_btn)

        self.attendance_history_tab.setLayout(layout)
        self.tabs.addTab(self.attendance_history_tab, "Yoklama Geçmişi")

    def create_absenteeism_tab(self):
        # Devamsızlık raporu sekmesi
        self.absenteeism_tab = QWidget()
        layout = QVBoxLayout()

        # Ders seçici ve devamsızlık sınırı
        form_layout = QFormLayout()
        self.absenteeism_lesson_selector = QComboBox(self.absenteeism_tab)
        form_layout.addRow("Ders Seç:", self.absenteeism_lesson_selector)

        self.absence_limit = QSpinBox(self.absenteeism_tab)
        self.absence_limit.setMinimum(1)
        self.absence_limit.setValue(10)
        form_layout.addRow("Devamsızlık Sınırı (Saat):", self.absence_limit)

        # Devamsızlık hesapla düğmesi
        self.calculate_btn = QPushButton("Devamsızlık Hesapla", self.absenteeism_tab)
        form_layout.addRow(self.calculate_btn)

        layout.addLayout(form_layout)

        # Devamsızlık metin alanı
        self.absenteeism_text = QTextEdit(self.absenteeism_tab)
        self.absenteeism_text.setReadOnly(True)
        layout.addWidget(self.absenteeism_text)

        self.absenteeism_tab.setLayout(layout)
        self.tabs.addTab(self.absenteeism_tab, "Devamsızlık Raporu")

    def create_lesson_management_tab(self):
        # Ders yönetimi sekmesi
        self.lesson_management_tab = QWidget()
        layout = QVBoxLayout()

        # Yeni ders ekleme formu
        form_layout = QFormLayout()
        self.new_lesson_input = QLineEdit(self.lesson_management_tab)
        form_layout.addRow("Yeni Ders Adı:", self.new_lesson_input)

        self.week_count = QSpinBox(self.lesson_management_tab)
        self.week_count.setMinimum(1)
        self.week_count.setValue(14)
        form_layout.addRow("Hafta Sayısı:", self.week_count)

        self.lessons_per_week = QLineEdit(self.lesson_management_tab)
        form_layout.addRow("Haftalık Ders Sayısı:", self.lessons_per_week)

        self.add_lesson_btn = QPushButton("Ders Ekle", self.lesson_management_tab)
        form_layout.addWidget(self.add_lesson_btn)

        # Ders kaldırma seçici
        self.lesson_list_selector = QComboBox(self.lesson_management_tab)
        form_layout.addRow("Ders Seç:", self.lesson_list_selector)

        self.remove_lesson_btn = QPushButton("Seçili Dersi Kaldır", self.lesson_management_tab)
        form_layout.addWidget(self.remove_lesson_btn)

        layout.addLayout(form_layout)
        self.lesson_management_tab.setLayout(layout)
        self.tabs.addTab(self.lesson_management_tab, "Ders Yönetimi")

    def create_photo_history_tab(self):
        # Fotoğraf geçmişi sekmesi
        self.photo_history_tab = QWidget()
        layout = QVBoxLayout()

        # Ders, hafta ve ders numarası seçicileri
        form_layout = QFormLayout()
        self.photo_lesson_selector = QComboBox(self.photo_history_tab)
        form_layout.addRow("Ders Seç:", self.photo_lesson_selector)

        self.photo_week_selector = QSpinBox(self.photo_history_tab)
        self.photo_week_selector.setMinimum(1)
        form_layout.addRow("Hafta:", self.photo_week_selector)

        self.photo_lesson_number_selector = QSpinBox(self.photo_history_tab)
        self.photo_lesson_number_selector.setMinimum(1)
        form_layout.addRow("Ders Numarası:", self.photo_lesson_number_selector)

        # Fotoğraf gösterme düğmesi
        self.show_photo_btn = QPushButton("Fotoğrafı Görüntüle", self.photo_history_tab)
        form_layout.addRow(self.show_photo_btn)

        layout.addLayout(form_layout)

        # Fotoğraf görüntüleme alanı
        self.photo_display_label = QLabel(self.photo_history_tab)
        self.photo_display_label.setMinimumSize(640, 480)
        self.photo_display_label.setStyleSheet("border: 1px solid #555555;")
        self.photo_display_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.photo_display_label)

        self.photo_history_tab.setLayout(layout)
        self.tabs.addTab(self.photo_history_tab, "Fotoğraf Geçmişi")
