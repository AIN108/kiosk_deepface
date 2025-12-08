import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

class KioskApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.image_folder = "C:/ksitscma-sef/ksitscma-sef/background/"
        self.menu_image_folders = {
            "Coffee": "C:/ksitscma-sef/ksitscma-sef/menu/Coffee/",
            "Ade": "CC:/ksitscma-sef/ksitscma-sef/menu/Ade/",
            "Dessert": "C:/ksitscma-sef/ksitscma-sef/menu/Dessert/",
            "Tea": "C:/ksitscma-sef/ksitscma-sef/menu/Tea/"
        }
        self.title("Kiosk UI")
        self.geometry("1024x768")
        self.cart = []
        self.dine_in_takeaway = None
        self.current_image_index = 0
        self.images = [self.image_folder + "image1.jpg", self.image_folder + "image2.jpg", self.image_folder + "image3.jpg"]
        self.history = [] #history 초기화
        self.bind("2", lambda event: self.start_digital_illiterate_mode())
        self.setup_first_page()

    def setup_first_page(self):
        self.first_page_frame = tk.Frame(self)
        self.first_page_frame.pack(fill="both", expand=True)

        self.photo_labels = []
        for img_path in self.images:
            img = Image.open(img_path).resize((1920, 1080), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(self.first_page_frame, image=photo)
            label.photo = photo
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
        self.second_page_frame = tk.Frame(self)
        self.second_page_frame.pack(fill="both", expand=True)

        self.menu_categories = ["Coffee", "Tea", "Ade", "Dessert"]
        self.menu_buttons = []

        self.top_frame = tk.Frame(self.second_page_frame)
        self.top_frame.pack(side="top", fill="x")

        for category in self.menu_categories:
            button = ttk.Button(self.top_frame, text=category, command=lambda c=category: self.show_menu(c))
            button.pack(side="left", padx=10, pady=10)
            self.menu_buttons.append(button)

        self.middle_frame = tk.Frame(self.second_page_frame)
        self.middle_frame.pack(expand=True)

        self.bottom_frame = tk.Frame(self.second_page_frame)
        self.bottom_frame.pack(side="bottom", fill="x")

        self.cart_frame = tk.Frame(self.bottom_frame)
        self.cart_frame.pack(side="left", fill="both", expand=True)

        self.cart_label = tk.Label(self.cart_frame, text="Cart", font=("Arial", 12))
        self.cart_label.pack()

        self.cart_listbox = tk.Listbox(self.cart_frame, height=6)
        self.cart_listbox.bind("<Double-1>", self.confirm_delete_from_cart)
        self.cart_listbox.pack(fill="both", expand=True)

        self.cart_total_label = tk.Label(self.cart_frame, text="Total: $0.00", font=("Arial", 12))
        self.cart_total_label.pack()

        self.payment_button = ttk.Button(self.bottom_frame, text="Pay", command=self.pay)
        self.payment_button.pack(side="right", padx=10, pady=10)

        self.show_menu("Coffee")

    def start_digital_illiterate_mode(self):
        if hasattr(self, 'second_page_frame'):
            self.second_page_frame.pack_forget()
        self.history = []  # history 초기화
        self.dill_mode_frame = tk.Frame(self)
        self.dill_mode_frame.pack(fill="both", expand=True)
        self.ask_dine_in_takeaway()

    def ask_dine_in_takeaway(self):
        self.clear_dill_mode_frame()

        label = tk.Label(self.dill_mode_frame, text="매장에서 드시겠습니까, 포장해서 드시겠습니까?", font=("Arial", 16))
        label.pack(pady=20)

        dine_in_button = ttk.Button(self.dill_mode_frame, text="매장", command=lambda: self.set_dine_in_takeaway("매장"))
        dine_in_button.pack(pady=10)

        takeaway_button = ttk.Button(self.dill_mode_frame, text="포장", command=lambda: self.set_dine_in_takeaway("포장"))
        takeaway_button.pack(pady=10)

        self.add_navigation_buttons()

    def set_dine_in_takeaway(self, choice):
        self.dine_in_takeaway = choice
        self.history.append(self.ask_dine_in_takeaway)
        self.ask_menu_category()

    def ask_menu_category(self):
        self.clear_dill_mode_frame()

        label = tk.Label(self.dill_mode_frame, text="원하시는 종류를 골라주세요", font=("Arial", 16))
        label.pack(pady=20)

        for category in self.menu_categories:
            button = ttk.Button(self.dill_mode_frame, text=category, command=lambda c=category: self.ask_menu_item(c))
            button.pack(pady=10)

        self.add_navigation_buttons()

    def ask_menu_item(self, category):
        self.clear_dill_mode_frame()

        label = tk.Label(self.dill_mode_frame, text=f"{category} 중에서 고르세요", font=("Arial", 16))
        label.pack(pady=20)

        image_folder = self.menu_image_folders[category]
        self.menu_items = []
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

        for item in self.menu_items:
            button = ttk.Button(self.dill_mode_frame, text=item['name'], command=lambda item=item: self.ask_item_quantity(item))
            button.pack(pady=10)

        self.add_navigation_buttons()

    def ask_item_quantity(self, item):
        # self.dill_mode_frame이 존재하지 않으면 초기화
        if not hasattr(self, 'dill_mode_frame') or self.dill_mode_frame is None:
            self.dill_mode_frame = tk.Frame(self)
            self.dill_mode_frame.pack(fill="both", expand=True)

        self.selected_item = item
        self.selected_item['options'] = []
        self.clear_dill_mode_frame()

        label = tk.Label(self.dill_mode_frame, text=f"{item['name']}의 수량을 선택해주세요", font=("Arial", 16))
        label.pack(pady=20)

        for i in range(1, 11):
            button = ttk.Button(self.dill_mode_frame, text=str(i), command=lambda i=i: self.set_item_quantity(i))
            button.pack(pady=5)

        self.add_navigation_buttons()

    def set_item_quantity(self, quantity):
        self.selected_item['quantity'] = quantity
        self.history.append(lambda: self.ask_item_quantity(self.selected_item))  # history에 현재 상태를 추가
        self.ask_item_shot(0)

    def ask_item_shot(self, index):
        self.clear_dill_mode_frame()

        if index < self.selected_item['quantity']:
            label = tk.Label(self.dill_mode_frame, text=f"샷 추가 하시겠습니까? ({index + 1}번째)", font=("Arial", 16))
            label.pack(pady=20)

            yes_button = ttk.Button(self.dill_mode_frame, text="예", command=lambda: self.set_item_shot(True, index))
            yes_button.pack(pady=10)

            no_button = ttk.Button(self.dill_mode_frame, text="아니오", command=lambda: self.set_item_shot(False, index))
            no_button.pack(pady=10)

            self.add_navigation_buttons()
        else:
            self.ask_item_iced_hot(0)

    def set_item_shot(self, add_shot, index):
        if len(self.selected_item['options']) <= index:
            self.selected_item['options'].append({})
        self.selected_item['options'][index]['샷 추가'] = "O" if add_shot else "X"
        self.ask_item_shot(index + 1)

    def ask_item_iced_hot(self, index):
        self.clear_dill_mode_frame()

        if index < self.selected_item['quantity']:
            label = tk.Label(self.dill_mode_frame, text=f"아이스/핫 중에서 고르세요 ({index + 1}번째)", font=("Arial", 16))
            label.pack(pady=20)

            iced_button = ttk.Button(self.dill_mode_frame, text="아이스", command=lambda: self.set_item_iced_hot("아이스", index))
            iced_button.pack(pady=10)

            hot_button = ttk.Button(self.dill_mode_frame, text="핫", command=lambda: self.set_item_iced_hot("핫", index))
            hot_button.pack(pady=10)

            self.add_navigation_buttons()
        else:
            self.add_to_cart_dill()

    def set_item_iced_hot(self, iced_hot, index):
        self.selected_item['options'][index]['아이스/핫'] = iced_hot
        self.ask_item_iced_hot(index + 1)

    def add_to_cart_dill(self):
        self.cart.append(self.selected_item.copy())
        self.history.append(lambda: self.ask_item_iced_hot(0))
        self.ask_another_item()

    def ask_another_item(self):
        self.clear_dill_mode_frame()

        label = tk.Label(self.dill_mode_frame, text="다른 메뉴를 추가하시겠습니까?", font=("Arial", 16))
        label.pack(pady=20)

        yes_button = ttk.Button(self.dill_mode_frame, text="네", command=self.ask_menu_category)
        yes_button.pack(pady=10)

        no_button = ttk.Button(self.dill_mode_frame, text="아니요", command=self.finish_order)
        no_button.pack(pady=10)

        self.add_navigation_buttons()

    def finish_order(self):
        self.clear_dill_mode_frame()

        label = tk.Label(self.dill_mode_frame, text="주문을 확인해주세요.", font=("Arial", 16))
        label.pack(pady=20)

        cart_label = tk.Label(self.dill_mode_frame, text="카트", font=("Arial", 16))
        cart_label.pack(pady=10)

        self.cart_listbox = tk.Listbox(self.dill_mode_frame, font=("Arial", 16))
        self.cart_listbox.bind("<Double-1>", self.confirm_delete_from_cart)
        self.cart_listbox.pack(fill="both", expand=True, pady=10)

        self.update_cart_listbox()

        total_label = tk.Label(self.dill_mode_frame, text=f"총 금액: ${self.calculate_total():.2f}", font=("Arial", 16))
        total_label.pack(pady=10)

        finish_button = ttk.Button(self.dill_mode_frame, text="결제하기", command=self.pay)
        finish_button.pack(pady=10)

        self.add_navigation_buttons()

    def update_cart_listbox(self):
        self.cart_listbox.delete(0, tk.END)
        for item in self.cart:
            item_total = item['price'] * item['quantity']
            options_text = f"({item['quantity']}개"
            for option in item['options']:
                options_text += f", (샷 추가 {option['샷 추가']}, {option['아이스/핫']})"
            options_text += ")"
            self.cart_listbox.insert(tk.END, f"{item['name']} {options_text} - ${item_total:.2f}")
        if self.dine_in_takeaway:
            dine_takeaway_text = f"형태: {self.dine_in_takeaway}"
            self.cart_listbox.insert(tk.END, dine_takeaway_text)

    def calculate_total(self):
        total = 0.0
        for item in self.cart:
            item_total = item['price'] * item['quantity']
            for option in item['options']:
                if option.get('샷 추가') == "O":
                    item_total += 0.5
            total += item_total
        return total

    def confirm_delete_from_cart(self, event):
        selection = self.cart_listbox.curselection()
        if selection:
            index = selection[0]
            if index == self.cart_listbox.size() - 1 and self.dine_in_takeaway:
                return
            item_name = self.cart_listbox.get(index)
            answer = messagebox.askyesno("삭제 확인", f"{item_name}을(를) 삭제하시겠습니까?")
            if answer:
                del self.cart[index]
                self.update_cart_listbox()

    def show_menu(self, category):
        for widget in self.middle_frame.winfo_children():
            widget.destroy()

        image_folder = self.menu_image_folders[category]

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

        for i, item in enumerate(self.menu_items):
            frame = tk.Frame(self.middle_frame, bd=2, relief="solid")
            frame.grid(row=i // 4, column=i % 4, padx=20, pady=20, ipadx=10, ipady=10)

            img = Image.open(item['image']).resize((56, 56), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label_image = tk.Label(frame, image=photo)
            label_image.photo = photo
            label_image.pack()

            label_text = tk.Label(frame, text=f"{item['name']}\n${item['price']:.2f}", font=("Arial", 12))
            label_text.pack()

            button = ttk.Button(frame, text="Select", command=lambda item=item: self.ask_item_quantity(item))
            button.pack(pady=5)

    def pay(self):
        self.clear_dill_mode_frame()
        self.show_payment_processing()

    def show_payment_processing(self):
        processing_frame = tk.Frame(self)
        processing_frame.pack(fill="both", expand=True)

        label = tk.Label(processing_frame, text="결제 진행 중...", font=("Arial", 24))
        label.pack(expand=True)

        self.after(3000, self.reset_to_first_page)

    def reset_to_first_page(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.cart = []
        self.dine_in_takeaway = None
        self.current_image_index = 0
        self.setup_first_page()

    def clear_dill_mode_frame(self):
        if hasattr(self, 'dill_mode_frame') and self.dill_mode_frame is not None:
            for widget in self.dill_mode_frame.winfo_children():
                widget.destroy()
        else:
            print("dill_mode_frame이 정의되지 않았습니다.")

    def add_navigation_buttons(self):
        button_frame = tk.Frame(self.dill_mode_frame)
        button_frame.pack(side="bottom", fill="x")

        back_button = ttk.Button(button_frame, text="뒤로 가기", command=self.go_back)
        back_button.pack(side="left", padx=5)

        home_button = ttk.Button(button_frame, text="홈", command=self.go_home)
        home_button.pack(side="right", padx=5)

    def go_back(self):
        if self.history:
            last_function = self.history.pop()
            self.clear_dill_mode_frame()
            last_function()
        else:
            self.reset_to_first_page()

    def go_home(self):
        self.clear_dill_mode_frame()
        self.history = []  # history 초기화
        self.start_digital_illiterate_mode()

if __name__ == "__main__":
    app = KioskApp()
    app.mainloop()