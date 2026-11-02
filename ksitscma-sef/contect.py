import os
import sys
import threading
import ast
import re

import time
import sqlite3
import datetime
import pandas as pd
from random import randint

from PyQt5 import uic
from PyQt5.QtGui import *
main_app = None
import shopping_cart
from shopping_cart import *

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtCore import QTimer

import pyttsx3
import cv2
import dlib
import speech_recognition as sr
from deepface import DeepFace
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class KioskApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.image_folder = "C:/ksitscma-sef/ksitscma-sef/background/"  # 이미지 폴더 경로 지정 (슬래시 사용), 절대경로 써도 됨, 상대경로는 폴더 내에 다 사진 넣을것
        self.menu_image_folders = {
            "Coffee": "C:/ksitscma-sef/ksitscma-sef/menu/Coffee/",
            "Ade": "C:/ksitscma-sef/ksitscma-sef/menu/Ade/",
            "Dessert": "C:/ksitscma-sef/ksitscma-sef/menu/Dessert/",
            "Tea": "C:/ksitscma-sef/ksitscma-sef/Tea/"
        }
        self.title("Kiosk UI")
        self.geometry("768x1024")
        self.resizable(False, False)  # 창 크기 조정 비활성화
        self.attributes("-fullscreen", True)
        self.cart = []
        self.current_image_index = 0
        self.images = [self.image_folder + "image1.jpg", self.image_folder + "image2.jpg",
                       self.image_folder + "image3.jpg"]
        self.setup_first_page()

    def setup_first_page(self):
        self.first_page_frame = tk.Frame(self)
        self.first_page_frame.pack(fill="both", expand=True)

        self.photo_labels = []
        for img_path in self.images:
            img = Image.open(img_path).resize((768, 1024), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(self.first_page_frame, image=photo)
            label.photo = photo  # 이미지 참조 유지
            label.bind("<Button-1>", self.go_to_second_page)
            self.photo_labels.append(label)

        self.photo_labels[self.current_image_index].pack(fill="both", expand=True)
        self.after(3000, self.next_image)

    def next_image(self):
        self.photo_labels[self.current_image_index].pack_forget()
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.photo_labels[self.current_image_index].pack(fill="both", expand=True)
        self.after(3000, self.next_image)

    def go_to_second_page(self, event=None):
        self.first_page_frame.pack_forget()
        self.setup_second_page()

    def setup_second_page(self):
        self.second_page_frame = tk.Frame(self, width=768, height=1024)
        self.second_page_frame.pack(fill="both", expand=True)
        self.second_page_frame.pack_propagate(False)  # 전체 크기 고정

        # 전체 768x1024를 아래와 같이 분배
        # 상단 카테고리: 70px
        # 하단 카트: 170px
        # 중앙 콘텐츠: 784px (1024-70-170)

        # 카테고리 버튼 스타일 설정
        style = ttk.Style()
        style.configure('Category.TButton', font=('Arial', 18, 'bold'))

        self.menu_categories = ["Coffee", "Tea", "Ade", "Dessert"]
        self.menu_buttons = []

        # 상단 카테고리 버튼 영역
        self.top_frame = tk.Frame(self.second_page_frame, height=70, bg="#f0f0f0")
        self.top_frame.pack(side="top", fill="x")
        self.top_frame.pack_propagate(False)  # 높이 고정

        # 카테고리 버튼 동일한 너비로 배치
        for i, category in enumerate(self.menu_categories):
            frame = tk.Frame(self.top_frame)
            frame.pack(side="left", fill="both", expand=True)
            button = ttk.Button(frame, text=category, style='Category.TButton',
                                command=lambda c=category: self.show_menu(c))
            button.pack(fill="both", expand=True, padx=2, pady=5)
            self.menu_buttons.append(button)

        # 메뉴 콘텐츠 영역 (스크롤 가능한 중앙 영역)
        self.middle_frame = tk.Frame(self.second_page_frame, height=784)
        self.middle_frame.pack(fill="both", expand=True)

        # 하단 장바구니 및 결제 버튼 영역
        self.bottom_frame = tk.Frame(self.second_page_frame, height=170, bg="#f5f5f5")
        self.bottom_frame.pack(side="bottom", fill="x")
        self.bottom_frame.pack_propagate(False)  # 높이 고정

        # 장바구니 영역 (70% 너비)
        self.cart_frame = tk.Frame(self.bottom_frame)
        self.cart_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # 장바구니 헤더 프레임 - 타이틀과 총액 표시
        cart_header = tk.Frame(self.cart_frame)
        cart_header.pack(fill="x")

        # 장바구니 타이틀과 총액을 같은 줄에 표시
        self.cart_label = tk.Label(cart_header, text="Cart", font=("Arial", 20, "bold"))
        self.cart_label.pack(side="left")

        self.cart_total_label = tk.Label(cart_header, text="Total: $0.00", font=("Arial", 18, "bold"))
        self.cart_total_label.pack(side="right", padx=10)

        # 장바구니 목록
        self.cart_listbox = tk.Listbox(self.cart_frame, height=4, font=("Arial", 16))
        self.cart_listbox.pack(fill="both", expand=True, pady=5)

        # 결제 버튼 영역 (30% 너비)
        payment_frame = tk.Frame(self.bottom_frame, width=220)
        payment_frame.pack(side="right", fill="both", padx=5, pady=5)

        # 결제 버튼
        self.payment_button = ttk.Button(payment_frame, text="Pay", style='Category.TButton',
                                         command=self.pay)
        self.payment_button.pack(fill="both", expand=True, padx=10, pady=10)

        # 초기 메뉴 표시
        self.show_menu("Coffee")

    def show_menu(self, category):
        # 기존 위젯 제거
        for widget in self.middle_frame.winfo_children():
            widget.destroy()

        # 메인 프레임
        content_frame = tk.Frame(self.middle_frame, width=768, height=784)
        content_frame.pack(fill="both", expand=True)
        content_frame.pack_propagate(False)  # 크기 고정

        # 캔버스와 스크롤바 설정
        canvas = tk.Canvas(content_frame, width=768, height=784)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        # 스크롤바와 캔버스 배치
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # 스크롤 가능한 프레임 생성
        scrollable_frame = tk.Frame(canvas, width=768)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # 스크롤 가능한 프레임을 캔버스에 배치
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=768)

        # 캔버스 크기가 변경될 때 프레임 너비 조정
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=canvas.winfo_width())

        canvas.bind("<Configure>", configure_scroll_region)

        # 이미지 폴더 설정
        image_folder = self.menu_image_folders[category]

        # 카테고리에 따라 개별 메뉴 설정/이름 다 바꿔도 상관없음
        if category == "Coffee":
            self.menu_items = [
                {"name": "Americano", "price": 5.0, "image": image_folder + "아메리카노.jpg"},
                {"name": "Latte", "price": 5.5, "image": image_folder + "라떼.jpg"},
                {"name": "Cappuccino", "price": 6.0, "image": image_folder + "카푸치노.jpeg"},
                {"name": "Espresso", "price": 6.5, "image": image_folder + "에스프레소.jpg"},
                {"name": "Mocha라떼", "price": 6.0, "image": image_folder + "모카라떼.jpg"},
                {"name": "Macchiato", "price": 6.5, "image": image_folder + "마카치노.jpg"},
                {"name": "Flat White", "price": 6.0, "image": image_folder + "플랫화이트.png"},
                {"name": "Ristretto", "price": 6.5, "image": image_folder + "도피오.jpg"},
                {"name": "Affogato", "price": 7.0, "image": image_folder + "아포가토.jpg"},
                {"name": "Irish Coffee", "price": 7.5, "image": image_folder + "아이리쉬.jpg"},
                {"name": "초코프라페", "price": 8.0, "image": image_folder + "프라페.jpg"},
                {"name": "모카프라페", "price": 8.5, "image": image_folder + "모카프라페.jpg"},
                {"name": "자바칩프라페", "price": 9.0, "image": image_folder + "자바칩프라페.jpg"},
                {"name": "키라멜프라페", "price": 9.5, "image": image_folder + "카라멜프라페.png"},
                {"name": "콘파냐", "price": 10.0, "image": image_folder + "콘파냐.jpg"},
                {"name": "오늘의 커피", "price": 10.5, "image": image_folder + "오늘커피.jpg"}
            ]
        elif category == "Tea":
            self.menu_items = [
                {"name": "녹차", "price": 4.0, "image": image_folder + "녹차.jpg"},
                {"name": "홍차", "price": 4.5, "image": image_folder + "tea.jpg"},
                {"name": "차이", "price": 5.5, "image": image_folder + "차이티.jpg"},
                {"name": "우롱차", "price": 4.0, "image": image_folder + "우롱차.jpg"},
                {"name": "캐모마일", "price": 4.5, "image": image_folder + "캐모마일.jpg"},
                {"name": "히비스커스", "price": 5.0, "image": image_folder + "히비스커스.jpg"},
                {"name": "자스민", "price": 5.5, "image": image_folder + "자스민차.jpg"},
                {"name": "얼그레이", "price": 6.0, "image": image_folder + "얼그레이.png"},
                {"name": "딸기피지오", "price": 6.5, "image": image_folder + "딸기피지오.jpg"},
                {"name": "라임피지오", "price": 7.0, "image": image_folder + "라임피지오.jpg"},
                {"name": "아이스티", "price": 7.5, "image": image_folder + "아이스티.jpg"},
                {"name": "아이스티 레몬", "price": 8.0, "image": image_folder + "아이스티레몬.jpg"},
                {"name": "자몽 피지오", "price": 8.5, "image": image_folder + "자몽피지오.jpg"},
                {"name": "콤부차", "price": 9.0, "image": image_folder + "콤부차.jpg"},
                {"name": "말차라떼", "price": 9.5, "image": image_folder + "말차라떼.jpg"}
            ]
        elif category == "Ade":
            self.menu_items = [
                {"name": "레몬에이드", "price": 5.0, "image": image_folder + "레몬에이드.jpg"},
                {"name": "블루레몬에이드", "price": 5.5, "image": image_folder + "블루레몬에이드.jpg"},
                {"name": "오렌지스무디", "price": 6.0, "image": image_folder + "오렌지스무디.jpg"},
                {"name": "청포도에이드", "price": 6.5, "image": image_folder + "청포도에이드.png"},
                {"name": "라임모히또", "price": 6.0, "image": image_folder + "라임모히또.jpg"},
                {"name": "망고스무디", "price": 6.5, "image": image_folder + "망고스무디.jpg"},
                {"name": "망고요거트스무디", "price": 7.0, "image": image_folder + "망고요거트스무디.jpg"},
                {"name": "복숭아스무디", "price": 7.5, "image": image_folder + "복숭아스무디.png"},
                {"name": "청포도스무디", "price": 8.0, "image": image_folder + "청포도스무디.jpg"},
                {"name": "요거트스무디", "price": 8.5, "image": image_folder + "요거트스무디.jpg"},
                {"name": "키위스무디", "price": 9.0, "image": image_folder + "키위스무디.jpg"},
                {"name": "딸기스무디", "price": 9.5, "image": image_folder + "딸기스무디.jpg"},
                {"name": "딸기요거트스무디", "price": 10.0, "image": image_folder + "딸기요거트스무디.jpg"},
                {"name": "파인애플스무디", "price": 10.5, "image": image_folder + "파인애플스무디.jpg"},
                {"name": "자몽에이드", "price": 11.0, "image": image_folder + "자몽에이드.jpg"},
                {"name": "수박주스", "price": 11.5, "image": image_folder + "수박주스.jpg"}
            ]
        elif category == "Dessert":
            self.menu_items = [
                {"name": "치즈케이크", "price": 5.0, "image": image_folder + "치즈케이크.jpg"},
                {"name": "티라미수", "price": 5.5, "image": image_folder + "티라미수.jpg"},
                {"name": "토스트", "price": 6.0, "image": image_folder + "토스트.jpg"},
                {"name": "레드벨벳", "price": 6.5, "image": image_folder + "레드벨벳.jpg"},
                {"name": "초코크림", "price": 6.0, "image": image_folder + "초코크림.jpg"},
                {"name": "머핀", "price": 6.5, "image": image_folder + "머핀.jpg"},
                {"name": "소금빵", "price": 7.0, "image": image_folder + "소금빵.jpg"},
                {"name": "마카롱", "price": 7.5, "image": image_folder + "마카롱.jpg"},
                {"name": "스콘", "price": 8.0, "image": image_folder + "스콘.jpg"},
                {"name": "치아바타", "price": 9.0, "image": image_folder + "치아바타.jpg"},
                {"name": "샌드위치", "price": 9.5, "image": image_folder + "belt샌드위치.jpg"},
                {"name": "베이글", "price": 10.0, "image": image_folder + "베이글.jpg"},
                {"name": "카스테라", "price": 10.5, "image": image_folder + "카스테라.jpg"},
                {"name": "푸딩", "price": 11.0, "image": image_folder + "푸딩.jpg"},
                {"name": "까눌레", "price": 11.5, "image": image_folder + "까눌레.jpg"}
            ]
        scrollable_frame.grid_columnconfigure(0, weight=1)
        scrollable_frame.grid_columnconfigure(1, weight=1)

        # 메뉴 아이템 배치
        for i, item in enumerate(self.menu_items):
            row = i // 2
            col = i % 2

            # 프레임 생성 (고정 너비)
            frame = tk.Frame(scrollable_frame, bd=2, relief="solid", width=375, height=350)
            frame.grid(row=row, column=col, padx=3, pady=5, sticky="nsew")
            frame.grid_propagate(False)  # 프레임 크기 고정

            # 이미지 로드 및 표시
            try:
                img = Image.open(item['image']).resize((350, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                label_image = tk.Label(frame, image=photo)
                label_image.photo = photo
                label_image.pack(fill="both", expand=True, padx=5, pady=5)
            except Exception as e:
                print(f"Error loading image: {e}")
                label = tk.Label(frame, text="[Image]", font=("Arial", 20))
                label.pack(fill="both", expand=True, padx=5, pady=5)

            # 이름 및 가격 표시
            name_label = tk.Label(frame, text=item['name'], font=("Arial", 18, "bold"))
            name_label.pack(anchor="w", padx=10)

            price_label = tk.Label(frame, text=f"${item['price']:.2f}", font=("Arial", 16))
            price_label.pack(anchor="w", padx=10)

            # 선택 버튼
            button_frame = tk.Frame(frame)
            button_frame.pack(fill="x", padx=10, pady=5)

            style = ttk.Style()
            style.configure('Menu.TButton', font=('Arial', 16, 'bold'))

            select_button = ttk.Button(button_frame, text="Select", style='Menu.TButton',
                                       command=lambda item=item: self.show_options(item))
            select_button.pack(fill="x")

        # 마지막 행 이후 추가 공간 확보 (스크롤 확인용)
        empty_frame = tk.Frame(scrollable_frame, height=20)
        empty_frame.grid(row=len(self.menu_items) // 2 + 1, column=0, columnspan=2)

        # 마우스 휠 이벤트 바인딩
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

    def show_options(self, item):
        options_window = tk.Toplevel(self)
        options_window.title("Options")
        options_window.geometry("600x400")  # 옵션창 크기 조정
        options_window.transient(self)
        options_window.grab_set()

        # 화면 중앙에 배치
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (400 // 2)
        options_window.geometry(f"600x400+{x}+{y}")

        # 메뉴 이름과 가격 표시
        header_frame = tk.Frame(options_window)
        header_frame.pack(fill="x", pady=10)

        name_label = tk.Label(header_frame, text=item['name'], font=("Arial", 20, "bold"))
        name_label.pack()

        price_label = tk.Label(header_frame, text=f"${item['price']:.2f}", font=("Arial", 16))
        price_label.pack()

        # 카테고리에 따라 옵션 표시 여부 결정
        if any(category in item.get('category', '') for category in ["Coffee", "Tea", "Ade"]):
            # 음료 옵션 표시
            options_frame = tk.Frame(options_window)
            options_frame.pack(fill="both", expand=True, padx=20)

            option1 = tk.Checkbutton(options_frame, text="Add Shot (+$0.5)", font=("Arial", 16))
            option1.pack(anchor="w", pady=10)

            option2 = tk.Checkbutton(options_frame, text="Iced/Hot", font=("Arial", 16))
            option2.pack(anchor="w", pady=10)

        # 버튼 스타일 설정
        style = ttk.Style()
        style.configure('Option.TButton', font=('Arial', 16, 'bold'))

        button_frame = tk.Frame(options_window)
        button_frame.pack(fill="x", pady=20)

        add_button = ttk.Button(button_frame, text="Add to Cart", style='Option.TButton',
                                command=lambda: self.add_to_cart(item, options_window))
        add_button.pack(side="left", padx=50)

        cancel_button = ttk.Button(button_frame, text="Cancel", style='Option.TButton',
                                   command=options_window.destroy)
        cancel_button.pack(side="right", padx=50)

    def add_to_cart(self, item, window):
        self.cart.append(item)
        self.update_cart()
        window.destroy()

    def update_cart(self):
        self.cart_listbox.delete(0, tk.END)
        total = 0.0
        for item in self.cart:
            self.cart_listbox.insert(tk.END, f"{item['name']} - ${item['price']:.2f}")
            total += item['price']
        self.cart_total_label.config(text=f"Total: ${total:.2f}")

    def pay(self):
        self.second_page_frame.pack_forget()
        self.show_payment_processing()

    def show_payment_processing(self):
        processing_frame = tk.Frame(self)
        processing_frame.pack(fill="both", expand=True)

        label = tk.Label(processing_frame, text="Processing Payment...", font=("Arial", 40))
        label.pack(expand=True)

        self.after(3000, self.reset_to_first_page)

    def reset_to_first_page(self):
        self.destroy()
        main_app.showMaximized()  # show() 대신 showMaximized() 사용
        main_app.activateWindow()  # 창 활성화
        main_app.raise_()
        # 중요: 메인 앱으로 돌아갈 때 디지털 문맹자 감지 로직 재시작
        threading.Thread(target=main_app.continuous_face_analysis, args=(0,), daemon=True).start()
        threading.Thread(target=main_app.continuous_eye_tracking, args=(1,), daemon=True).start()
        '''
        for widget in self.winfo_children():
            widget.destroy()
        self.cart = []
        self.current_image_index = 0
        self.setup_first_page()
        '''


def resource_path(relative_path):
    """UI 받아오는 함수"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# UI 불러오기
main_page_class = uic.loadUiType(resource_path('./ui/mega_ui_ver3.ui'))[0] # 메가 메인 UI 불러오기
choose_option_class = uic.loadUiType(resource_path('./ui/mega_choose_option_page.ui'))[0] # 메가 음료옵션창 불러오기
msg_box_class = uic.loadUiType(resource_path('./ui/msg_box.ui'))[0]  # 메세지박스 ui 불러오기
point_page_class = uic.loadUiType(resource_path('./ui/point_page.ui'))[0] # 포인트페이지 창 띄우기
manager_page_class = uic.loadUiType(resource_path('./ui/manager_page.ui'))[0] # 관리자페이지
receipt_page = uic.loadUiType(resource_path('./ui/receipt_page_2.ui'))[0] # 영수증 창

class Rept(QDialog, receipt_page):
    """영수증"""
    def __init__(self, parent, order_num, t_price):
        super().__init__()
        self.setupUi(self)
        self.parent = parent

        self.order_number_label.setText(str(order_num))
        self.total_price_label.setText(str(t_price))
        self.set_datetime()

        self.parent.fill_the_table_widget(self.tableWidget)

    def set_datetime(self):
        now = datetime.datetime.now()
        formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
        self.date_label.setText(str(formatted_now))

class Point_Page(QDialog, point_page_class):
    """포인트 적립 창"""
    data_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 화면 설정
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)  # 프레임 지우기 / 윈도우가 다른 창 위에 항상 최상위로 유지되도록 함
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # 배경 투명하게 함

        # 버튼 모으기
        buttons = self.point_buttons.findChildren(QPushButton)
        for button in buttons:
            button.clicked.connect(self.write_point_num)

        # 버튼 시그널 설정
        self.point_confirm_btn.clicked.connect(self.point_check)  # 확인 버튼
        self.cancel_btn.clicked.connect(self.close)  # x 버튼

    def write_point_num(self):
        """번호를 누르면 번호창에 업데이트 된다"""
        num_list = [str(num) for num in range(0, 10)]  # 버튼은 0부터 010까지 존재함
        num_list.append('010')

        self.user_num = []
        btn_name = self.sender().text()  # 누른 버튼 텍스트 가져옴
        now_label_text = self.user_number_label.text()  # 라벨의 텍스트 가져옴

        if btn_name in num_list:
            now_label_text += str(btn_name)
            self.only_num = now_label_text.replace('-', '')
            self.user_num.append(self.user_num.append(btn_name))
            print('누를때', self.user_num)
            if len(self.only_num) <= 11:
                self.user_number_label.setText(self.mask_numbers(now_label_text))
        else:
            self.user_num = self.user_num[:-1]
            print('지울때', self.user_num)
            now_label_text = now_label_text[:-1]
            self.user_number_label.setText(self.mask_numbers(now_label_text))

    def mask_numbers(self, i):
        i = i.replace('-', '')
        if len(i) <= 3:
            return i
        elif 3 < len(i) < 8:
            return f'{i[:3]}-{(len(i) - 3) * "*"}'
        else:
            return i[:3] + '-****-' + i[7:]

    def point_check(self):
        now_label_text = self.user_number_label.text()  # 라벨의 텍스트 가져옴
        if len(now_label_text) == 11:
            self.data_signal.emit(now_label_text)
            self.close()
        else:
            self.close()
            con = sqlite3.connect('./data/data.db')
            df = pd.read_sql('select * from order_table', con)
            df.loc[:, 'customer_id'] = self.user_num
            df.to_sql('order_table', con, if_exists='replace', index=False)
            con.commit()
            con.close()
            print('포인트 적립 확인')

class MSG_Dialog(QDialog, msg_box_class):
    """메세지 박스 다이얼로그"""
    data_signal = pyqtSignal(str)

    def __init__(self, parent, page_data):
        super().__init__(parent)
        self.parent = parent
        self.setupUi(self)

        # 화면 설정
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)  # 프레임 지우기 / 윈도우가 다른 창 위에 항상 최상위로 유지되도록 함
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # 배경 투명하게 함
        self.sign = page_data
        self.stackedWidget.setCurrentWidget(self.one_btn_page)

        # 버튼 페이지 설정
        if page_data == 1:
            self.info_label.setText("메뉴가 품절이라 선택하실 수 없습니다.")
        elif page_data == 2:
            self.info_label.setText("메뉴를 1개 이상 선택하셔야 합니다.")
        elif page_data == 3:
            self.info_label.setText(f"결제중입니다.. 5초 후에 창이 닫힙니다.")
            self.remain_time = 5
            self.p_timer = QTimer()
            self.p_timer.timeout.connect(self.update_p_timer)
            self.p_timer.setInterval(1000)
            self.p_timer.start()
        elif page_data == 4:
            self.info_label.setText("포인트 적립을 하시겠습니까?")
            self.stackedWidget.setCurrentWidget(self.two_btn_page)
        elif page_data == 5:
            self.info_label.setText("회원정보가 사라집니다. 계속하시겠습니까?")
            self.stackedWidget.setCurrentWidget(self.two_btn_page)
        elif page_data == 6:
            self.info_label.setText("유효한 카드번호가 아닙니다. 다시 입력하세요.")
        elif page_data == 7:
            self.info_label.setText("이미 KT할인이 적용되었습니다.")
        elif page_data == 8:
            self.info_label.setText("영수증 출력을 하시겠습니까?")
            self.stackedWidget.setCurrentWidget(self.two_btn_page)
        else:
            pass

        # 버튼 누르면 정보 넘겨주기
        self.ok_btn.clicked.connect(self.check_and_close)  # 확인 누르면 확인하고 창 닫힘

        self.no_btn.clicked.connect(self.check_no_btn_and_close)  # 취소 누르면 창 닫힘
        self.yes_btn.clicked.connect(self.show_num_keypad)

    def check_and_close(self):
        print('닫기를 탐')
        if self.sign == 8:
            print('영수증 드릴게')

        else:
            self.close()

    def check_no_btn_and_close(self):
        if self.sign == 4:
            print('여기서 오픈 페이지로 바뀝니다. 그리고 데이터 삭제해야 함')
            self.close()
            msg_box_page = MSG_Dialog(self.parent, 8)  # 포인트 창이 뜨고
            msg_box_page.exec_()
        if self.sign == 8:
            self.close()
            self.parent.stackedWidget.setCurrentWidget(self.parent.opening_page)
            self.parent.timer.start()
            self.parent.delete_order_table_values()  # 테이블 내용 삭제
            # 홈 화면으로 돌아갈 때 디지털 문맹자 감지 재시작
            self.parent.resetDigitalLiteracyStatus()
            # 창 활성화 코드 추가
            self.parent.showMaximized()
            self.parent.activateWindow()
            self.parent.raise_()
        else:
            self.close()

    def update_p_timer(self):
        self.remain_time -= 1
        if self.remain_time == 0:  # 시간이 종료되면
            self.p_timer.stop()  # 타이머가 멈추고
            self.close()
            self.show_point_msg_box()
        self.info_label.setText(f"결제중입니다.. {self.remain_time}초 후에 창이 닫힙니다.")

    def show_point_msg_box(self):
        msg_box_page = MSG_Dialog(self.parent, 4)  # 포인트 창이 뜨고
        msg_box_page.exec_()

    def show_num_keypad(self):
        """숫자패드 창 띄우기"""
        if not self.sign == 8:
            self.close()
            key_page = Point_Page()
            key_page.data_signal.connect(self.get_label_text)
            key_page.show()
            key_page.exec_()
        else:
            self.parent.order_num += 1  # 주문번호 늘리기
            rept = Rept(self.parent, self.parent.order_num, self.parent.get_total_price())
            rept.show()
            rept.exec_()
            self.close()
            self.parent.stackedWidget.setCurrentWidget(self.parent.opening_page)
            self.parent.timer.start()
            self.parent.delete_order_table_values()  # 테이블 내용 삭제
            # 주문 완료 후 디지털 문맹자 감지 로직 초기화 및 재시작
            self.parent.initDigitalLiteracyAnalysis() # 테이블 내용 삭제
            self.parent.showMaximized()
            self.parent.activateWindow()
            self.parent.raise_()

    def get_label_text(self, text):
        print('테스트 텍스트 출력=============')
        print(text)

class Option_Class(QDialog, choose_option_class):
    """선택옵션 창"""
    data_signal = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setupUi(self)

        # 화면 설정
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)  # 프레임 지우기 / 윈도우가 다른 창 위에 항상 최상위로 유지되도록 함
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # 배경 투명하게 함
        self.move(30, 40)  # 창 이동

        # 가격 이름 메뉴정보 불러오기
        data = parent.send_info
        self.drink_name = data['menu_name_x'].to_string(index=False)
        self.drink_price = data['price'].to_string(index=False)
        self.drink_info = data['info'].to_string(index=False)

        # 정보 담기
        self.menu_photo_label.setPixmap(QPixmap(data['img_path'].to_string(index=False)))  # 메뉴 이미지
        self.menu_name_label.setText(str(self.drink_name))  # 메뉴 이름
        self.menu_info_label.setText(str(self.drink_info))  # 메뉴 정보
        self.menu_price_label.setText(str(self.drink_price) + '원')  # 메뉴 가격

        # 옵션 위한 테이블 생성
        option_df = data.loc[:, 'cinnamon':'zero_cider_changed']
        option_df_dict = option_df.to_dict('list')
        option_df_keys = list(option_df_dict.keys())
        option_df_keys.append('decaffein')
        print(option_df_keys)
        option_df_dict_not_null = {key: [int(x) for x in value[0].split(',')] for key, value in option_df_dict.items()
                                   if value != ['0']}  # 0이 들어가지 않은 인수형의 숫자 반환

        if '디카페인' in self.drink_name:  # 디카페인은 db에서 분리를안해서 후작업
            option_df_dict_not_null['decaffein'] = 1
            del option_df_dict_not_null['strong_or_weak']

        # 음료에 따라 옵션창 띄워주는 부분
        self.option_frame_list = [getattr(self, f'option_frame_{frame}') for frame in range(1, 13)]  # 프레임들을 리스트에 담음

        for idx, key in enumerate(option_df_keys):  # 음료에 맞게 옵션창 띄워줌
            if key in list(option_df_dict_not_null.keys()):
                self.option_frame_list[idx].setVisible(True)  # 음료에 있는 카테고리만 보여주고
            else:
                self.option_frame_list[idx].setVisible(False)  # 나머지는 안보여줌

        # 버튼 한번만 눌리게 체크
        self.btn_duplicates_check()

        # 버튼 누를 때마다 옵션 가격 추가해주는 시그널 연결
        self.option_buttons = self.option_bottom_frame.findChildren(QPushButton)
        for option_btn in self.option_buttons:
            option_btn.clicked.connect(self.set_extra_charge)
            if option_btn.isChecked():
                self.set_extra_charge()

        # 버튼 시그널 연결
        self.cancel_btn.clicked.connect(lambda x: self.close())  # 창 종료하기
        self.cancel_btn.clicked.connect(self.close)  # 창 종료하기
        self.order_btn.clicked.connect(self.order_confirm)
        self.reset_btn.clicked.connect(self.btn_duplicates_check)  # 옵션 초기화 버튼

        # db불러오기
        self.con = sqlite3.connect('./data/data.db')  # 데이터베이스 연결 정보 설정

    def set_extra_charge(self):
        """버튼 누를 때마다 옵션 가격 추가해주는 부분"""

        # 옵션 가격 데이터 불러오기
        option_price = pd.read_csv('./data/drinks_price.csv')
        option_price_eng_name = option_price['eng_name'].to_list()

        # 눌린 버튼들 확인하기 및 라벨에 업데이트
        add_price = 0
        self.customer_order_option_list = []
        self.customer_order_option_list_kor = []
        self.option_buttons = self.option_bottom_frame.findChildren(QPushButton)

        for btn in self.option_buttons:
            if btn.isChecked() and btn.isVisible():  # 체크된 버튼만 확인
                btn_object_name = btn.objectName()  # 버튼 객체 이름
                idx = option_price_eng_name.index(btn_object_name)  # 버튼의 index확인
                drinks_price = option_price.loc[idx, 'noraml_drink']  # 체크된 옵션 가격 가져오기
                drinks_option_name = option_price.loc[idx, 'eng_name']  # 체크된 옵션 영어 이름 가져오기
                drinks_option_kor_name = option_price.loc[idx, 'kor_name']
                add_price += drinks_price  # 가격 더해주기
                if '안함' not in drinks_option_kor_name:
                    self.customer_order_option_list_kor.append(drinks_option_kor_name)
                self.customer_order_option_list.append(drinks_option_name)

        # 상단에 값 추가
        self.update_drink_price = str(int(self.drink_price) + int(add_price))
        self.menu_price_label.setText(self.update_drink_price + '원')
        if len(self.customer_order_option_list_kor) != 0:
            self.choose_option_label.setText(str(', '.join(self.customer_order_option_list_kor)))
        else:
            self.choose_option_label.setText('없음')

    def btn_duplicates_check(self):
        """각 옵션창 프레임 내에 있는 버튼들 한번만 눌리게"""

        # 버튼 그룹 담아주기
        self.option_button_groups = []

        # 프레임들 안에 있는 버튼들을 각각 버튼 그룹으로 담아줌
        for i in range(1, 13):
            option_frame = self.option_frame_list[i - 1]
            buttons = option_frame.findChildren(QPushButton)
            button_group = QButtonGroup()
            button_group.setExclusive(True)

            for btn in buttons:
                button_group.addButton(btn)
            button_group.buttonClicked.connect(self.btn_check)  # 중복버튼 누르기 방지
            button_group.buttonClicked.connect(self.btn_clicked_style)  # 버튼 색 바뀌게 하기
            self.option_button_groups.append(button_group)

        # 각 옵션 선택창 안에 들어있는 1번 버튼 눌리게 하기
        for btn_group in self.option_button_groups:
            btn_group.buttons()[0].click()  # 첫번째 버튼 무조건 눌리게

    def btn_clicked_style(self, btn):
        """선택한 옵션버튼 색 바꿔줌"""
        for btn_group in self.option_button_groups:
            if btn in btn_group.buttons():
                for button in btn_group.buttons():
                    button.setStyleSheet('')
        btn.setStyleSheet('border: 3px solid rgb(229, 79, 65);')

    def btn_check(self):
        """버튼 그룹 가져와서 체크하는 부분"""
        sender = self.sender()  # 버튼 모두를 가져옴
        for button_group in self.option_button_groups:
            if sender not in button_group.buttons():
                button_group.setExclusive(True)

    def close(self):
        self.parent.remove_label()
        self.accept()

    def order_confirm(self):
        """선택옵션 확인 후 db에 저장"""

        self.parent.drink_num += 1  # 주문 수량 늘려줌
        option_str = str(self.customer_order_option_list)  # 리스트 str형태로 바꿔주기
        cur = self.con.cursor()  # 커서 생성
        cur.execute("INSERT INTO order_table (id, drink_cnt, order_drink, price, custom_option)"
                    "VALUES(?,?,?,?,?);",  # SQL 쿼리 실행
                    (self.parent.drink_num, 1, self.drink_name, self.update_drink_price, option_str))
        self.con.commit()  # 변경사항 저장

        # 장바구니 리스트위젯에 값 넣어주기
        add_shopping_item_to_listwidget(
            self.parent.drinks_cart_list_widget, str(self.parent.drink_num),
            self.drink_name, self.update_drink_price, self.parent.menu_cnt_label, self.parent.payment_admit_btn)

        # 메뉴 갯수 라벨에 넣어주기(담은 메뉴 수 라벨)
        cur.execute('SELECT SUM(drink_cnt) FROM order_table')  # 테이블에 있는 메뉴 수 세서
        result = cur.fetchone()[0]  # 이를 튜플 형태로 가져오고 첫번째 값만 가져옴
        self.parent.menu_cnt_label.setText(str(result) + '개')

        order_df = pd.read_sql('select * from order_table', self.con)
        order_df['drink_cnt'] = order_df['drink_cnt'].astype(int)
        order_df['price'] = order_df['price'].astype(int)
        total_price = (order_df['drink_cnt'] * order_df['price']).sum()
        self.parent.payment_admit_btn.setText(f'  {str(total_price)}원\n  결제하기')

        cur.close()  # 연결 종료
        self.con.close()
        # 선택옵션 창 종료
        self.parent.remove_label()
        self.accept()
        self.close()

        if self.parent.digital_literacy_detected:
            self.parent.tts_engine.say(self.drink_name)
            self.parent.tts_engine.runAndWait()

class WindowClass(QMainWindow, main_page_class):
    """오픈화면 & 메인화면 창"""
    clicked = pyqtSignal()
    def add_page_mouse_press(self, event):
        """오픈화면 누르면 발생하는 이벤트"""
        self.stackedWidget.setCurrentWidget(self.main_page)


    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)  # 창 테두리 제거
        self.showMaximized()

        # 초기 설정
        self.digital_literacy_detected = False  # 디지털 문맹자 판단 여부 초기화
        self.tts_engine = pyttsx3.init()
        # 얼굴 분석 및 눈 추적 스레드 시작
        self.startDigitalLiteracyAnalysis()
        self.setupVoiceRecognition()

        self.home_button.clicked.connect(self.resetDigitalLiteracyStatus)
        self.payment_admit_btn.clicked.connect(self.resetDigitalLiteracyStatusAfterPayment)
        self.home_button.clicked.connect(self.resetDigitalLiteracyStatus)

        # 오픈화면 #######################################################################################################
        self.stackedWidget.setCurrentIndex(0)  # 시작할때 화면은 오픈 페이지로 설정
        self.set_ad_image()  # 이미지 변경
        self.setWindowFlags(Qt.FramelessWindowHint) # 프레임 지우기
        self.move(10,30) #창이동

        # 페이지 이동 및 타이머 시작
        self.ad_label.mousePressEvent = lambda event: (self.stackedWidget.setCurrentWidget(self.main_page))  # 페이지 이동)

        # 메인화면 시작 ##################################################################################################

        # 0. DB 불러오기
        con = sqlite3.connect('./data/data.db')
        self.price_df = pd.read_sql('select * from drinks_price', con)  # 가격 테이블
        self.menu_df = pd.read_sql('select * from drinks_menu', con)  # 음료상세정보 전체 테이블
        self.img_path_df = pd.read_sql('select * from drinks_img_path', con)  # 음료 이미지 경로 테이블
        self.order_table_df = pd.read_sql('select * from order_table', con)  #
        self.drink_num = 0  # 음료 주문번호
        self.order_num = 100 # 고객 주문번호 100부터 시작

        # 1. 타이머
        # 타이머 기본 설정값
        self.DURATION_INT = 120
        self.remaining_time = self.DURATION_INT

        # # 타이머와 관련된 변수들
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.setInterval(1000)

        # 2. 카테고리 버튼 이동
        self.category_stackedWidget.setCurrentWidget(self.category_1)  # 기본값
        self.category_btn_list = [getattr(self, f"category_btn_{i}") for i in range(1, 16)]  # 카테고리 버튼 리스트화
        for btn in self.category_btn_list:
            btn.clicked.connect(self.set_categroy_num)  # 카테고리 하단 메뉴 크기 설정
            btn.clicked.connect(self.change_categroy_btn_color)  # 버튼 색 바꾸기
            btn.clicked.connect(self.show_menu_arrow_btn)  # 카테고리 하단 메뉴 크기 설정
            btn.clicked.connect(lambda: self.menu_stackedWidget.setCurrentWidget(self.page_1))  # 음료 페이지 1페이지로 초기화
            btn.clicked.connect(lambda x, category=btn: self.start_timer(btn))  # 카테고리 버튼 누를 때마다 타이머 초기화

        # 3. 카테고리 페이지 넘기기 (메인화면 페이지 넘기기)
        self.category_right_btn.clicked.connect(lambda: self.check_current_page(1))
        self.category_right_btn_2.clicked.connect(lambda: self.check_current_page(2))
        self.category_left_btn.clicked.connect(lambda: self.check_current_page(1))
        self.category_left_btn_2.clicked.connect(lambda: self.check_current_page(2))

        # 4. 커피 메뉴 좌/우 버튼
        self.category_btn_1.click()
        self.menu_arrow_btn_num = 2
        self.menu_left_btn.clicked.connect(lambda: self.menu_stackedWidget.setCurrentWidget(self.page_1))
        self.menu_right_btn.clicked.connect(lambda: self.menu_stackedWidget.setCurrentWidget(self.page_2))
        self.menu_right_btn.clicked.connect(self.show_menu_arrow_btn)
        self.menu_left_btn.clicked.connect(self.show_menu_arrow_btn)

        # 5. 프레임 버튼 클릭하기 및 가격 폰트 변경
        self.menu_frame_list = [getattr(self, f"menu_frame_{i}") for i in range(1, 25)]  # 메뉴 프레임 리스트화
        for frame in self.menu_frame_list:
            frame.mousePressEvent = lambda event, name=frame.objectName(): self.click_frame(event, name)

        # 6. 버튼 시그널 연결
        self.all_remove_label.clicked.connect(self.delete_order_table_values)  # 전체 삭제 버튼
        self.home_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.opening_page))  # 홈 버튼 누르면 오픈화면으로 이동

        # 주문확인화면 시작 ############################################################################################

        # 1. 주문확인창 시작 및 테이블위젯 채우기
        self.payment_admit_btn.clicked.connect(self.move_to_order_check_page)

        # 2. 버튼 시그널 연결 모음
        self.cancel_btn_2.clicked.connect(self.timer_restart_and_go_to_main_page)
        self.back_to_main_page_btn.clicked.connect(self.timer_restart_and_go_to_main_page)
        self.eat_here_btn.clicked.connect(lambda: self.move_to_payment_choose('for_here'))
        self.take_out_btn.clicked.connect(lambda: self.move_to_payment_choose('to_go'))

        # 결제수단선택창 ############################################################################################

        # 버튼 시그널 연결
        self.payment_choose_signal()
        self.cancel_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.order_check_page))  # x 버튼 누르면 주문확인창으로 이동
        self.kt_discount = False

        # 카드 / 큐알코드 결제창 ######################################################################################

        ### 1. 카드 결제창

        # 버튼 클릭 이벤트

        self.cancel_btn_3.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.payment_choose_page))  # x 버튼 누르면 결제선택수단창으로 이동
        self.cancel_btn_4.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.payment_choose_page))  # 취소  버튼 누르면 결제선택수단창으로 이동
        self.card_img_frame.mousePressEvent = lambda event: self.mobile_pay_msgbox()
        self.barcode_type = None
        ### 2. 큐알코드 결제창
        self.use_coupon.clicked.connect(self.askRcpt)  # 쿠폰사용버튼 -> 영수증 물어보는 함수로 이동 및 종료

        self.cancel_btn_5.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.payment_choose_page))  # x 버튼 누르면 결제선택수단창으로 이동
        self.order_btn_2.clicked.connect(self.check_discount_and_move)  # 할인 적용하고 이동

        # 숫자 키보드 버튼 누를때 이벤트 발생
        keyboard_buttons = self.keyboard_frame.findChildren(QPushButton)
        for btn in keyboard_buttons:
            btn.clicked.connect(self.change_card_num)

        # 기타 스타일시트 변경 부분 ###############################################################################
        # 큐알코드 커서 변경해주기
        self.qr_check_frame.setCursor(QCursor(QPixmap('./img/qt자료/bacord').scaled(80, 80)))
        self.card_label.setCursor(QCursor(QPixmap('./img/qt자료/payment_phone.png').scaled(120, 100)))
        self.horizontalSlider.setCursor(QCursor(QPixmap('./img/qt자료/matercard.png').scaled(80, 70)))

        self.digital_literacy_analysis_active = False

        #스레드
        self.detection_timer = QTimer(self)
        self.detection_timer.timeout.connect(self.deactivateDigitalLiteracyDetection)
        self.detection_timer.setSingleShot(True)

    ## 함수 시작 #######################################################################################################
    '''결제창 관련 함수'''
    ####
    def resetDigitalLiteracyStatusAfterPayment(self):
        """결제 후 디지털 문맹자 검사 상태 초기화 및 재시작"""
        self.initDigitalLiteracyAnalysis()

    def setupVoiceRecognition(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        # 음성 인식을 위한 스레드 시작
        threading.Thread(target=self.listenForCommands, daemon=True).start()

    def listenForCommands(self):
        """음성 인식을 수행하고 인식된 명령을 처리하는 메서드"""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)  # 배경 소음 조정

        while True:  # 음성 인식 루프
            try:
                print("Say something!")
                with self.microphone as source:
                    audio = self.recognizer.listen(source)
                # 구글 웹 서비스를 사용해 인식(다른 API로 변경 가능)
                command = self.recognizer.recognize_google(audio, language='ko-KR')
                print(f"Recognized command: {command}")

                # 인식된 명령 처리
                self.processCommand(command)

            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
            except Exception as e:
                print(f"An error occurred: {e}")

    def processCommand(self, command):
        """인식된 명령을 처리하는 메서드, 중복된 키워드 제거 후 메뉴 검색 및 추가"""
        # 키워드 분리 및 중복 제거
        keywords = list(set(re.findall(r'\w+', command)))  # 정규 표현식을 사용하여 단어 추출 및 중복 제거
        for keyword in keywords:
            # 메뉴 DB에서 각 키워드와 일치하는 메뉴 찾기
            matching_menus = self.menu_df[self.menu_df['menu_name'].str.contains(keyword, case=False, na=False)]
            if not matching_menus.empty:
                # 일치하는 메뉴가 있으면 첫 번째 메뉴를 쇼핑 카트에 추가
                menu_name = matching_menus.iloc[0]['menu_name']
                menu_price = matching_menus.iloc[0]['price']
                print(f"Adding {menu_name} to cart based on keyword: {keyword}")
                self.addMenuToCart(menu_name, str(menu_price))
                break  # 첫 번째 일치하는 메뉴를 추가한 후 반복문 종료
        else:
            print(f"No matching menu found for any keyword in command: {command}")

    def addMenuToCart(self, name, price):
        """메뉴를 쇼핑 카트에 추가하는 메서드"""
        idx = str(self.drink_num + 1)  # 예시 id, 실제로는 유니크한 값을 사용해야 함
        # 쇼핑 카트에 메뉴 추가하는 기능 호출
        add_shopping_item_to_listwidget(self.drinks_cart_list_widget, idx, name, price, self.menu_cnt_label,
                                        self.payment_admit_btn)
        self.drink_num += 1

    def initDigitalLiteracyAnalysis(self):
        """디지털 문맹자 분석을 초기화하고 재시작하는 함수"""
        print("디지털 문맹자 분석 초기화 및 재시작")
        # 기존 스레드가 있다면 중지 신호 보내기
        self.digital_literacy_analysis_active = False
        # 잠시 대기하여 스레드가 종료될 시간 부여
        time.sleep(0.5)
        # 상태 초기화
        self.digital_literacy_detected = False
        # 분석 활성화 및 새 스레드 시작
        self.digital_literacy_analysis_active = True
        threading.Thread(target=self.continuous_face_analysis, args=(0,), daemon=True).start()
        threading.Thread(target=self.continuous_eye_tracking, args=(1,), daemon=True).start()
        # TTS 엔진 재초기화
        self.tts_engine = pyttsx3.init()
        print("디지털 문맹자 분석 재시작 완료")

    def stopDigitalLiteracyAnalysis(self):
        # 디지털 문맹자 조회 중단
        self.digital_literacy_analysis_active = False

    def configureEvents(self):
        # 오프닝 페이지로 돌아가는 이벤트 설정
        self.home_button.clicked.connect(self.onHomeButtonClicked)

    def onHomeButtonClicked(self):

        # 오프닝 페이지로 이동
        self.stackedWidget.setCurrentWidget(self.opening_page)
        # 디지털 문맹자 감지 관련 변수 초기화
        self.initDigitalLiteracyAnalysis()

    def continuous_face_analysis(self, camera_id=0):
        """얼굴 분석을 계속 수행하는 메서드"""
        cap = cv2.VideoCapture(camera_id)
        print(f"카메라 {camera_id}로 얼굴 분석 시작")

        while True:  # 원래 코드처럼 무한 루프로 변경
            ret, frame = cap.read()
            if not ret:
                print(f"카메라 {camera_id}에서 프레임 읽기 실패, 재시도 중...")
                cap.release()
                time.sleep(1)  # 잠시 대기
                cap = cv2.VideoCapture(camera_id)  # 카메라 다시 열기
                continue

            faces = detector(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
            for face in faces:
                x, y, w, h = face.left(), face.top(), face.width(), face.height()
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                try:
                    face_img = frame[y:y + h, x:x + w]
                    results = DeepFace.analyze(face_img, actions=['age', 'emotion'], enforce_detection=False)
                    if isinstance(results, list):
                        if len(results) > 0:
                            results = results[0]
                        else:
                            continue

                    age = results['age']
                    emotion = results['dominant_emotion']
                    cv2.putText(frame, f"Age: {age}, Emotion: {emotion}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (0, 255, 0), 2)

                    if (emotion in ['surprise', 'angry'] or age >= 50) and not self.digital_literacy_detected:
                        print(f"카메라 {camera_id}: 감지된 감정: {emotion}, 나이: {age} - 디지털 문맹자 검출")
                        self.digital_literacy_detected = True
                        self.switch_to_kiosk_app()
                        # break 지우고 계속 실행

                except Exception as e:
                    continue

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        print(f"카메라 {camera_id} 얼굴 분석 종료")
        cap.release()
        cv2.destroyAllWindows()

    # WindowClass의 continuous_eye_tracking 메서드도 원래대로 복원
    def continuous_eye_tracking(self, camera_id=1):
        """눈 움직임을 추적하는 메서드"""
        cap = cv2.VideoCapture(camera_id)
        print(f"카메라 {camera_id}로 눈 추적 시작")

        if not cap.isOpened():
            print(f"카메라 {camera_id} 열기 실패, 재시도 중...")
            time.sleep(1)
            cap = cv2.VideoCapture(camera_id)  # 다시 시도
            if not cap.isOpened():
                print("카메라 열기 실패!")
                return

        # 카메라에서 해상도 가져오기
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 임계값 설정 (화면의 20%)
        horizontal_threshold = width * 0.2
        vertical_threshold = height * 0.2

        initial_positions = None
        max_horizontal_movement = 0
        max_vertical_movement = 0

        left_eye_points = []  # 왼쪽 눈 위치 저장 리스트
        right_eye_points = []  # 오른쪽 눈 위치 저장 리스트

        while True:  # 원래 코드처럼 무한 루프로 변경
            ret, frame = cap.read()
            if not ret:
                print(f"카메라 {camera_id}에서 프레임 읽기 실패, 재시도 중...")
                cap.release()
                time.sleep(1)  # 잠시 대기
                cap = cv2.VideoCapture(camera_id)  # 카메라 다시 열기
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)

            for face in faces:
                landmarks = predictor(gray, face)
                left_eye_center = (landmarks.part(36).x + landmarks.part(39).x) // 2, \
                                  (landmarks.part(36).y + landmarks.part(39).y) // 2
                right_eye_center = (landmarks.part(42).x + landmarks.part(45).x) // 2, \
                                   (landmarks.part(42).y + landmarks.part(45).y) // 2

                if initial_positions is None:
                    initial_positions = (left_eye_center, right_eye_center)
                    continue

                left_eye_movement_horizontal = abs(left_eye_center[0] - initial_positions[0][0])
                right_eye_movement_horizontal = abs(right_eye_center[0] - initial_positions[1][0])
                left_eye_movement_vertical = abs(left_eye_center[1] - initial_positions[0][1])
                right_eye_movement_vertical = abs(right_eye_center[1] - initial_positions[1][1])

                # 최대 이동 거리 업데이트
                max_horizontal_movement = max(max_horizontal_movement, left_eye_movement_horizontal,
                                              right_eye_movement_horizontal)
                max_vertical_movement = max(max_vertical_movement, left_eye_movement_vertical,
                                            right_eye_movement_vertical)

                left_eye_points.append(left_eye_center)
                right_eye_points.append(right_eye_center)

                for i in range(1, len(left_eye_points)):
                    cv2.line(frame, left_eye_points[i - 1], left_eye_points[i], (255, 0, 0), 1)
                for i in range(1, len(right_eye_points)):
                    cv2.line(frame, right_eye_points[i - 1], right_eye_points[i], (0, 255, 0), 1)

                cv2.circle(frame, left_eye_center, 2, (0, 255, 0), -1)
                cv2.circle(frame, right_eye_center, 2, (255, 0, 0), -1)

                if max_horizontal_movement > horizontal_threshold or max_vertical_movement > vertical_threshold:
                    print(f"카메라 {camera_id}: 큰 눈 움직임 감지 - 디지털 문맹자 검출")
                    self.digital_literacy_detected = True
                    self.switch_to_kiosk_app()
                    cap.release()
                    cv2.destroyAllWindows()
                    return

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        print(f"카메라 {camera_id} 눈 추적 종료")
        cap.release()
        cv2.destroyAllWindows()

    def switch_to_kiosk_app(self):
        """디지털 문맹자 감지 시 1번 UI를 종료하고 2번 UI를 실행"""
        self.hide()  # 현재 창 숨기기

        # 전역 변수로 main_app에 현재 인스턴스 저장
        global main_app
        main_app = self

        self.kiosk_app = KioskApp()
        self.kiosk_app.mainloop()
    def resetDigitalLiteracyStatus(self):
        """디지털 문맹자 검사 상태 초기화"""
        self.digital_literacy_detected = False
        # 필요한 경우 추가적인 상태 초기화 로직 구현

    def startDigitalLiteracyAnalysis(self):
        """디지털 문맹자 검사 시작, 이미 시작된 경우 중복 시작 방지"""
        self.digital_literacy_analysis_active = True
        threading.Thread(target=self.continuous_face_analysis, args=(0,), daemon=True).start()
        threading.Thread(target=self.continuous_eye_tracking, args=(1,), daemon=True).start()

    def activateDigitalLiteracyDetection(self):
        """디지털 문맹자 판별 기능을 활성화하고 45초 동안 유지"""
        self.digital_literacy_detection_active = True
        self.detection_timer.start(45000)

    def deactivateDigitalLiteracyDetection(self):
        """디지털 문맹자 판별 기능을 비활성화"""
        self.digital_literacy_detection_active = False

    def resetDigitalLiteracyStatus(self):
        """디지털 문맹자 검사 상태 초기화 및 재시작"""
        self.initDigitalLiteracyAnalysis()

    def resetDigitalLiteracyStatusAfterPayment(self):
        """결제 후 디지털 문맹자 검사 상태 초기화 및 재시작"""
        self.initDigitalLiteracyAnalysis()


    def askRcpt(self):
        """영수증 물어보는 함수로 이동"""

        # 만약 결제 전이라면 이동하지 않음
        try:
            card_num = self.table_widget_qr_code.item(0, 0).text()
        except AttributeError:
            card_num = ''

        if len(card_num) > 0:
            msg_box_page = MSG_Dialog(self, 8)
            msg_box_page.exec_()
            # 영수증 처리 후 창 활성화
            self.showMaximized()
            self.activateWindow()
            self.raise_()
        self.initDigitalLiteracyAnalysis()

    def check_discount_and_move(self):
        d_price = self.get_discount_price()  # 할인금액
        t_price = self.get_total_price()  # 총 금액
        self.r_price = t_price - d_price  # 총금액 - 할인금액 = 사용자의결제금액
        self.total_payment_price.setText(f'  주문금액: {str(t_price)}원 - 할인금액:{str(d_price)}원')
        self.total_payment_price_2.setText(f'  결제금액: {str(self.r_price)}원')
        self.payment_choose_title_bar.setText(f'    결제수단 선택({str(self.r_price)})원')
        self.stackedWidget.setCurrentWidget(self.payment_choose_page)

    def mobile_pay_msgbox(self):
        """모바일 페이 메세지박스 띄우기"""
        msg_box_page = MSG_Dialog(self, 3)
        msg_box_page.exec_()

    def set_table_widget(self, tablewidget, row, column, labels):
        """큐알코드 테이블 위젯 값 설정하기"""
        self.table_widget_qr_code.setRowCount(row)  # 행 갯수 설정
        self.table_widget_qr_code.setColumnCount(column)  # 열 갯수 설정
        self.table_widget_qr_code.setVerticalHeaderLabels(labels)  # 행 제목 설정
        self.table_widget_qr_code.horizontalHeader().setVisible(False)  # 열 헤더 숨기기
        self.table_widget_qr_code.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        if self.barcode_type == 'qr_payment':
            print(self.get_total_price())
            print(self.get_discount_price())
            self.table_widget_qr_code.setItem(4, 0, QtWidgets.QTableWidgetItem(
                f"{str(int(self.get_total_price()) -self.get_discount_price())}원"))

    def change_card_num(self):
        """큐알코드 선택창에서 키패드 번호 입력"""

        # 사용자가 누른 키패드 번호 받아옴
        sender_name = self.sender().text()
        print('사용자가 누른 번호', sender_name)
        if self.barcode_type == 'kt_discount':
            card_num_row = 3
        if self.barcode_type == 'qr_payment':
            card_num_row = 2
        else:
            card_num_row = 1

        self.insert_value_in_tablewidget(self.table_widget_qr_code, sender_name, card_num_row)

    def insert_value_in_tablewidget(self, tablewidget, sender_obj, card_row):

        # 키패드 번호 리스트에 저장
        keypad_numbers = [str(num) for num in range(10)]
        keypad_numbers.extend(['00', '000'])

        # 현재 테이블위젯에 있는 카드번호
        try:
            card_num = tablewidget.item(card_row, 0).text()
        except AttributeError:
            card_num = ''
        string = (card_num + sender_obj).replace('-', '')
        print('카드번호는', card_num)

        # 테이블 위젯에 조건에 따라 값 넣어줌
        if sender_obj in keypad_numbers and len(string) <= 16:  # 키패드 리스트에 값이 있다면(0~9, 00, 000)
            string = (card_num + sender_obj).replace('-', '')
            divided_4_letter = '-'.join([string[i:i + 4] for i in range(0, len(string), 4)])
            tablewidget.setItem(card_row, 0, QtWidgets.QTableWidgetItem(divided_4_letter))  # 카드 번호 위치에 값 넣어줌
            # tablewidget.item(card_row, 0).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)  # 값 오른쪽 정렬
        elif sender_obj == 'clear':
            tablewidget.setItem(card_row, 0, QtWidgets.QTableWidgetItem(''))  # clear 되었을 때 값 넣어주기
        elif sender_obj == '승인':
            if card_num.replace('-', '') == '1111222233334444':
                if self.barcode_type == 'kt_discount':
                    kt_info = ['KT할인', '특정할인', '20230601 ~ 20230930', card_num, str(self.get_total_price()) + '원',
                               str(self.get_discount_price()) + '원']
                    self.set_number_in_qr_payment_table(6, kt_info)
                if self.barcode_type == 'qr_payment':
                    coupon_info = [str(self.get_total_price() - self.get_discount_price()) + '원', str(randint(1, 3)), card_num]
                    self.set_number_in_qr_payment_table(3, coupon_info)
            else:
                msg_box_page = MSG_Dialog(self, 6)  # 유효한 카드번호가 아닙니다. 다시 입력하세요.
                msg_box_page.exec_()
        elif sender_obj == '←':
            card_num = card_num[:-1]
            tablewidget.setItem(card_row, 0, QtWidgets.QTableWidgetItem(card_num))  # 하나 줄여서 값 넣어주기
            tablewidget.item(card_row, 0).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)  # 값 오른쪽 정렬
        else:
            pass

    def set_number_in_qr_payment_table(self, num, value):
        """qr/바코드 창에 값 넣어줌"""
        print('바코드 창 탑니다..')
        nums = [n for n in range(num)]
        for i in nums:
            self.table_widget_qr_code.setItem(nums[i], 0, QtWidgets.QTableWidgetItem(value[i]))

    def get_discount_price(self):
        """할인된 금액 리턴"""
        con = sqlite3.connect('./data/data.db')
        order_df = pd.read_sql('select * from order_table', con)
        if self.barcode_type == 'kt_discount':
            order_df.loc[0, 'discount_price'] = 1900

        order_df.to_sql('order_table', con, if_exists='replace', index=False)
        con.commit()
        con.close()
        discount_p = order_df.loc[0, 'discount_price']
        if discount_p == None:
            discount_p = 0

        return discount_p

    '''결제수단 선택창 관련 함수'''

    def payment_choose_signal(self):
        """결제수단 버튼에 따라 다른 정보 전달"""
        payment_btn_df = pd.read_csv('./data/payment_choose.csv')  # csv 값 가져오기(결제버튼 정보)
        payment_choose_buttons = self.payment_choose_main_widget.findChildren(QPushButton)  # 결제창에 있는 모든 버튼 가져오기
        for btn in payment_choose_buttons:
            con1 = payment_btn_df['btn_name'] == btn.objectName()  # 버튼객체이름과 같은 버튼이라는 조건에 맞다면
            crs_btn = payment_btn_df.loc[con1, ['kor_name', 'type']].to_dict('list')  # 버튼 이름과 결제형태 딕셔너리 형식으로 가져오기
            btn.clicked.connect(lambda x, y=crs_btn['kor_name'][0], z=crs_btn['type'][0]: self.move_to_payment_page(y, z))

    def move_to_payment_page(self, name, type):
        """전달해준 정보에 따라 다른 결제창 불러오기"""
        print('타입', type)
        print('kt할인여부', self.kt_discount)

        # 카드 결제창 이동
        if type == 1:  # 카드
            self.payment_card_title_bar.setText("  " + name)
            self.stackedWidget.setCurrentWidget(self.charge_page)
            self.update_card_payment_table()

        elif type == 2 or (type == 3 and not self.kt_discount) or type == 4:  # qr/바코드 창으로 이동
            self.move_to_payment_page_for_qr(name, type)
        else:
            msg_box_page = MSG_Dialog(self, 7)
            msg_box_page.exec_()

    def move_to_payment_page_for_qr(self, name, type):
        """선택한 버튼에 따라 맞는 결제창으로 이동"""
        self.table_widget_qr_code.clearContents()  # 테이블 위젯 지우기
        self.table_widget_qr_code.setRowCount(0)

        if type == 2:  # 쿠폰 조회창
            self.qr_check_btns_stackwidget.setCurrentWidget(self.coupon_check_btn)
            lab = ['쿠폰번호', '쿠폰명칭', '잔여금액', '받을금액', '결제금액']
            self.barcode_type = 'coupon_payment'

        if type == 4:  # qr/바코드 결제창 이동
            self.qr_check_btns_stackwidget.setCurrentWidget(self.coupon_check_btn)
            lab = ['총 결제금액', '할부개월', '카드번호']
            self.barcode_type = 'qr_payment'

        else:  # kt 할인창 이동
            self.qr_check_btns_stackwidget.setCurrentWidget(self.kt_check_btn)
            lab = ['제휴사명', '할인종료', '유효기간', '카드번호', '대상금액', '할인금액']
            self.barcode_type = 'kt_discount'
            self.kt_discount = True

        self.set_table_widget(self.table_widget_qr_code, len(lab), 1, lab)  # 테이블에 값 넣어주기
        self.barcord_payment_title_bar.setText("  " + name)  # 창 상단의 이름 바꾸기
        self.stackedWidget.setCurrentWidget(self.barcod_payment_page)  # qr/바코드 페이지로 이동

    def get_total_price(self):
        """총 가격 계산 및 반환"""
        con = sqlite3.connect('./data/data.db')
        order_table_df = pd.read_sql('select * from order_table', con)

        # 총 가격 계산
        order_table_df['drink_cnt'] = order_table_df['drink_cnt'].astype(int)
        order_table_df['price'] = order_table_df['price'].astype(int)
        total_price = (order_table_df['drink_cnt'] * order_table_df['price']).sum()
        return total_price

    def get_total_cnt(self):
        """총 갯수 계산 및 반환"""
        con = sqlite3.connect('./data/data.db')
        order_table_df = pd.read_sql('select * from order_table', con)
        total_count = order_table_df['drink_cnt'].sum()
        return total_count

    def update_card_payment_table(self):
        """카드 결제창 테이블 위젯 값 업데이트"""
        total_price = self.get_total_price()  # 총 가격
        discount_price = self.get_discount_price()
        f_price = total_price - discount_price

        # 카드번호 랜덤으로 만들어줄것
        card_num = self.make_random_card_num()

        # 카드 테이블에 값 업데이트 해주기
        self.card_payment_table_widget.setRowCount(3)
        self.card_payment_table_widget.setColumnCount(1)
        self.card_payment_table_widget.horizontalHeader().setVisible(False)  # 열 헤더를 숨깁니다.
        self.card_payment_table_widget.setItem(0, 0, QtWidgets.QTableWidgetItem(str(f_price) + '원'))
        self.card_payment_table_widget.setItem(1, 0, QtWidgets.QTableWidgetItem('0개월'))
        self.card_payment_table_widget.setItem(2, 0, QtWidgets.QTableWidgetItem(card_num))
        self.card_payment_table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 열 너비를 조정합니다.

    def make_random_card_num(self):
        """카드 번호 랜덤으로 만들어주기"""
        random_card_num = [str(randint(1000, 9999)) for _ in range(4)]
        random_card_num_for_print = ' '.join(random_card_num)
        mask_card_num = "*" * (len(random_card_num_for_print) - 4) + random_card_num_for_print[-4:]
        return mask_card_num

    '''주문 확인창 관련 함수'''
    def insert_img_for_recommend(self):
        """추천 디저트 메뉴 5개 넣음"""
        menu_and_price_join_df = pd.merge(self.menu_df, self.img_path_df, on='id')  # 조인
        con1 = (menu_and_price_join_df['category'] == '디저트')

    def move_to_payment_choose(self, state):
        """포장/매장 선택하는 것 db에 저장해주기"""
        con = sqlite3.connect('./data/data.db')
        order_table_df = pd.read_sql('select * from order_table', con)
        order_table_df.loc[:, 'for_here_or_to_go'] = state
        order_table_df.to_sql('order_table', con, if_exists='replace', index=False)
        con.commit()
        con.close()
        self.stackedWidget.setCurrentWidget(self.payment_choose_page)

    def timer_restart_and_go_to_main_page(self):
        """타이머 재시작 및 메인 페이지로 이동"""
        self.timer.start()
        self.stackedWidget.setCurrentWidget(self.main_page)

    def fill_the_table_widget(self, table):
        """테이블 위젯 채우기"""
        # 업데이트한 db불러오기
        con = sqlite3.connect('./data/data.db')
        order_table_df = pd.read_sql('select * from order_table', con)
        price_df = pd.read_csv('./data/drinks_price.csv')  # 가격 csv 도 불러오기(한글이름으로 비교)

        # 테이블위젯 행 값 계산
        row = order_table_df['id'].count()
        table.setRowCount(row)  # 행값 적용

        # 옵션 값 딕셔너리 화 하기
        order_table_dict = pd.DataFrame(order_table_df).to_dict()

        # 테이블위젯 값 생성하고 넣기
        for idx in range(row):
            # 테이블위젯 값 생성
            drink_option_df = order_table_df.loc[idx, 'custom_option']  # 각 행의 옵션을 가져와서
            drink_option_list = ast.literal_eval(drink_option_df)  # 문자열로 되어 있는 리스트들을 리스트처럼 만들어줌
            option_choices_no_choice = [price_df[price_df['eng_name'] == i]['kor_name'].to_string(index=False)
                                        # 그리고 not choice가 써져 있지 않은 값들을 리스트에 넣어줌
                                        for i in drink_option_list if 'no_choice' not in i]

            # 값 넣기
            items = [QTableWidgetItem(str(order_table_dict[col][idx])) for col in ['order_drink', 'drink_cnt', 'price']]
            items.append(QTableWidgetItem(','.join(option_choices_no_choice)))

            # 테이블 위젯 가운데로 정렬
            for item in items:
                item.setTextAlignment(Qt.AlignCenter)  # Qt.AlignHCenter 가운데로 정렬

            # 테이블위젯에 값 넣기
            for col, item in enumerate(items):
                table.setItem(idx, col, item)

        # 테이블위젯 열 길이 헤더 크기만큼 정렬해주기
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

    def move_to_order_check_page(self):
        """주문확인창"""
        # 타이머 중단
        self.timer.stop()

        # 현재 db 연결
        con = sqlite3.connect('./data/data.db')
        order_table_df = pd.read_sql('select * from order_table', con)

        total_price = self.get_total_price()  # 총 가격 계산
        total_count = order_table_df['drink_cnt'].sum()  # 총 갯수 계산
        discount_price = order_table_df['discount_price'].sum()  # 할인금 계산

        # 라벨 및 버튼에 넣어주기
        self.total_price_for_check_page.setText(str(total_price) + '원')
        self.payment_choose_title_bar.setText(f'  결제수단 선택({str(int(total_price) - int(discount_price))}원)')  # 이건 결제수단 선택창임
        self.total_payment_price.setText(f'  주문금액: {str(total_price)}원 - 할인금액:{str(discount_price)}원')  # 이건 결제수단 선택창임
        self.total_payment_price_2.setText(f'  결제금액: {str(total_price)}원')  # 이건 결제수단 선택창임
        self.total_cnt_for_check_page.setText(str(total_count) + '개')

        # 총 갯수가 0 초과하면 창 넘어가기
        if total_count > 0:
            self.stackedWidget.setCurrentWidget(self.order_check_page)  # 주문 확인 창으로 이동
            self.fill_the_table_widget(self.tableWidget_menu_check)  # 테이블위젯 값 채우기
            self.fill_the_table_widget(self.tableWidget_menu_2_for_qr)  # 일단 여기에 넣음 @@@@@@@@@@@@@@@@@@@ 수정필요
        else:
            msg_box_page = MSG_Dialog(self, 2)  # 1보다 작으면 메세지 창 띄우기
            msg_box_page.exec_()

    '''메인창 관련 함수'''

    def check_current_page(self, num):
        if num == 1:
            self.category_stackedWidget.setCurrentWidget(self.category_2)
            self.category_btn_11.click()
        elif num == 2:
            self.category_stackedWidget.setCurrentWidget(self.category_1)
            self.category_btn_1.click()
        self.menu_stackedWidget.setCurrentWidget(self.page_1)

    def delete_order_table_values(self):
        """ 주문 값 삭제"""

        # 리스트 위젯 값 삭제
        self.drinks_cart_list_widget.clear()

        conn = sqlite3.connect('./data/data.db')  # 데이터베이스 연결 정보 설정
        cur = conn.cursor()  # 커서 생성
        cur.execute("DELETE FROM 'order_table'")  # SQL 쿼리 실행

        cur.execute("SELECT SUM(drink_cnt) FROM 'order_table'")
        result = cur.fetchone()[0]
        if result == None:
            result = 0
        self.menu_cnt_label.setText(str(result) + '개')

        order_df = pd.read_sql('select * from order_table', conn)
        order_df['drink_cnt'] = order_df['drink_cnt'].astype(int)
        order_df['price'] = order_df['price'].astype(int)
        total_price = (order_df['drink_cnt'] * order_df['price']).sum()
        self.payment_admit_btn.setText(f'  {str(total_price)}원\n  결제하기')

        conn.commit()  # 변경사항 저장
        cur.close()  # 연결 종료
        conn.close()

    def start_timer(self, category):
        """타이머 시작하는 함수"""
        self.timer.stop()
        self.remaining_time = self.DURATION_INT
        self.timer.start()

    def update_timer(self):
        """타이머 시간 업데이트"""
        if self.stackedWidget.currentWidget() == self.main_page:  # 메인페이지에서만 구동함
            self.remaining_time -= 1
            if self.remaining_time == 0:
                self.remaining_time = self.DURATION_INT
                self.stackedWidget.setCurrentWidget(self.main_page)
            self.timer_label.setText(f"{str(self.remaining_time)}초")
        else:
            pass

    def click_frame(self, event, name):
        """메뉴 선택하고 선택옵션 창 띄우기"""
        # print(f'{name}프레임을 선택했습니다.')
        option_page_df = pd.merge(self.menu_df, self.img_path_df, on='id')
        print(option_page_df.columns)

        # 조건설정
        condition1 = (option_page_df['category'] == self.user_clicked_category)
        condition2 = (option_page_df['category_num'] == int(name[11:]))

        # 조건에 맞는 변수이름에 저장
        sold_out_state = option_page_df.loc[condition1 & condition2, 'sold_out']
        self.send_info = option_page_df.loc[condition1 & condition2]
        print(self.send_info['info'])
        if sold_out_state.sum() > 0:
            msg_box_page = MSG_Dialog(self, 1)
            msg_box_page.exec_()
        else:
            self.show_sample_label()
            dialog_page = Option_Class(self)
            dialog_page.show()

        self.send_info = option_page_df.loc[condition1 & condition2]
        drink_name = self.send_info['menu_name_x'].to_string(index=False)

        # 디지털 문맹자가 감지된 경우, 메뉴 이름 TTS로 읽어주기
        if self.digital_literacy_detected:
            self.tts_engine.say(drink_name)
            self.tts_engine.runAndWait()

    def remove_label(self):
        """선택옵션창 뒤에 검은 화면 숨겨줌"""
        self.sample_label.hide()

    def show_sample_label(self):
        """임시 검은 라벨 띄우기"""
        self.sample_label = QLabel(self)
        self.sample_label.setGeometry(0, 0, 768, 1024)
        self.sample_label.setStyleSheet('background-color: rgba(45,45,45,200);')
        self.sample_label.show()

    def show_menu_arrow_btn(self):
        """카테고리 개수에 따라 메뉴 화살표상태를 변경합니다."""
        current_page = self.menu_stackedWidget.currentWidget().objectName()
        self.menu_right_btn.setVisible(current_page == 'page_1' and self.menu_arrow_btn_num == 2)
        self.menu_left_btn.setVisible(current_page == 'page_2' and self.menu_arrow_btn_num == 2)

    def set_categroy_num(self):
        """카테고리 숫자에 따라 음료 라벨 보여주기"""

        # [1] 카테고리 수 만큼 프레임 보여주기
        menu_frame_list = [getattr(self, f"menu_frame_{i}") for i in range(1, 25)]  # 담길 라벨 리스트화
        btn_name = self.sender().text()  # 버튼 이름 가져오기
        self.user_clicked_category = btn_name

        # 값 초기화
        self.connn = sqlite3.connect('./data/data.db')
        self.menu_df = pd.read_sql('select * from drinks_menu', self.connn)  # 음료상세정보 전체 테이블

        category_drinks_num = len(self.menu_df[self.menu_df['category'] == btn_name])  # 카테고리 메뉴 갯수 세기

        # 카테고리 번호만큼 프레임 보여주기
        for index, frame in enumerate(menu_frame_list):
            getattr(self, f'menu_img_{index + 1}').clear()  # 라벨 클리어 시켜주기
            getattr(self, f'menu_name_label_{index + 1}').clear()
            getattr(self, f'menu_price_label_{index + 1}').clear()
            if index + 1 <= category_drinks_num:  # 해당하는 카테고리 번호까지 프레임의 background-color 바꿔준다.
                frame.setStyleSheet('background-color: white;')
            else:
                frame.setStyleSheet('background-color: rgb(255, 204, 0);')

        self.insert_img(btn_name, category_drinks_num)

    def insert_img(self, btn_name, category_drinks_num):
        # [2] 이미지 삽입
        # 1) menu table과 img_path 테이블을 join (key = id)
        menu_and_price_join_df = pd.merge(self.menu_df, self.img_path_df, how='left', on='id')  # 조인
        con1 = (menu_and_price_join_df['category'] == btn_name)  # 버튼 번호에 맞는 조건 설정
        user_click_category_df = menu_and_price_join_df.loc[
            con1, ['id', 'category', 'category_num', 'sold_out', 'menu_name_x', 'img_path', 'price']]  # 테이블 2차 가공 원하는 열만

        # 2)이미지 열을 라벨에 입힌다. 카테고리 번호에 맞게
        con3 = user_click_category_df['sold_out'] == 1
        for i in range(1, category_drinks_num + 1):
            con2 = user_click_category_df['category_num'] == i  # 조건: 카테고리 번호가 일치해야 함

            drink_img = user_click_category_df.loc[con2, 'img_path'].values
            drink_name = user_click_category_df.loc[con2, 'menu_name_x'].values
            drink_price = user_click_category_df.loc[con2, 'price'].values
            sold_out_state = user_click_category_df.loc[con2 & con3, 'sold_out'].values

            if sold_out_state.size > 0:
                print(drink_name, '품절')
                getattr(self, f'menu_img_{i}').setPixmap(QPixmap('./img/qt자료/sold_out_3.png').scaled(175, 180, Qt.IgnoreAspectRatio))
            elif drink_img.size > 0 and drink_name.size > 0 and drink_price.size > 0:
                getattr(self, f'menu_img_{i}').setPixmap(QPixmap(drink_img[0]))
            getattr(self, f'menu_name_label_{i}').setText(str(drink_name[0]))
            getattr(self, f'menu_price_label_{i}').setText(f'{str(drink_price[0])}원')
        self.connn.close()
        if category_drinks_num > 12:
            self.menu_arrow_btn_num = 2
        else:
            self.menu_arrow_btn_num = 1

    def change_categroy_btn_color(self):
        """메인화면 상단 카테고리 버튼 색 바뀌게 함"""

        btn_object = self.sender()  # 버튼 객체 가져오기

        # 선택한 버튼 색 바꾸고 그 외의 색 바꾸기
        for btn in self.category_btn_list:
            if btn == btn_object:
                btn.setStyleSheet('''
                    background-color: rgb(45, 45, 45);
                    border: 2px solid rgb(45, 45, 45);
                    border-radius:15px; color:white; 
                    ''')
            else:
                btn.setStyleSheet('''
                    background-color: rgb(255, 204, 0);
                    border: 2px solid rgb(45, 45, 45);
                    border-radius:15px;
                    color:black;
                    ''')

    '''오프닝 페이지 관련 함수'''

    def set_ad_image(self):
        """3초에 한번씩 오픈 페이지 이미지 변하게 함"""
        self.ad_img_num = 1  # 오픈 페이지 이미지 변수 설정
        self.ad_label.setPixmap(QPixmap(f'./img/ad/ad_img_{self.ad_img_num}').scaled(QSize(768, 1024)))  # 첫번째 이미지

        # 3초 타이머 설정.
        ad_timer = QTimer(self)
        ad_timer.timeout.connect(self.change_ad_image)  # 타임아웃되면 change_ad_image 함수로 이동
        ad_timer.start(3000)

    def change_ad_image(self):
        """3초에 1번씩 이미지 변경해 줌"""
        self.ad_img_num += 1  # 이미지 변수에 1씩 더해줌
        if self.ad_img_num == 5:  # 만약 5라면
            self.ad_img_num = 1  # 1로 만들어준다

        pixmap = QPixmap(f'./img/ad/ad_img_{self.ad_img_num}')  # 사진 경로 받아오기
        self.ad_label.setPixmap(QPixmap(pixmap).scaled(QSize(768, 1024)))  # 라벨 이미지에 설정함


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = WindowClass()
    mainWindow.show()
    sys.exit(app.exec_())