"""ksnv.py / kiosk.py를 offscreen Qt에서 실행하는 테스트 도우미 (pytest가 하위 프로세스로 실행).

카메라·얼굴·음성 라이브러리(cv2, dlib, deepface, pyttsx3, speech_recognition)는 하드웨어가 필요하므로
스텁으로 대체한다. 결과는 마지막 줄에 JSON으로 출력한다.
사용: QT_QPA_PLATFORM=offscreen python ksnv_harness.py <startup|voice|kiosk|camera|ks>   (cwd = 앱 폴더 복사본)
camera: ksnv.py 카메라 분석 스레드(가짜 카메라 0·1)를 홈 버튼 반복·창 닫기와 함께 관찰한다.
ks: ks.py(프로토타입) 메뉴 버튼을 눌렀을 때 UI 이벤트 루프가 계속 도는지 관찰한다.
"""
import json
import os
import runpy
import sys
import threading
import time
import types

mode = sys.argv[1]
sys.path.insert(0, os.getcwd())  # 앱 폴더의 shopping_cart.py를 찾도록
result = {"mode": mode, "errors": []}


class _Any:
    def __init__(self, *a, **k):
        pass

    def __call__(self, *a, **k):
        return _Any()

    def __getattr__(self, name):
        if name == "isOpened":
            return lambda: False
        if name == "read":
            return lambda: (False, None)
        return _Any()

    def __iter__(self):
        return iter(())

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


for name in ("cv2", "dlib", "pyttsx3", "deepface", "speech_recognition"):
    module = types.ModuleType(name)
    module.__getattr__ = lambda attr: _Any()
    sys.modules[name] = module
sys.modules["deepface"].DeepFace = _Any()

camera = {"opened": [], "released": [], "imshow_off_main": 0, "imshow": 0}
if mode in ("camera", "ks"):
    class FakeCapture:
        """항상 열리고 30fps로 프레임을 주는 가짜 카메라"""

        def __init__(self, index, *args):
            self.index, self.open = index, True
            camera["opened"].append(index)

        def isOpened(self):
            return self.open

        def get(self, prop):
            return 640.0  # 해상도 등 속성 조회

        def read(self):
            time.sleep(0.03)
            return (self.open, _Any() if self.open else None)

        def release(self):
            if self.open:
                camera["released"].append(self.index)
            self.open = False

    def fake_imshow(name, frame):
        camera["imshow"] += 1
        if threading.current_thread() is not threading.main_thread():
            camera["imshow_off_main"] += 1

    cv2 = sys.modules["cv2"]
    cv2.VideoCapture = FakeCapture
    cv2.imshow = fake_imshow
    cv2.waitKey = lambda delay=0: -1
    cv2.destroyAllWindows = lambda: None
    sys.modules["dlib"].get_frontal_face_detector = lambda: (lambda image: [])  # 얼굴 없음

heard = []
if mode in ("voice", "startup", "camera"):
    sr = types.ModuleType("speech_recognition")

    class Recognizer:
        def adjust_for_ambient_noise(self, source):
            heard.append("adjust")

        def listen(self, source):
            if mode in ("startup", "camera"):
                raise SystemExit  # 시작 스모크 테스트에서는 음성 스레드를 바로 끝낸다
            time.sleep(1)  # 실제 마이크처럼 발화를 기다리는 동안 메인 스레드가 메뉴 데이터를 불러온다
            heard.append("listen")
            return "audio"

        def recognize_google(self, audio, language=None):
            if heard.count("listen") > 1:
                raise SystemExit  # 두 번째 반복에서 인식 스레드 종료
            return "아메리카노 주세요"

    sr.Recognizer, sr.Microphone = Recognizer, _Any
    sr.UnknownValueError = type("UnknownValueError", (Exception,), {})
    sr.RequestError = type("RequestError", (Exception,), {})
    sys.modules["speech_recognition"] = sr

threading.excepthook = lambda args: None if args.exc_type is SystemExit else result["errors"].append(
    f"thread {args.exc_type.__name__}: {args.exc_value}")  # SystemExit는 스텁이 스레드를 끝내는 신호
sys.excepthook = lambda t, v, tb: result["errors"].append(f"slot {t.__name__}: {v}")

from PyQt5.QtCore import QTimer  # noqa: E402
from PyQt5.QtWidgets import QApplication  # noqa: E402

app = QApplication(sys.argv)
quit_timer = QTimer()
quit_timer.setSingleShot(True)
quit_timer.timeout.connect(app.quit)
quit_timer.start(3000)
ui_ticks = []
tick_timer = QTimer()
tick_timer.timeout.connect(lambda: ui_ticks.append(time.monotonic()))  # UI 이벤트 루프가 도는지 확인
tick_timer.start(100)
real_exit = sys.exit
sys.exit = lambda code=0: None
try:
    script = {"kiosk": "kiosk.py", "ks": "ks.py"}.get(mode, "ksnv.py")
    ns = runpy.run_path(script, run_name="harness")
    if mode == "voice":
        calls = []
        original = ns["WindowClass"].processCommand
        ns["WindowClass"].processCommand = lambda self, cmd: (calls.append(cmd), original(self, cmd))
    window = ns["MainScreen" if mode == "ks" else "WindowClass"]()
    window.show()

    def open_cameras():
        """아직 release되지 않은 카메라 번호 목록 (번호별로 열린 횟수 - 해제 횟수)"""
        return sorted(i for i in set(camera["opened"])
                      for _ in range(camera["opened"].count(i) - camera["released"].count(i)))

    if mode in ("camera", "ks"):
        quit_timer.start(3000)  # 창 생성에 걸린 시간과 무관하게 아래 일정이 모두 끝난 뒤 종료
    if mode == "camera":
        for delay in (500, 800, 1100):  # 홈 버튼을 세 번 누른다 (판정 초기화)
            QTimer.singleShot(delay, window.home_button.click)
        QTimer.singleShot(2000, lambda: result.update(open_before_close=sorted(open_cameras())))
        QTimer.singleShot(2200, window.close)
    if mode == "ks":
        QTimer.singleShot(300, window.dineInButton.click)
        QTimer.singleShot(900, window.takeAwayButton.click)  # 판별 중 다시 눌러도 카메라를 또 열지 않아야 한다
        QTimer.singleShot(2200, window.close)
    app.exec_()
    if mode in ("camera", "ks"):
        time.sleep(0.5)  # 창을 닫은 뒤 스레드가 장치를 놓을 시간
        result["opened"] = {str(i): camera["opened"].count(i) for i in sorted(set(camera["opened"]))}
        result["open_after_close"] = sorted(open_cameras())
        result["imshow_off_main"] = camera["imshow_off_main"]
        result["imshow"] = camera["imshow"]
        result["ui_ticks"] = len(ui_ticks)
    result["status"] = "ok"
    if mode == "startup":
        result["total_price"] = int(window.get_total_price() or 0)
        result["total_cnt"] = int(window.get_total_cnt() or 0)
    if mode == "voice":
        result["heard"] = heard
        result["commands"] = calls
        result["cart_items"] = window.drinks_cart_list_widget.count()
    if mode == "kiosk":
        result["pages"] = window.stackedWidget.count()
except Exception as exc:  # noqa: BLE001
    result["status"] = f"{type(exc).__name__}: {exc}"
print(json.dumps(result, ensure_ascii=False))
real_exit(0)
