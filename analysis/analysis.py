import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description="Аналіз поставок препаратів")
parser.add_argument("csv_file", nargs="?", default="supplies.csv", help="шлях до CSV (за замовчуванням supplies.csv)")
args = parser.parse_args()

df = pd.read_csv(args.csv_file)
print("Завантажено рядків:", len(df))

mean_price = np.mean(df["price_per_unit"])
median_quantity = np.median(df["quantity"])
std_price = np.std(df["price_per_unit"])
print("Середня ціна:", round(mean_price, 2))
print("Медіана кількості:", median_quantity)
print("Стандартне відхилення ціни:", round(std_price, 2))

profit = df["quantity"] * df["price_per_unit"]
profit_by_supplier = profit.groupby(df["supplier"]).sum()
best_supplier = profit_by_supplier.idxmax()
print("Постачальник з найбільшим прибутком:", best_supplier, "-", round(profit_by_supplier.max(), 2))

quantity_by_category = df.groupby("category")["quantity"].sum()
print("Кількість за категоріями:")
print(quantity_by_category)

low_supply = df[df["quantity"] < 100]
low_supply_file = "low_supply.csv"
low_supply.to_csv(low_supply_file, index=False)
print("Дефіцитних поставок:", len(low_supply), "- збережено в", low_supply_file)

df["total_price"] = df["quantity"] * df["price_per_unit"]

df_sorted = df.sort_values("total_price", ascending=False)
print("Топ-3 за total_price:")
print(df_sorted.head(3))

with open("report.txt", "w", encoding="utf-8") as f:
    f.write("ЗВІТ ПО ПОСТАВКАХ\n")
    f.write("=================\n")
    f.write(f"Вхідний файл: {args.csv_file}\n")
    f.write(f"Кількість записів: {len(df)}\n\n")
    f.write("Середні показники:\n")
    f.write(f"- середня ціна: {mean_price:.2f}\n")
    f.write(f"- медіана кількості: {median_quantity:.0f}\n")
    f.write(f"- стандартне відхилення ціни: {std_price:.2f}\n\n")
    f.write(f"Постачальник з найбільшим прибутком: {best_supplier} ({profit_by_supplier.max():.2f})\n")
    f.write(f"Файл з дефіцитними поставками (quantity < 100): {low_supply_file}\n")
print("Звіт збережено в report.txt")

quantity_by_category.plot(kind="bar")
plt.title("Кількість препаратів за категоріями")
plt.xlabel("Категорія")
plt.ylabel("Кількість")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("categories.png")
plt.show()
