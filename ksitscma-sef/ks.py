import sys
import threading
import cv2
import dlib
from deepface import DeepFace
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, \
    QGridLayout, QMessageBox
from PyQt5.QtCore import Qt
import speech_recognition as sr
import pyttsx3

# 전역 변수 선언
order = {}
orderLabel = None


# 디지털 문맹자 인식 함수
def detect_digital_illiteracy(camera_id=0):
    # 카메라 설정
    cap = cv2.VideoCapture(camera_id)
    detector = dlib.get_frontal_face_detector()
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        faces = detector(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        for face in faces:
            try:
                # DeepFace 분석
                results = DeepFace.analyze(frame, actions=['age', 'emotion'], enforce_detection=False)
                if 'surprise' in results['dominant_emotion'] or 'angry' in results['dominant_emotion']:
                    # 디지털 문맹자로 판단된 경우
                    cap.release()
                    return True
            except Exception as e:
                continue
    cap.release()
    return False


# 음성 인식 및 처리
def start_voice_recognition():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    try:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        command = recognizer.recognize_google(audio).lower()
        process_voice_command(command)
    except sr.UnknownValueError:
        # 음성 인식 실패 처리
        print("음성 인식을 실패했습니다.")


def process_voice_command(command):
    global order
    # 예: "아메리카노 추가해줘" 명령어 처리 로직
    # 실제 명령어 처리 로직 구현 필요


# 메뉴 아이템 클래스
class MenuItem(QWidget):
    def __init__(self, name, price):
        super().__init__()
        self.name = name
        self.price = price
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.label = QLabel(f'{self.name}\n{self.price}원')
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.addButton = QPushButton('+')
        self.addButton.clicked.connect(self.addItem)
        layout.addWidget(self.addButton)

        self.setLayout(layout)

    def addItem(self):
        global order
        if self.name in order:
            order[self.name]['quantity'] += 1
        else:
            order[self.name] = {'quantity': 1, 'price': self.price}
        updateOrderDisplay()


# 주문 내역 업데이트
def updateOrderDisplay():
    global orderLabel
    text = ''
    total = 0
    for item, details in order.items():
        text += f'{item} x {details["quantity"]}\n'
        total += details['quantity'] * details['price']
    text += f'총액: {total}원'
    orderLabel.setText(text)


# 메뉴판 화면 클래스
class MenuScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('메뉴판')
        self.setGeometry(100, 100, 800, 600)

        self.layout = QGridLayout()
        self.widgets = {
            'americano': MenuItem('아메리카노', 4000),
            'cafelatte': MenuItem('카페라떼', 4500),
            # 추가 메뉴 아이템
        }
        for i, widget in enumerate(self.widgets.values()):
            self.layout.addWidget(widget, i // 2, i % 2)

        global orderLabel
        orderLabel = QLabel('주문 내역이 여기에 표시됩니다.')
        self.layout.addWidget(orderLabel, len(self.widgets) // 2 + 1, 0, 1, 2)

        centralWidget = QWidget()
        centralWidget.setLayout(self.layout)
        self.setCentralWidget(centralWidget)


# 메인 화면 클래스
class MainScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('키오스크 메인 화면')
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.dineInButton = QPushButton('먹고 가기')
        self.dineInButton.clicked.connect(self.showMenu)
        layout.addWidget(self.dineInButton)

        self.takeAwayButton = QPushButton('포장하기')
        self.takeAwayButton.clicked.connect(self.showMenu)
        layout.addWidget(self.takeAwayButton)

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

    def showMenu(self):
        self.menuScreen = MenuScreen()
        self.menuScreen.show()
        # 디지털 문맹자 판별 후 음성 인식 시작
        if detect_digital_illiteracy():
            start_voice_recognition()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainScreen()
    main.show()
    sys.exit(app.exec_())
