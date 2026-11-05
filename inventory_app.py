import csv
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

COLUMNS = ["id", "name", "category", "quantity", "price", "location", "created_at"]
TITLES = ["ID", "Назва", "Категорія", "Кількість", "Ціна", "Склад/полиця", "Створено"]


class CsvStorage:
    filetypes = [("CSV", "*.csv")]
    extension = ".csv"

    def load(self, path):
        items = []
        with open(path, newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                item = {c: row[c] for c in COLUMNS}
                item["quantity"] = int(item["quantity"])
                item["price"] = float(item["price"])
                items.append(item)
        return items

    def save(self, path, items):
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(items)


class App:
    def __init__(self, root):
        self.storage = CsvStorage()
        self.items = []
        self.path = None
        self.selected_id = None

        root.title("Облік товарів")
        menu = tk.Menu(root)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Відкрити...", command=self.open_file)
        file_menu.add_command(label="Зберегти", command=self.save)
        file_menu.add_command(label="Зберегти як...", command=self.save_as)
        menu.add_cascade(label="Файл", menu=file_menu)
        root.config(menu=menu)

        top = tk.Frame(root)
        top.pack(side="top", fill="x", padx=5, pady=5)
        tk.Label(top, text="Пошук:").pack(side="left")
        self.search = tk.StringVar()
        self.search.trace_add("write", self.refresh)
        tk.Entry(top, textvariable=self.search).pack(side="left", fill="x", expand=True)

        self.status = tk.Label(root, text="Готово", anchor="w", relief="sunken")
        self.status.pack(side="bottom", fill="x")

        middle = tk.Frame(root)
        middle.pack(fill="both", expand=True, padx=5)

        self.tree = ttk.Treeview(middle, columns=COLUMNS, show="headings")
        for col, title in zip(COLUMNS, TITLES):
            self.tree.heading(col, text=title)
            self.tree.column(col, width=100)
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        form = tk.Frame(middle)
        form.pack(side="right", padx=10)
        self.vars = {}
        self.entries = {}
        for col, title in list(zip(COLUMNS, TITLES))[:-1]:
            tk.Label(form, text=title).pack(anchor="w")
            self.vars[col] = tk.StringVar()
            self.entries[col] = tk.Entry(form, textvariable=self.vars[col])
            self.entries[col].pack(fill="x", pady=(0, 5))
        tk.Button(form, text="Додати", command=self.add).pack(fill="x")
        tk.Button(form, text="Оновити", command=self.update).pack(fill="x")
        tk.Button(form, text="Видалити", command=self.delete).pack(fill="x")
        tk.Button(form, text="Очистити форму", command=self.clear_form).pack(fill="x")

    def show(self, text):
        self.status.config(text=text)

    def find(self, item_id):
        for item in self.items:
            if item["id"] == item_id:
                return item

    def new_id(self):
        numbers = [int(i["id"]) for i in self.items if i["id"].isdigit()]
        return str(max(numbers, default=0) + 1)

    def refresh(self, *args):
        text = self.search.get().lower()
        rows = []
        for item in self.items:
            if text in item["name"].lower() or text in item["category"].lower():
                rows.append(item)
        self.tree.delete(*self.tree.get_children())
        for item in rows:
            self.tree.insert("", "end", iid=item["id"], values=[item[c] for c in COLUMNS])

    def on_select(self, event):
        selection = self.tree.selection()
        if selection:
            self.selected_id = selection[0]
            item = self.find(self.selected_id)
            for col in self.vars:
                self.vars[col].set(item[col])
            self.show("Обрано запис " + self.selected_id)

    def read_form(self, own_id):
        values = {col: self.vars[col].get().strip() for col in self.vars}
        errors = {}
        if values["name"] == "":
            errors["name"] = "Назва не може бути порожньою"
        if values["category"] == "":
            errors["category"] = "Категорія не може бути порожньою"
        try:
            values["quantity"] = int(values["quantity"])
            if values["quantity"] < 0:
                raise ValueError
        except ValueError:
            errors["quantity"] = "Кількість має бути цілим числом ≥ 0"
        try:
            values["price"] = float(values["price"].replace(",", "."))
            if values["price"] < 0:
                raise ValueError
        except ValueError:
            errors["price"] = "Ціна має бути числом ≥ 0"
        if values["id"] != "" and values["id"] != own_id and self.find(values["id"]):
            errors["id"] = "Такий id вже існує"

        for col, entry in self.entries.items():
            entry.config(bg="pink" if col in errors else "white")
        if errors:
            self.show(list(errors.values())[0])
            return None
        return values

    def add(self):
        item = self.read_form(None)
        if item is None:
            return
        if item["id"] == "":
            item["id"] = self.new_id()
        item["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.items.append(item)
        self.clear_form()
        self.refresh()
        self.show("Додано: " + item["name"])

    def update(self):
        old = self.find(self.selected_id)
        if old is None:
            self.show("Оберіть запис у таблиці")
            return
        item = self.read_form(old["id"])
        if item is None:
            return
        if item["id"] == "":
            item["id"] = old["id"]
        item["created_at"] = old["created_at"]
        self.items[self.items.index(old)] = item
        self.clear_form()
        self.refresh()
        self.show("Оновлено: " + item["name"])

    def delete(self):
        item = self.find(self.selected_id)
        if item is None:
            self.show("Оберіть запис у таблиці")
            return
        if messagebox.askyesno("Видалення", "Видалити «" + item["name"] + "»?"):
            self.items.remove(item)
            self.clear_form()
            self.refresh()
            self.show("Видалено: " + item["name"])

    def clear_form(self):
        for col in self.vars:
            self.vars[col].set("")
            self.entries[col].config(bg="white")
        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=self.storage.filetypes)
        if path == "":
            return
        try:
            items = self.storage.load(path)
        except Exception as error:
            messagebox.showerror("Помилка", "Не вдалося відкрити файл: " + str(error))
            return
        self.items = items
        self.path = path
        self.clear_form()
        self.refresh()
        self.show("Завантажено записів: " + str(len(items)))

    def save(self):
        if self.path is None:
            self.save_as()
            return
        try:
            self.storage.save(self.path, self.items)
        except OSError as error:
            messagebox.showerror("Помилка", "Не вдалося зберегти файл: " + str(error))
            return
        self.show("Збережено записів: " + str(len(self.items)))

    def save_as(self):
        path = filedialog.asksaveasfilename(filetypes=self.storage.filetypes,
                                            defaultextension=self.storage.extension)
        if path != "":
            self.path = path
            self.save()


root = tk.Tk()
App(root)
root.mainloop()
