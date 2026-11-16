"""ksnv.py / kiosk.py를 offscreen Qt에서 실행하는 테스트 도우미 (pytest가 하위 프로세스로 실행).

카메라·얼굴·음성 라이브러리(cv2, dlib, deepface, pyttsx3, speech_recognition)는 하드웨어가 필요하므로
스텁으로 대체한다. 결과는 마지막 줄에 JSON으로 출력한다.
사용: QT_QPA_PLATFORM=offscreen python ksnv_harness.py <startup|voice|kiosk>   (cwd = 앱 폴더 복사본)
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

heard = []
if mode in ("voice", "startup"):
    sr = types.ModuleType("speech_recognition")

    class Recognizer:
        def adjust_for_ambient_noise(self, source):
            heard.append("adjust")

        def listen(self, source):
            if mode == "startup":
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
QTimer.singleShot(3000, app.quit)
real_exit = sys.exit
sys.exit = lambda code=0: None
try:
    ns = runpy.run_path("kiosk.py" if mode == "kiosk" else "ksnv.py", run_name="harness")
    if mode == "voice":
        calls = []
        original = ns["WindowClass"].processCommand
        ns["WindowClass"].processCommand = lambda self, cmd: (calls.append(cmd), original(self, cmd))
    window = ns["WindowClass"]()
    window.show()
    app.exec_()
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
