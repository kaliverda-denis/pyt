import tkinter as tk
from tkinter import ttk
import threading
import time
import random
import queue

class Warehouse:
    def __init__(self, name, meds, price_per_unit, use_lock=True):
        self.name = name
        self.meds = meds
        self.initial_meds = meds
        self.price_per_unit = price_per_unit
        self.lock = threading.Lock() if use_lock else None
        self.stolen_meds = 0
        self.profit = 0
        self.inject_delay = False

    def steal(self, amount):
        if random.random() < 0.2:
            return 0
        
        if self.lock:
            self.lock.acquire()
            
        try:
            if self.meds >= amount:
                if self.inject_delay:
                    time.sleep(0.001)
                self.meds -= amount
                self.stolen_meds += amount
                self.profit += amount * self.price_per_unit
                return amount
            else:
                actual_stolen = self.meds
                if self.inject_delay:
                    time.sleep(0.001)
                self.meds -= actual_stolen
                self.stolen_meds += actual_stolen
                self.profit += actual_stolen * self.price_per_unit
                return actual_stolen
        finally:
            if self.lock:
                self.lock.release()

class Runner(threading.Thread):
    def __init__(self, warehouse, thief_name, progress_queue, sleep_time):
        super().__init__()
        self.warehouse = warehouse
        self.thief_name = thief_name
        self.progress_queue = progress_queue
        self.sleep_time = sleep_time

    def run(self):
        for _ in range(10):
            amount = random.randint(10, 30)
            self.warehouse.steal(amount)
            self.progress_queue.put(1)
            if self.sleep_time > 0:
                time.sleep(random.uniform(0.1, 0.5))

class SimulationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Оцінка ризиків - Симуляція крадіжок")
        self.geometry("850x650")
        
        self.progress_queue = queue.Queue()
        self.warehouses = []
        self.runners = []
        self.progress_bars = []
        self.buttons = []
        
        self.setup_ui()
        self.create_progress_bars()

    def setup_ui(self):
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        
        btn1 = tk.Button(btn_frame, text="1. Показати 1 прогін (Безпечно)", command=lambda: self.start_simulation(True, False, 1, True, 0.2))
        btn1.pack(side=tk.LEFT, padx=5)
        self.buttons.append(btn1)
        
        btn2 = tk.Button(btn_frame, text="2. Прогнати 100 разів (Швидко)", command=lambda: self.start_simulation(True, False, 100, False, 0))
        btn2.pack(side=tk.LEFT, padx=5)
        self.buttons.append(btn2)
        
        btn3 = tk.Button(btn_frame, text="3. Зламати (Без lock)", command=lambda: self.start_simulation(False, True, 1, True, 0.2), bg="salmon")
        btn3.pack(side=tk.LEFT, padx=5)
        self.buttons.append(btn3)
        
        self.progress_frame = tk.Frame(self)
        self.progress_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.text_output = tk.Text(self, height=20)
        self.text_output.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def setup_data(self, use_lock):
        self.warehouses = []
        for i in range(1, 4):
            name = f"Склад-{i}"
            meds = random.randint(100, 300)
            price = random.uniform(10.0, 50.0)
            self.warehouses.append(Warehouse(name, meds, price, use_lock))

    def create_progress_bars(self):
        for widget in self.progress_frame.winfo_children():
            widget.destroy()
            
        self.progress_bars = []
        self.runners = []
        
        for i in range(5):
            frame = tk.Frame(self.progress_frame)
            frame.pack(fill=tk.X, pady=2)
            lbl = tk.Label(frame, text=f"Бігун {i+1}:", width=10, anchor="w")
            lbl.pack(side=tk.LEFT)
            pb = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=400, mode='determinate', maximum=10)
            pb.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.progress_bars.append(pb)

    def log(self, message):
        self.text_output.insert(tk.END, message + "\n")
        self.text_output.see(tk.END)

    def start_simulation(self, use_lock, inject_delay, iterations, visualize, sleep_time):
        for b in self.buttons:
            b.config(state=tk.DISABLED)
        self.text_output.delete(1.0, tk.END)
        
        sim_thread = threading.Thread(target=self.run_simulation_logic, args=(use_lock, inject_delay, iterations, visualize, sleep_time))
        sim_thread.start()

    def run_simulation_logic(self, use_lock, inject_delay, iterations, visualize, sleep_time):
        try:
            for iteration in range(1, iterations + 1):
                self.setup_data(use_lock)
                
                for w in self.warehouses:
                    w.inject_delay = inject_delay

                if visualize:
                    self.after(0, self.create_progress_bars)
                    for pb in self.progress_bars:
                        self.after(0, lambda p=pb: p.config(value=0))
                    while not self.progress_queue.empty():
                        self.progress_queue.get()
                
                self.runners = []
                for i in range(5):
                    warehouse = random.choice(self.warehouses)
                    runner = Runner(warehouse, f"Злодій-{i+1}", self.progress_queue, sleep_time)
                    self.runners.append(runner)

                for runner in self.runners:
                    runner.start()

                if visualize:
                    completed_tasks = 0
                    total_tasks = len(self.runners) * 10
                    runner_progress = [0] * len(self.runners)
                    
                    while completed_tasks < total_tasks:
                        self.progress_queue.get()
                        completed_tasks += 1
                        idx = completed_tasks % len(self.runners)
                        runner_progress[idx] += 1
                        self.after(0, lambda i=idx, v=runner_progress[idx]: self.progress_bars[i].config(value=v))

                for runner in self.runners:
                    runner.join()

                total_stolen = sum(w.stolen_meds for w in self.warehouses)
                total_profit = sum(w.profit for w in self.warehouses)
                
                try:
                    for w in self.warehouses:
                        assert w.meds >= 0, f"Інваріант 1 зламано: на складі '{w.name}' від'ємна кількість ({w.meds})"
                        assert w.initial_meds == w.meds + w.stolen_meds, f"Інваріант 2 зламано: на складі '{w.name}' початкова кількість ({w.initial_meds}) != залишок ({w.meds}) + вкрадено ({w.stolen_meds})"
                        
                    expected_profit = sum(w.stolen_meds * w.price_per_unit for w in self.warehouses)
                    assert abs(total_profit - expected_profit) < 0.01, "Інваріант 3 зламано: загальний прибуток не збігається"
                    
                    if visualize or iterations > 1 and iteration % 10 == 0:
                        self.log(f"[Прогін {iteration}] Успіх. Вкрадено: {total_stolen}, Прибуток: {total_profit:.2f}")
                    elif iterations == 1:
                        self.log(f"Успіх. Вкрадено: {total_stolen}, Прибуток: {total_profit:.2f}")
                        
                except AssertionError as e:
                    self.log(f"\n!!! ЗБІЙ НА ПРОГОНІ {iteration} !!!")
                    self.log(str(e))
                    if not use_lock:
                        self.log("\nВИСНОВОК: Відсутність блокування (lock) призвела до Race Condition.")
                        self.log("Потоки одночасно перевіряли кількість і списували її, що призвело до розсинхронізації даних.")
                        self.log("Штучна затримка time.sleep(0.001) дозволила іншому потоку втрутитися між перевіркою та записом.")
                    break
                
                if iterations > 1 and not visualize:
                    pass
                elif iterations > 1 and visualize:
                    time.sleep(0.05)
                
            if iterations == 100:
                self.log("\nВсі 100 прогонів пройшли успішно. Жоден інваріант не зламано.")
                
        finally:
            self.after(0, lambda: [b.config(state=tk.NORMAL) for b in self.buttons])

if __name__ == "__main__":
    app = SimulationApp()
    app.mainloop()