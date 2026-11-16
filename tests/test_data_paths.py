"""앱 코드의 상대 경로('./data/...', './ui/...')가 실제 폴더 이름과 대소문자까지 일치하는지 검사한다.

Windows·macOS 기본 파일시스템은 대소문자를 구분하지 않아 './DATA/'도 열리지만, Linux에서는 실패한다.
"""
import ast
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "ksitscma-sef"


def exists_case_sensitive(base, relative):
    current = base
    for part in Path(relative).parts:
        if part == ".":
            continue
        if not current.is_dir() or part not in os.listdir(current):
            return False
        current = current / part
    return True


def relative_path_literals(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    in_fstring = {id(node) for joined in ast.walk(tree) if isinstance(joined, ast.JoinedStr)
                  for node in ast.walk(joined)}
    return sorted({node.value for node in ast.walk(tree)
                   if isinstance(node, ast.Constant) and isinstance(node.value, str)
                   and node.value.startswith("./") and id(node) not in in_fstring})


@pytest.mark.parametrize("script", ["ksnv.py", "shopping_cart.py", "contect.py", "kiosk.py"])
def test_relative_paths_match_folder_case(script):
    # 폴더 부분만 확인한다 (파일 이름 자체의 오류는 이 테스트의 범위가 아님)
    folders = {str(Path(p).parent) for p in relative_path_literals(APP / script)}
    missing = sorted(f for f in folders if not exists_case_sensitive(APP, f))
    assert missing == [], f"{script}: 대소문자까지 일치하는 폴더가 없음 {missing}"


def test_cart_plus_button_updates_database(tmp_path):
    # ksnv.py 장바구니의 + 버튼(shopping_cart.ShoppingItemWidget)이 data/data.db를 실제로 고치는지 확인
    for item in ("data", "img"):
        shutil.copytree(APP / item, tmp_path / item)
    shutil.copy2(APP / "shopping_cart.py", tmp_path / "shopping_cart.py")
    script = textwrap.dedent("""
        import sqlite3, sys
        from PyQt5.QtWidgets import QApplication, QListWidget, QLabel, QPushButton
        app = QApplication(sys.argv)
        con = sqlite3.connect("data/data.db")
        con.execute("DELETE FROM order_table")
        con.execute("INSERT INTO order_table (id, drink_cnt, order_drink, price, custom_option) "
                    "VALUES ('1', 1, '아메리카노', 2000, '[]')")
        con.commit(); con.close()
        from shopping_cart import ShoppingItemWidget
        widget = ShoppingItemWidget('1', '아메리카노', '2000', QListWidget(), QLabel(), QPushButton())
        widget.increase_button.click()
        con = sqlite3.connect("data/data.db")
        print("drink_cnt", con.execute("SELECT drink_cnt FROM order_table WHERE id = '1'").fetchone()[0])
    """)
    env = dict(os.environ, QT_QPA_PLATFORM="offscreen")
    proc = subprocess.run([sys.executable, "-c", script], cwd=tmp_path, env=env,
                          capture_output=True, text=True, timeout=60)
    assert "drink_cnt 2" in proc.stdout, proc.stdout + proc.stderr
