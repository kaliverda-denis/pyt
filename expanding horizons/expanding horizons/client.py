import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import csv
import os

API_URL = 'http://127.0.0.1:5000'
CACHE_FILE = 'cache.csv'
FIELDNAMES = ['id', 'name', 'category', 'quantity', 'price', 'location', 'created_at']

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Розширення горизонтів - Інвентар")
        self.root.geometry("950x650")

        self.is_offline = False
        self.current_edit_id = None

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Синхронізувати зараз", command=self.force_sync)
        file_menu.add_command(label="Експорт CSV", command=self.export_csv)
        menubar.add_cascade(label="Файл", menu=file_menu)
        self.root.config(menu=menubar)

        form_frame = tk.Frame(self.root)
        form_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(form_frame, text="Назва:").grid(row=0, column=0, sticky="w")
        self.entry_name = tk.Entry(form_frame, width=20)
        self.entry_name.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(form_frame, text="Категорія:").grid(row=0, column=2, sticky="w")
        self.entry_category = tk.Entry(form_frame, width=20)
        self.entry_category.grid(row=0, column=3, padx=5, pady=2)

        tk.Label(form_frame, text="Кількість:").grid(row=1, column=0, sticky="w")
        self.entry_quantity = tk.Entry(form_frame, width=20)
        self.entry_quantity.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(form_frame, text="Ціна:").grid(row=1, column=2, sticky="w")
        self.entry_price = tk.Entry(form_frame, width=20)
        self.entry_price.grid(row=1, column=3, padx=5, pady=2)

        tk.Label(form_frame, text="Локація:").grid(row=2, column=0, sticky="w")
        self.entry_location = tk.Entry(form_frame, width=20)
        self.entry_location.grid(row=2, column=1, padx=5, pady=2)

        self.btn_save = tk.Button(form_frame, text="Додати товар", command=self.save_item, bg="lightgreen", width=20)
        self.btn_save.grid(row=2, column=2, columnspan=2, pady=10)
        
        tk.Button(form_frame, text="Очистити форму", command=self.clear_form, bg="lightgray", width=20).grid(row=3, column=2, columnspan=2)

        self.tree = ttk.Treeview(self.root, columns=FIELDNAMES, show='headings')
        for col in FIELDNAMES:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.status_var = tk.StringVar()
        self.status_var.set("Готово")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Button(btn_frame, text="Оновити список (GET)", command=self.load_data).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Видалити обране (DELETE)", command=self.delete_selected, bg="#ffcccc").pack(side=tk.LEFT, padx=10)

    def clear_form(self):
        self.current_edit_id = None
        self.entry_name.delete(0, tk.END)
        self.entry_category.delete(0, tk.END)
        self.entry_quantity.delete(0, tk.END)
        self.entry_price.delete(0, tk.END)
        self.entry_location.delete(0, tk.END)
        self.btn_save.config(text="Додати товар", bg="lightgreen")
        self.status_var.set("Форму очищено.")

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        item_values = self.tree.item(selected[0])['values']
        if not item_values or len(item_values) < 6:
            return

        self.current_edit_id = str(item_values[0])
        
        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, item_values[1])
        
        self.entry_category.delete(0, tk.END)
        self.entry_category.insert(0, item_values[2])
        
        self.entry_quantity.delete(0, tk.END)
        self.entry_quantity.insert(0, item_values[3])
        
        self.entry_price.delete(0, tk.END)
        self.entry_price.insert(0, item_values[4])
        
        self.entry_location.delete(0, tk.END)
        self.entry_location.insert(0, item_values[5])

        self.btn_save.config(text="Оновити товар", bg="yellow")
        self.status_var.set(f"Обрано товар для редагування (ID: {self.current_edit_id})")

    def save_item(self):
        item_data = {
            "name": self.entry_name.get(),
            "category": self.entry_category.get(),
            "quantity": self.entry_quantity.get(),
            "price": self.entry_price.get(),
            "location": self.entry_location.get()
        }

        if self.is_offline:
            if self.current_edit_id:
                self.status_var.set("Редагування в офлайн-режимі недоступне.")
                return
            
            items = self.read_from_cache()
            item_data['id'] = f"offline_{len(items)+1}"
            item_data['created_at'] = "offline"
            items.append(item_data)
            self.save_to_cache(items)
            self.update_table(items)
            self.status_var.set("Додано локально (офлайн).")
            self.clear_form()
            return

        try:
            if self.current_edit_id:
                response = requests.put(f'{API_URL}/items/{self.current_edit_id}', json=item_data)
                success_code = 200
                success_msg = "Товар успішно оновлено (PUT)."
            else:
                response = requests.post(f'{API_URL}/items', json=item_data)
                success_code = 201
                success_msg = "Товар успішно додано (POST)."

            if response.status_code == 400:
                error_msg = response.json().get('error', 'Невідома помилка')
                self.status_var.set(f"Помилка валідації: {error_msg}")
                messagebox.showerror("Помилка сервера", error_msg)
            elif response.status_code == success_code:
                self.status_var.set(success_msg)
                self.clear_form()
                self.load_data()

        except requests.ConnectionError:
            self.switch_to_offline_mode()
            if not self.current_edit_id:
                self.save_item()

    def load_data(self):
        try:
            response = requests.get(f'{API_URL}/items', timeout=3)
            response.raise_for_status()
            items = response.json()
            self.is_offline = False
            self.update_table(items)
            self.save_to_cache(items)
            self.status_var.set("Дані завантажено з сервера.")
        except (requests.ConnectionError, requests.Timeout):
            self.switch_to_offline_mode()
        except Exception as e:
            self.status_var.set(f"Помилка сервера: {e}")

    def switch_to_offline_mode(self):
        self.is_offline = True
        self.status_var.set("УВАГА: Сервер недоступний. Працюємо в офлайн-режимі.")
        items = self.read_from_cache()
        self.update_table(items)

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Увага", "Оберіть товар для видалення.")
            return
        
        item_id = str(self.tree.item(selected[0])['values'][0])
        
        if self.is_offline:
            self.status_var.set("Неможливо видалити на сервері в офлайн-режимі.")
            return

        if not messagebox.askyesno("Підтвердження", "Ви впевнені, що хочете видалити цей товар?"):
            return

        try:
            response = requests.delete(f'{API_URL}/items/{item_id}')
            if response.status_code == 200:
                self.status_var.set("Видалено (DELETE).")
                self.clear_form()
                self.load_data()
        except requests.ConnectionError:
            self.switch_to_offline_mode()

    def force_sync(self):
        self.status_var.set("Спроба синхронізації...")
        try:
            requests.get(f'{API_URL}/items', timeout=2)
            
            if self.is_offline:
                cache_items = self.read_from_cache()
                for item in cache_items:
                    if str(item['id']).startswith('offline_'):
                        del item['id']
                        del item['created_at']
                        requests.post(f'{API_URL}/items', json=item)
                self.status_var.set("Синхронізація успішна! Локальні дані відправлено.")
            else:
                self.status_var.set("Дані вже синхронізовані. Оновлюємо список.")
            
            self.load_data()
            
        except requests.ConnectionError:
            self.status_var.set("Помилка синхронізації: Сервер досі недоступний.")
            messagebox.showwarning("Помилка", "Немає зв'язку з сервером.")

    def export_csv(self):
        if self.is_offline:
            messagebox.showwarning("Помилка", "Експорт доступний лише при підключенні до сервера.")
            return
            
        try:
            response = requests.get(f'{API_URL}/export')
            if response.status_code == 200:
                file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
                if file_path:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    self.status_var.set("Файл успішно експортовано.")
        except requests.ConnectionError:
            self.status_var.set("Помилка: Сервер недоступний для експорту.")

    def update_table(self, items):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in items:
            self.tree.insert('', tk.END, values=[item.get(f, '') for f in FIELDNAMES])

    def save_to_cache(self, items):
        with open(CACHE_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(items)

    def read_from_cache(self):
        if not os.path.exists(CACHE_FILE):
            return []
        with open(CACHE_FILE, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()