import customtkinter as ctk
import json
import csv
from datetime import datetime
import os

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class InventoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Aplicație Inventar")
        self.geometry("700x550")

        # Artistic color palette: variants of blue, yellow, and red.
        self.bg_blue = "#1A365D"      # Dark Blue
        self.panel_blue = "#2B6CB0"   # Lighter Blue
        self.btn_yellow = "#F6E05E"   # Soft Yellow
        self.btn_yellow_h = "#D69E2E" # Darker Yellow
        self.btn_red = "#E53E3E"      # Soft Red
        self.btn_red_h = "#C53030"    # Darker Red

        self.configure(fg_color=self.bg_blue)

        self.items = ["Cămașă", "Cană", "Eșarfă", "Calendar", "Pix"]
        self.payment_methods = ["Numerar", "Card"]

        self.data_file = "session_recovery.json"
        self.admin_password = "admin" # Simple password for demonstration

        # Create a container frame
        self.main_frame = ctk.CTkFrame(self, fg_color=self.bg_blue)
        self.main_frame.pack(fill="both", expand=True)

        self.build_user_interface()
        self.build_admin_interface()

        # Show user interface by default
        self.show_user_interface()

    def build_user_interface(self):
        self.user_frame = ctk.CTkFrame(self.main_frame, fg_color=self.bg_blue)

        # Artistic Title
        title = ctk.CTkLabel(self.user_frame, text="Înregistrare Vânzări", font=ctk.CTkFont(size=24, weight="bold"), text_color=self.btn_yellow)
        title.pack(pady=(30, 20))

        # Item Selection
        item_frame = ctk.CTkFrame(self.user_frame, fg_color=self.panel_blue, corner_radius=15)
        item_frame.pack(pady=10, padx=50, fill="x")

        ctk.CTkLabel(item_frame, text="Articol:", text_color="white", font=ctk.CTkFont(size=14)).pack(side="left", padx=20, pady=15)
        self.item_var = ctk.StringVar(value=self.items[0])
        self.item_dropdown = ctk.CTkOptionMenu(item_frame, values=self.items, variable=self.item_var,
                                               fg_color=self.btn_yellow, text_color="black", button_color=self.btn_yellow_h, button_hover_color=self.btn_yellow_h,
                                               corner_radius=20)
        self.item_dropdown.pack(side="right", padx=20, pady=15)

        # Quantity
        qty_frame = ctk.CTkFrame(self.user_frame, fg_color=self.panel_blue, corner_radius=15)
        qty_frame.pack(pady=10, padx=50, fill="x")

        ctk.CTkLabel(qty_frame, text="Cantitate:", text_color="white", font=ctk.CTkFont(size=14)).pack(side="left", padx=20, pady=15)
        self.qty_var = ctk.StringVar(value="1")
        self.qty_entry = ctk.CTkEntry(qty_frame, textvariable=self.qty_var, width=140, corner_radius=20)
        self.qty_entry.pack(side="right", padx=20, pady=15)

        # Payment Method
        pay_frame = ctk.CTkFrame(self.user_frame, fg_color=self.panel_blue, corner_radius=15)
        pay_frame.pack(pady=10, padx=50, fill="x")

        ctk.CTkLabel(pay_frame, text="Metodă de plată:", text_color="white", font=ctk.CTkFont(size=14)).pack(side="left", padx=20, pady=15)
        self.pay_var = ctk.StringVar(value=self.payment_methods[0])
        self.pay_dropdown = ctk.CTkOptionMenu(pay_frame, values=self.payment_methods, variable=self.pay_var,
                                              fg_color=self.btn_red, text_color="white", button_color=self.btn_red_h, button_hover_color=self.btn_red_h,
                                              corner_radius=20)
        self.pay_dropdown.pack(side="right", padx=20, pady=15)

        # Submit Button
        self.submit_btn = ctk.CTkButton(self.user_frame, text="Salvează Tranzacția", font=ctk.CTkFont(size=16, weight="bold"),
                                        fg_color=self.btn_yellow, text_color="black", hover_color=self.btn_yellow_h,
                                        corner_radius=25, height=45, command=self.save_transaction)
        self.submit_btn.pack(pady=30)

        # Last sold item info label
        self.last_sold_label = ctk.CTkLabel(self.user_frame, text="Nicio tranzacție recentă.", text_color="white", font=ctk.CTkFont(size=12, slant="italic"))
        self.last_sold_label.pack(pady=5)

        # Inconspicuous Admin Button
        self.admin_btn = ctk.CTkButton(self.user_frame, text="Acces Administrator", font=ctk.CTkFont(size=10),
                                       fg_color="transparent", text_color="gray", hover_color=self.bg_blue,
                                       command=self.show_admin_login)
        self.admin_btn.place(relx=0.98, rely=0.98, anchor="se")

    def build_admin_interface(self):
        self.admin_frame = ctk.CTkFrame(self.main_frame, fg_color=self.bg_blue)

        title = ctk.CTkLabel(self.admin_frame, text="Panou Administrator", font=ctk.CTkFont(size=24, weight="bold"), text_color=self.btn_red)
        title.pack(pady=(30, 20))

        # Data View Textbox (Rounded via CTkTextbox)
        self.data_view = ctk.CTkTextbox(self.admin_frame, width=600, height=300, corner_radius=15, fg_color=self.panel_blue, text_color="white")
        self.data_view.pack(pady=10)

        btn_frame = ctk.CTkFrame(self.admin_frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        self.export_btn = ctk.CTkButton(btn_frame, text="Exportă CSV", font=ctk.CTkFont(size=14, weight="bold"),
                                        fg_color=self.btn_yellow, text_color="black", hover_color=self.btn_yellow_h,
                                        corner_radius=20, command=self.export_csv)
        self.export_btn.pack(side="left", padx=20)

        self.back_btn = ctk.CTkButton(btn_frame, text="Înapoi", font=ctk.CTkFont(size=14, weight="bold"),
                                      fg_color=self.btn_red, text_color="white", hover_color=self.btn_red_h,
                                      corner_radius=20, command=self.show_user_interface)
        self.back_btn.pack(side="right", padx=20)

        self.admin_msg_label = ctk.CTkLabel(self.admin_frame, text="", text_color=self.btn_yellow, font=ctk.CTkFont(size=12))
        self.admin_msg_label.pack(pady=5)

    def show_user_interface(self):
        self.admin_frame.pack_forget()
        self.user_frame.pack(fill="both", expand=True)

    def show_admin_interface(self):
        self.user_frame.pack_forget()
        self.admin_frame.pack(fill="both", expand=True)
        self.load_admin_data()
        self.admin_msg_label.configure(text="")

    def show_admin_login(self):
        dialog = ctk.CTkInputDialog(text="Introduceți parola:", title="Autentificare Administrator")
        # Center dialog roughly
        password = dialog.get_input()
        if password == self.admin_password:
            self.show_admin_interface()
        elif password is not None:
            self.last_sold_label.configure(text="Eroare: Parolă incorectă!", text_color=self.btn_red)

    def save_transaction(self):
        item = self.item_var.get()
        qty = self.qty_var.get()
        pay = self.pay_var.get()

        if not qty.isdigit() or int(qty) <= 0:
            self.last_sold_label.configure(text="Eroare: Cantitate invalidă!", text_color=self.btn_red)
            return

        transaction = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "articol": item,
            "cantitate": int(qty),
            "plata": pay
        }

        # Auto-save (Failsafe)
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

        self.last_sold_label.configure(text=f"Ultima vânzare: {qty} x {item} ({pay})", text_color=self.btn_yellow)
        self.qty_var.set("1") # Reset quantity

    def load_admin_data(self):
        self.data_view.delete("1.0", "end")
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    transactions = json.load(f)

                if not transactions:
                    self.data_view.insert("end", "Nu există tranzacții înregistrate.")
                    return

                header = f"{'Data și Ora':<20} | {'Articol':<15} | {'Cantitate':<10} | {'Metodă Plată':<15}\n"
                self.data_view.insert("end", header)
                self.data_view.insert("end", "-" * 65 + "\n")

                for t in transactions:
                    line = f"{t['timestamp']:<20} | {t['articol']:<15} | {t['cantitate']:<10} | {t['plata']:<15}\n"
                    self.data_view.insert("end", line)
            except Exception as e:
                self.data_view.insert("end", f"Eroare la citirea datelor: {e}")
        else:
            self.data_view.insert("end", "Nu există tranzacții înregistrate.")

    def export_csv(self):
        if not os.path.exists(self.data_file):
            self.admin_msg_label.configure(text="Nu există date pentru export.")
            return

        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                transactions = json.load(f)

            if not transactions:
                self.admin_msg_label.configure(text="Nu există date pentru export.")
                return

            csv_filename = f"export_vanzari_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["timestamp", "articol", "cantitate", "plata"])
                writer.writeheader()
                writer.writerows(transactions)

            self.admin_msg_label.configure(text=f"Export reușit: {csv_filename}")
        except Exception as e:
            self.admin_msg_label.configure(text=f"Eroare la export: {e}")

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()
