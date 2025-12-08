import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic

# UI 파일 연결
# 단, UI 파일은 Python 코드 파일과 같은 디렉토리에 위치해야 합니다.
form_class = uic.loadUiType("C:\ksitscma-sef\ksitscma-sef\QT_design.ui")[0]

# 화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 버튼과 시그널/슬롯 연결
        self.btn_coffee.clicked.connect(self.go_to_page1)
        self.btn_decaffein.clicked.connect(self.go_to_page2)
        self.btn_tea.clicked.connect(self.go_to_page3)
        self.btn_drinks.clicked.connect(self.go_to_page4)
        self.btn_food.clicked.connect(self.go_to_page5)
        self.btn_products.clicked.connect(self.go_to_page6)
        
        # 각 뒤로 가기 버튼에 시그널/슬롯 연결
        self.btn_back_1.clicked.connect(self.go_to_page0)
        self.btn_back_2.clicked.connect(self.go_to_page0)
        self.btn_back_3.clicked.connect(self.go_to_page0)
        self.btn_back_4.clicked.connect(self.go_to_page0)
        self.btn_back_5.clicked.connect(self.go_to_page0)
        self.btn_back_6.clicked.connect(self.go_to_page0)
        self.btn_back_7.clicked.connect(self.go_to_page0)
        
        # 각 구매 버튼에 시그널/슬롯 연결
        self.btn_purchase_1.clicked.connect(self.go_to_page7)
        self.btn_purchase_2.clicked.connect(self.go_to_page7)
        self.btn_purchase_3.clicked.connect(self.go_to_page7)
        self.btn_purchase_4.clicked.connect(self.go_to_page7)
        self.btn_purchase_5.clicked.connect(self.go_to_page7)
        self.btn_purchase_6.clicked.connect(self.go_to_page7)

    def go_to_page(self, index):
        # 현재 페이지 인덱스를 전달받아 해당 페이지로 전환
        self.stackedWidget.setCurrentIndex(index)

    def go_to_page0(self):
        # 첫 번째 페이지로 이동
        self.stackedWidget.setCurrentIndex(0)

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
        # 일곱 번째 페이지로 이동
        self.go_to_page(7)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.stackedWidget.setCurrentIndex(0)  # 초기 화면으로 index 0 페이지를 설정
    myWindow.show()
    sys.exit(app.exec_())
