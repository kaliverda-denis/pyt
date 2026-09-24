def process_medicines(medicines):
    for item in medicines:
        name, quantity, category, temp = item

        if type(quantity) is not int or not isinstance(temp, (float, int)) or isinstance(temp, bool):
            print(f"{name} — Помилка даних")
            continue


        match category:
            case "antibiotic":
                category_status = "Рецептурний препарат"
            case "vitamin":
                category_status = "Вільний продаж"
            case "vaccine":
                category_status = "Потребує спецзберігання"
            case _:
                category_status = "Невідома категорія"


        if temp < 5:
            temp_status = "Надто холодно"
        elif temp > 25:
            temp_status = "Надто жарко"
        else:
            temp_status = "Норма"
        print(f"{name} — {category_status}, {temp_status}")


if __name__ == "__main__":
    batch = [
        ("Амоксицилін", 10, "antibiotic", 12.0),
        ("Вітамін C", 50, "vitamin", 3.0),
        ("Вакцина від грипу", 5, "vaccine", 28.0),
        ("Сироп", 2, "syrup", 15.5),
        ("Тест помилки 1", "десять", "vitamin", 20.0),  
        ("Тест помилки 2", 5, "antibiotic", "15°C"),    
    ]

    process_medicines(batch)