📄 Project Description
Advanced Facial and Emotion Recognition-Based Attendance System (SARON) is a sophisticated attendance management tool designed for educational institutions. Leveraging real-time facial recognition and emotion analysis, SARON automates the attendance tracking process, ensuring accurate and efficient monitoring of student presence and emotional states during classes. This system enhances traditional attendance methods by incorporating advanced technologies to provide insightful analytics and streamlined operations.

✨ Features
Real-Time Facial Recognition: Automatically identifies students using facial recognition technology.
Emotion Analysis: Utilizes DeepFace to analyze students' emotional states.
User-Friendly Interface: Developed with PySide6 for an intuitive and aesthetic GUI.
Student and Course Management: Add, remove, and manage students and courses seamlessly.
Attendance History and Reporting: View historical attendance data and generate absenteeism reports.
Photo Capture and Storage: Capture and store student photos efficiently.
Secure Login System: Safe authentication with "Remember Me" functionality.
Data Backup and Recovery: Save and load data using CSV and pickle files.
Multi-Course Support: Manage multiple courses simultaneously.
Live Attendance Mode: Enable real-time attendance tracking with continuous monitoring.
Manual Attendance Entry: Option to manually add attendance records.
Lesson Management: Add and remove lessons, configure lesson details such as weeks and sessions per week.
Attendance Absenteeism Calculation: Calculate and report students' absenteeism based on predefined limits.

🛠 Installation
📋 Requirements
Python 3.7+
Required Python Libraries:
PySide6
opencv-python
face_recognition
deepface
numpy
pandas

git clone https://github.com/your_username/advanced-facial-emotion-recognition-attendance-system.git
cd advanced-facial-emotion-recognition-attendance-system

requirements.txt
PySide6
opencv-python
face_recognition
deepface
numpy
pandas

pip install -r requirements.txt

python main.py

Splash Screen

Upon launching, a splash screen will display the application logo and a progress bar indicating the loading status.

Login Screen

Username: Enter your username (default: admin).
Password: Enter your password (default: admin123).
Remember Me: Check this box to save your credentials for future logins.
Forgot Password: Click to receive instructions on password recovery.
Main Attendance System

Tabs: Navigate through different functionalities using the tabs:

Yoklama (Attendance): Capture attendance using the webcam.
Öğrenci Yönetimi (Student Management): Manage student records.
Yoklama Geçmişi (Attendance History): View historical attendance data.
Devamsızlık Raporu (Absenteeism Report): Generate absenteeism reports.
Ders Yönetimi (Lesson Management): Manage lesson details.
Fotoğraf Geçmişi (Photo History): View captured attendance photos.
Live Attendance: Enable live attendance tracking for real-time monitoring.

Manual Entry: Add attendance records manually if needed.

Photo Capture: Capture and store student photos during attendance.

📂 Managing Students and Lessons
Add Student: Enter student details and capture or select a photo.
Remove Student: Select a student from the list and remove their record.
Add Lesson: Define new lessons with details like weeks and sessions per week.
Remove Lesson: Select and remove existing lessons.
📊 Viewing Reports
Attendance History: Select a lesson and view detailed attendance records.
Absenteeism Report: Define absence limits and generate reports on students exceeding those limits.
🤝 Contributing
Contributions are welcome! To contribute to SARON, please follow these steps:




