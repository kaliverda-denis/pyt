
deals = [
    ("Олена", 50, "clean"),
    ("Іван", 500, "suspicious"),
    ("Петро", 5000, "fraud"),
    ("Марія", "abc", "clean"),      
    ("Сергій", 200, "unknown"),
]

def categorize_by_sum(amount):
    if amount < 100:
        return "Дрібнота"
    elif amount < 1000:
        return "Середнячок"
    else:
        return "Великий клієнт"

def decision_by_status(status):
    match status:
        case "clean":
            return "Працювати без питань"
        case "suspicious":
            return "Перевірити документи"
        case "fraud":
            return "У чорний список"
        case _:
            return "Невідомий статус"

def process_clients(deals):
    result = []
    for name, amount, status in deals:
        
        if not isinstance(amount, (int, float)):
            category = "Фальшиві дані"
        else:
            category = categorize_by_sum(amount)

        decision = decision_by_status(status)
        result.append((name, category, decision))

    return result


clients = process_clients(deals)


for name, category, decision in clients:
    print(f"{name}: {category}, {decision}")