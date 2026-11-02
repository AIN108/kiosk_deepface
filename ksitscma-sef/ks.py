import sys
import threading
import time
import cv2
import dlib
from deepface import DeepFace
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, \
    QGridLayout, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import speech_recognition as sr
import pyttsx3

# 전역 변수 선언
order = {}
orderLabel = None

DETECTION_TIMEOUT_SEC = 30  # 판별이 끝나지 않을 때 카메라를 붙잡고 있는 최대 시간


# 디지털 문맹자 인식 함수
def detect_digital_illiteracy(camera_id=0, timeout=DETECTION_TIMEOUT_SEC, should_stop=lambda: False):
    """카메라로 디지털 문맹자 여부를 판별한다. 시간 초과·중단 요청·카메라 오류 시 False.

    시간이 오래 걸리므로 UI 스레드가 아닌 DetectionWorker(QThread)에서 호출해야 한다.
    """
    # 카메라 설정
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print(f"카메라 {camera_id}를 열 수 없습니다.")
        return False
    detector = dlib.get_frontal_face_detector()
    deadline = time.monotonic() + timeout
    try:
        while time.monotonic() < deadline and not should_stop():
            ret, frame = cap.read()
            if not ret:
                break
            faces = detector(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
            if not faces:
                continue
            try:
                # DeepFace 분석 (프레임 전체 기준, 얼굴이 있을 때 프레임당 1회)
                results = DeepFace.analyze(frame, actions=['age', 'emotion'], enforce_detection=False)
            except Exception as e:
                print(f"얼굴 분석 실패: {e}")
                continue
            # 최신 deepface는 얼굴별 결과 리스트를 반환한다.
            if isinstance(results, list):
                results = results[0] if results else {}
            if results.get('dominant_emotion') in ('surprise', 'angry'):
                # 디지털 문맹자로 판단된 경우
                return True
    finally:
        cap.release()
    return False


class DetectionWorker(QThread):
    """디지털 문맹자 판별을 백그라운드에서 실행하고 결과를 시그널로 UI 스레드에 전달"""
    detected = pyqtSignal(bool)

    def __init__(self, camera_id=0, parent=None):
        super().__init__(parent)
        self.camera_id = camera_id

    def run(self):
        self.detected.emit(detect_digital_illiteracy(self.camera_id, should_stop=self.isInterruptionRequested))


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
    except (sr.RequestError, OSError) as e:
        # 네트워크 오류·마이크 없음 (백그라운드 스레드에서 실행되므로 예외를 기록만 함)
        print(f"음성 인식을 사용할 수 없습니다: {e}")


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
        self.detectionWorker = None
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
        # 디지털 문맹자 판별 후 음성 인식 시작 (UI가 멈추지 않도록 백그라운드에서 실행)
        if self.detectionWorker is not None and self.detectionWorker.isRunning():
            return  # 이미 판별 중이면 카메라를 다시 열지 않음
        self.detectionWorker = DetectionWorker(parent=self)
        self.detectionWorker.detected.connect(self.onDetectionFinished)
        self.detectionWorker.start()

    def onDetectionFinished(self, detected):
        if detected:
            # 음성 인식도 마이크 입력을 기다리며 블록되므로 별도 스레드에서 실행
            threading.Thread(target=start_voice_recognition, daemon=True).start()

    def closeEvent(self, event):
        if self.detectionWorker is not None and self.detectionWorker.isRunning():
            self.detectionWorker.requestInterruption()
            self.detectionWorker.wait(3000)
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainScreen()
    main.show()
    sys.exit(app.exec_())
