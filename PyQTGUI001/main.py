from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer
import cv2
import csv
import os
import re
from PIL import Image  # 추가

Form, Window = uic.loadUiType("res/mainWindow.ui")

class MainApp:
    def __init__(self):
        self.app = QApplication([])
        self.window = Window()
        self.form = Form()
        self.form.setupUi(self.window)

        # 웹캠 열기
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.critical(None, "오류", "웹캠을 열 수 없습니다.")
            return

        # 웹캠 프레임 표시 타이머
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        # 버튼 이벤트 연결
        self.form.btnPhoto.clicked.connect(self.capture_photo)
        self.form.btnSave.clicked.connect(self.save_data)
        self.form.btnDel.clicked.connect(self.clear_fields)  # btnDel 버튼 이벤트 연결

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.form.label_4.setPixmap(QPixmap.fromImage(q_image))

    def capture_photo(self):
        name = self.form.lineEdit_name.text().strip()
        if not name:
            QMessageBox.warning(None, "경고", "이름을 입력하세요!")
            return

        # 안전한 파일명 처리
        safe_name = re.sub(r'[\\/:*?"<>| ]+', '_', name)

        # 한글 포함된 경로도 허용
        photos_dir = os.path.join(os.getcwd(), "photos")
        os.makedirs(photos_dir, exist_ok=True)

        filename = os.path.join(photos_dir, f"{safe_name}.png")
        print("사진 저장 시도 경로:", filename)

        ret, frame = self.cap.read()
        if not ret or frame is None:
            QMessageBox.critical(None, "오류", "웹캠 프레임을 읽을 수 없습니다!")
            return

        try:
            # OpenCV → PIL 변환 후 저장
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb)
            pil_img.save(filename)  # 한글 경로에서도 OK

            self.form.lineEditPhoto.setText(filename)
            QMessageBox.information(None, "저장 완료", f"사진이 저장되었습니다:\n{filename}")
        except Exception as e:
            QMessageBox.critical(None, "오류", f"사진 저장 중 오류가 발생했습니다:\n{e}")

    def save_data(self):
        number = self.form.lineEdit_number.text()
        recommend = self.form.textEdit_recommend.toPlainText()
        name = self.form.lineEdit_name.text()
        photo = self.form.lineEditPhoto.text()

        try:
            with open("data.csv", "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Number", "Recommendation", "Name"])
                writer.writerow([number, recommend, name])
            QMessageBox.information(None, "저장 완료", "데이터가 성공적으로 저장되었습니다!")
        except Exception as e:
            QMessageBox.critical(None, "저장 실패", f"오류가 발생했습니다:\n{e}")

    def clear_fields(self):
        # lineEdit_name, lineEdit_number, textEdit_recommend 초기화
        self.form.lineEdit_name.clear()
        self.form.lineEdit_number.clear()
        self.form.textEdit_recommend.clear()

    def run(self):
        self.window.show()
        self.app.exec()
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = MainApp()
    app.run()
