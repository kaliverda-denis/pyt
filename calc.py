def calculator():
    num1 = float(input("Перше число: "))
    op = input("Операція (+, -, *, /): ")
    num2 = float(input("Друге число: "))

    if op == "+":
        result = num1 + num2
    elif op == "-":
        result = num1 - num2
    elif op == "*":
        result = num1 * num2
    elif op == "/":
        if num2 == 0:
            print("Ділення на нуль, айайай")
            return
        result = num1 / num2
    else:
        print("Шо це таке")
        return

    print(f"Результат: {result}")

calculator()