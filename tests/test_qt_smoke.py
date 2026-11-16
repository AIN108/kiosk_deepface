"""offscreen Qt 스모크 테스트: ksnv.py(통합 실험판) 시작·DB 경로·음성 명령 경로, kiosk.py(UI 모드)."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "ksitscma-sef"
HARNESS = Path(__file__).with_name("ksnv_harness.py")
COPY_ITEMS = ["ui", "data", "img", "menu", "background", "QT_design.ui", "ksnv.py", "kiosk.py", "ks.py", "shopping_cart.py"]


@pytest.fixture(scope="session")
def app_copy(tmp_path_factory):
    """앱이 data/data.db에 쓸 수 있으므로 필요한 파일만 임시 폴더에 복사해 그곳에서 실행한다."""
    target = tmp_path_factory.mktemp("ksitscma-sef")
    for item in COPY_ITEMS:
        source = APP / item
        if source.is_dir():
            shutil.copytree(source, target / item)
        else:
            shutil.copy2(source, target / item)
    return target


def run_harness(app_copy, mode, timeout=120):
    env = dict(os.environ, QT_QPA_PLATFORM="offscreen")
    try:
        proc = subprocess.run([sys.executable, str(HARNESS), mode], cwd=app_copy, env=env,
                              capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        pytest.fail(f"{mode}: {timeout}초 안에 끝나지 않음 (UI 이벤트 루프가 멈췄을 수 있음)")
    lines = [line for line in proc.stdout.splitlines() if line.startswith("{")]
    assert lines, f"하네스 출력 없음 (code {proc.returncode})\n{proc.stdout}\n{proc.stderr}"
    return json.loads(lines[-1])


def test_ksnv_starts_with_repository_paths(app_copy):
    # ui/·data/ 소문자 경로로 UI 6종과 DB·CSV를 찾아야 대소문자를 구분하는 OS에서도 시작된다
    result = run_harness(app_copy, "startup")
    assert result["status"] == "ok", result
    assert result["errors"] == []
    assert result["total_price"] == 0 and result["total_cnt"] == 0


def test_ksnv_voice_command_reaches_cart(app_copy):
    result = run_harness(app_copy, "voice")
    assert result["status"] == "ok", result
    assert result["heard"][:2] == ["adjust", "listen"]  # 인식 루프가 실제로 마이크를 듣는다
    assert result["commands"] == ["아메리카노 주세요"]
    assert result["cart_items"] == 1


def test_kiosk_ui_mode_loads(app_copy):
    result = run_harness(app_copy, "kiosk")
    assert result["status"] == "ok", result
    assert result["pages"] >= 8  # go_to_page0~7에 해당하는 페이지


def test_ksnv_camera_threads_start_once_and_stop_on_close(app_copy):
    # 홈 버튼을 세 번 눌러도 카메라 0·1을 한 번씩만 열고, 창을 닫으면 둘 다 해제한다
    result = run_harness(app_copy, "camera")
    assert result["status"] == "ok", result
    assert result["errors"] == []
    assert result["open_before_close"] == [0, 1]
    assert result["resets"] == 3  # 홈 버튼 한 번에 판정 초기화 한 번 (시그널 이중 연결 없음)
    assert result["opened"] == {"0": 1, "1": 1}
    assert result["open_after_close"] == []
    # cv2.imshow(HighGUI)는 메인(UI) 스레드에서만 호출한다
    assert result["imshow"] > 0 and result["imshow_off_main"] == 0


def test_ks_detection_does_not_block_ui(app_copy):
    # 메뉴 버튼을 누르면 판별(카메라 루프)이 백그라운드에서 돌고 UI 이벤트 루프는 계속 돈다
    result = run_harness(app_copy, "ks", timeout=60)
    assert result["status"] == "ok", result
    assert result["errors"] == []
    assert result["ui_ticks"] >= 20  # 100ms 타이머가 약 3초 동안 계속 실행됨
    assert result["opened"] == {"0": 1}  # 판별 중 다시 눌러도 카메라를 또 열지 않음
    assert result["open_after_close"] == []
