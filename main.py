from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.window import Window
import json
import csv
from datetime import datetime
import os

# Colors
BG_BLUE = (0.1, 0.21, 0.36, 1)      # #1A365D
PANEL_BLUE = (0.17, 0.42, 0.69, 1)  # #2B6CB0
BTN_YELLOW = (0.96, 0.88, 0.37, 1)  # #F6E05E
BTN_RED = (0.9, 0.24, 0.24, 1)      # #E53E3E
TEXT_WHITE = (1, 1, 1, 1)
TEXT_BLACK = (0, 0, 0, 1)

class ColoredBoxLayout(BoxLayout):
    def __init__(self, bg_color, radius=0, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.radius = radius
        with self.canvas.before:
            Color(*self.bg_color)
            if self.radius > 0:
                self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            else:
                self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class StyledButton(Button):
    def __init__(self, bg_color, text_color, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = bg_color
        self.color = text_color
        # simple rounding
        self.background_down = ''

class InventoryApp(App):
    def build(self):
        self.title = "Aplicație Inventar"
        Window.clearcolor = BG_BLUE
        self.data_file = "session_recovery.json"
        self.admin_password = "admin"

        self.items = ["Cămașă", "Cană", "Eșarfă", "Calendar", "Pix"]
        self.payment_methods = ["Numerar", "Card"]

        self.main_layout = FloatLayout()

        self.build_user_interface()
        self.build_admin_interface()

        self.main_layout.add_widget(self.user_frame)
        return self.main_layout

    def build_user_interface(self):
        self.user_frame = ColoredBoxLayout(bg_color=BG_BLUE, orientation='vertical', padding=20, spacing=10)

        title = Label(text="Înregistrare Vânzări", font_size=32, color=BTN_YELLOW, bold=True, size_hint=(1, 0.15))
        self.user_frame.add_widget(title)

        # Item Selection
        item_layout = ColoredBoxLayout(bg_color=PANEL_BLUE, radius=15, orientation='horizontal', padding=10, size_hint=(1, 0.15))
        item_layout.add_widget(Label(text="Articol:", color=TEXT_WHITE, font_size=20, size_hint=(0.5, 1)))
        self.item_spinner = Spinner(text=self.items[0], values=self.items, background_color=BTN_YELLOW, color=TEXT_BLACK, size_hint=(0.5, 1))
        item_layout.add_widget(self.item_spinner)
        self.user_frame.add_widget(item_layout)

        # Quantity
        qty_layout = ColoredBoxLayout(bg_color=PANEL_BLUE, radius=15, orientation='horizontal', padding=10, size_hint=(1, 0.15))
        qty_layout.add_widget(Label(text="Cantitate:", color=TEXT_WHITE, font_size=20, size_hint=(0.5, 1)))
        self.qty_input = TextInput(text="1", multiline=False, input_filter='int', halign='center', font_size=20, size_hint=(0.5, 1))
        self.qty_input.bind(on_text_validate=self.save_transaction)
        qty_layout.add_widget(self.qty_input)
        self.user_frame.add_widget(qty_layout)

        # Payment Method
        pay_layout = ColoredBoxLayout(bg_color=PANEL_BLUE, radius=15, orientation='horizontal', padding=10, size_hint=(1, 0.15))
        pay_layout.add_widget(Label(text="Metodă de plată:", color=TEXT_WHITE, font_size=20, size_hint=(0.5, 1)))
        self.pay_spinner = Spinner(text=self.payment_methods[0], values=self.payment_methods, background_color=BTN_RED, color=TEXT_WHITE, size_hint=(0.5, 1))
        pay_layout.add_widget(self.pay_spinner)
        self.user_frame.add_widget(pay_layout)

        # Save Trigger (No button, bound to Enter on keyboard)
        help_label = Label(text="*Apăsați Enter (Return) pe tastatură pentru a salva*", color=BTN_YELLOW, italic=True, size_hint=(1, 0.05))
        self.user_frame.add_widget(help_label)

        # Log
        self.log_input = TextInput(text="Jurnal Tranzacții:\n", readonly=True, background_color=PANEL_BLUE, foreground_color=TEXT_WHITE, size_hint=(1, 0.3))
        self.user_frame.add_widget(self.log_input)

        # Admin Button
        admin_layout = FloatLayout(size_hint=(1, 0.05))
        admin_btn = Button(text="Acces Administrator", color=(0.5, 0.5, 0.5, 1), background_color=(0,0,0,0), size_hint=(0.3, 1), pos_hint={'right': 1, 'y': 0})
        admin_btn.bind(on_press=self.show_admin_login)
        admin_layout.add_widget(admin_btn)
        self.user_frame.add_widget(admin_layout)

    def build_admin_interface(self):
        self.admin_frame = ColoredBoxLayout(bg_color=BG_BLUE, orientation='vertical', padding=20, spacing=10)

        title = Label(text="Panou Administrator", font_size=32, color=BTN_RED, bold=True, size_hint=(1, 0.1))
        self.admin_frame.add_widget(title)

        self.data_view = TextInput(readonly=True, background_color=PANEL_BLUE, foreground_color=TEXT_WHITE, size_hint=(1, 0.7))
        self.admin_frame.add_widget(self.data_view)

        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.1))

        export_btn = StyledButton(bg_color=BTN_YELLOW, text_color=TEXT_BLACK, text="Exportă CSV", bold=True)
        export_btn.bind(on_press=self.export_csv)
        btn_layout.add_widget(export_btn)

        back_btn = StyledButton(bg_color=BTN_RED, text_color=TEXT_WHITE, text="Înapoi", bold=True)
        back_btn.bind(on_press=self.show_user_interface)
        btn_layout.add_widget(back_btn)

        self.admin_frame.add_widget(btn_layout)

        self.admin_msg_label = Label(text="", color=BTN_YELLOW, size_hint=(1, 0.1))
        self.admin_frame.add_widget(self.admin_msg_label)

    def show_user_interface(self, instance=None):
        self.main_layout.clear_widgets()
        self.main_layout.add_widget(self.user_frame)

    def show_admin_login(self, instance):
        # Very simple login flow for Kivy (usually you'd use a Popup)
        self.main_layout.clear_widgets()
        login_frame = ColoredBoxLayout(bg_color=BG_BLUE, orientation='vertical', padding=50, spacing=20)

        login_frame.add_widget(Label(text="Autentificare Administrator", color=BTN_YELLOW, font_size=24, size_hint=(1, 0.2)))

        self.pwd_input = TextInput(password=True, multiline=False, size_hint=(1, 0.2))
        login_frame.add_widget(self.pwd_input)

        btn_layout = BoxLayout(spacing=10, size_hint=(1, 0.2))
        login_btn = StyledButton(bg_color=BTN_YELLOW, text_color=TEXT_BLACK, text="Login")
        login_btn.bind(on_press=self.check_password)
        btn_layout.add_widget(login_btn)

        cancel_btn = StyledButton(bg_color=BTN_RED, text_color=TEXT_WHITE, text="Anulare")
        cancel_btn.bind(on_press=self.show_user_interface)
        btn_layout.add_widget(cancel_btn)

        login_frame.add_widget(btn_layout)

        self.login_msg = Label(text="", color=BTN_RED, size_hint=(1, 0.2))
        login_frame.add_widget(self.login_msg)

        self.main_layout.add_widget(login_frame)

    def check_password(self, instance):
        if self.pwd_input.text == self.admin_password:
            self.pwd_input.text = ""
            self.show_admin_interface()
        else:
            self.login_msg.text = "Eroare: Parolă incorectă!"

    def show_admin_interface(self):
        self.main_layout.clear_widgets()
        self.main_layout.add_widget(self.admin_frame)
        self.load_admin_data()
        self.admin_msg_label.text = ""

    def save_transaction(self, instance=None):
        item = self.item_spinner.text
        qty = self.qty_input.text
        pay = self.pay_spinner.text

        if not qty.isdigit() or int(qty) <= 0:
            self.update_log("Eroare: Cantitate invalidă!")
            return

        transaction = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "articol": item,
            "cantitate": int(qty),
            "plata": pay
        }

        # Auto-save
        transactions = []
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    transactions = json.load(f)
            except:
                pass

        transactions.append(transaction)

        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(transactions, f, ensure_ascii=False, indent=4)

        self.update_log(f"Vânzare salvată: {qty} x {item} ({pay})")
        self.qty_input.text = "1"

    def update_log(self, message):
        self.log_input.text += message + "\n"

    def load_admin_data(self):
        self.data_view.text = ""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    transactions = json.load(f)

                if not transactions:
                    self.data_view.text = "Nu există tranzacții înregistrate."
                    return

                header = f"{'Data și Ora':<20} | {'Articol':<15} | {'Cantitate':<10} | {'Metodă Plată':<15}\n"
                self.data_view.text += header
                self.data_view.text += "-" * 65 + "\n"

                for t in transactions:
                    line = f"{t['timestamp']:<20} | {t['articol']:<15} | {t['cantitate']:<10} | {t['plata']:<15}\n"
                    self.data_view.text += line
            except Exception as e:
                self.data_view.text = f"Eroare la citirea datelor: {e}"
        else:
            self.data_view.text = "Nu există tranzacții înregistrate."

    def export_csv(self, instance):
        if not os.path.exists(self.data_file):
            self.admin_msg_label.text = "Nu există date pentru export."
            return

        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                transactions = json.load(f)

            if not transactions:
                self.admin_msg_label.text = "Nu există date pentru export."
                return

            csv_filename = f"export_vanzari_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["timestamp", "articol", "cantitate", "plata"])
                writer.writeheader()
                writer.writerows(transactions)

            self.admin_msg_label.text = f"Export reușit: {csv_filename}"
        except Exception as e:
            self.admin_msg_label.text = f"Eroare la export: {e}"

if __name__ == "__main__":
    InventoryApp().run()
