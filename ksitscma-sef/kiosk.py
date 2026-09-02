from pathlib import Path
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow

BASE_DIR = Path(__file__).resolve().parent
UI_PATH = BASE_DIR / "QT_design.ui"

if not UI_PATH.exists():
    raise FileNotFoundError(f"UI 파일을 찾을 수 없습니다: {UI_PATH}")

form_class = uic.loadUiType(str(UI_PATH))[0]


class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.btn_coffee.clicked.connect(self.go_to_page1)
        self.btn_decaffein.clicked.connect(self.go_to_page2)
        self.btn_tea.clicked.connect(self.go_to_page3)
        self.btn_drinks.clicked.connect(self.go_to_page4)
        self.btn_food.clicked.connect(self.go_to_page5)
        self.btn_products.clicked.connect(self.go_to_page6)

        self.btn_back_1.clicked.connect(self.go_to_page0)
        self.btn_back_2.clicked.connect(self.go_to_page0)
        self.btn_back_3.clicked.connect(self.go_to_page0)
        self.btn_back_4.clicked.connect(self.go_to_page0)
        self.btn_back_5.clicked.connect(self.go_to_page0)
        self.btn_back_6.clicked.connect(self.go_to_page0)
        self.btn_back_7.clicked.connect(self.go_to_page0)

        self.btn_purchase_1.clicked.connect(self.go_to_page7)
        self.btn_purchase_2.clicked.connect(self.go_to_page7)
        self.btn_purchase_3.clicked.connect(self.go_to_page7)
        self.btn_purchase_4.clicked.connect(self.go_to_page7)
        self.btn_purchase_5.clicked.connect(self.go_to_page7)
        self.btn_purchase_6.clicked.connect(self.go_to_page7)

    def go_to_page(self, index):
        self.stackedWidget.setCurrentIndex(index)

    def go_to_page0(self):
        self.go_to_page(0)

    def go_to_page1(self):
        self.go_to_page(1)

    def go_to_page2(self):
        self.go_to_page(2)

    def go_to_page3(self):
        self.go_to_page(3)

    def go_to_page4(self):
        self.go_to_page(4)

    def go_to_page5(self):
        self.go_to_page(5)

    def go_to_page6(self):
        self.go_to_page(6)

    def go_to_page7(self):
        self.go_to_page(7)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WindowClass()
    window.stackedWidget.setCurrentIndex(0)
    window.show()
    sys.exit(app.exec_())
