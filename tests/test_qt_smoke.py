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
COPY_ITEMS = ["ui", "data", "img", "menu", "background", "QT_design.ui", "ksnv.py", "kiosk.py", "shopping_cart.py"]


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


def run_harness(app_copy, mode):
    env = dict(os.environ, QT_QPA_PLATFORM="offscreen")
    proc = subprocess.run([sys.executable, str(HARNESS), mode], cwd=app_copy, env=env,
                          capture_output=True, text=True, timeout=120)
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
