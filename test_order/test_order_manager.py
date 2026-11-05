import math

import pytest

from order_manager import Order


def make_items():
    return [
        {"name": "a", "price": 100.0, "quantity": 2},
        {"name": "b", "price": 50.0, "quantity": 1},
        {"name": "c", "price": 10.0, "quantity": 5},
    ]


def it(price, quantity=1, name="x"):
    return {"name": name, "price": price, "quantity": quantity}



@pytest.mark.parametrize("items, expected", [
    ([], 0),
    ([it(7.5, 4)], 30),
    (make_items(), 300),
    ([it(100, 0), it(5, 2)], 10),   
    ([it(0, 9), it(5, 2)], 10),     
    ([it(0.1, 3)], 0.3),            
])
def test_total(items, expected):
    assert Order(1, items).total() == pytest.approx(expected)




@pytest.mark.parametrize("items, expected", [
    ([it(5, name="s")], "s"),
    ([it(9, name="first"), it(1), it(2)], "first"),
    ([it(1), it(2), it(99, name="last")], "last"),
    ([it(10, name="x1"), it(10, name="x2")], "x1"),        
    ([it(-5), it(-1, name="neg")], "neg"),                 
    ([it(1, 1000), it(2, 1, name="dear")], "dear"),        
])
def test_most_expensive(items, expected):
    assert Order(1, items).most_expensive()["name"] == expected


def test_most_expensive_returns_same_object():
    items = make_items()
    assert Order(1, items).most_expensive() is items[0]


def test_most_expensive_empty_raises():
    with pytest.raises(ValueError):
        Order(1, []).most_expensive()



@pytest.mark.parametrize("percent, expected", [
    (0, [100, 50, 10]),
    (10, [90, 45, 9]),
    (12.5, [87.5, 43.75, 8.75]),
    (50, [50, 25, 5]),
    (100, [0, 0, 0]),
])
def test_discount_changes_all_prices(percent, expected):
    order = Order(1, make_items())
    order.apply_discount(percent)
    assert [i["price"] for i in order.items] == pytest.approx(expected)
    assert [i["quantity"] for i in order.items] == [2, 1, 5]  

def test_discount_affects_total_and_compounds():
    order = Order(1, make_items())
    order.apply_discount(50)
    assert order.total() == pytest.approx(150)
    order.apply_discount(50)
    assert order.total() == pytest.approx(75)


def test_discount_empty_items():
    order = Order(1, [])
    order.apply_discount(50)
    assert order.items == []




@pytest.mark.parametrize("percent", [-1, -0.01, 100.01, 101, float("inf"), float("-inf"), math.nan])
def test_discount_out_of_range(percent):
    order = Order(1, make_items())
    with pytest.raises(ValueError, match="Invalid discount"):
        order.apply_discount(percent)
    assert order.items == make_items()  


def test_discount_invalid_on_empty_items():
    with pytest.raises(ValueError):
        Order(1, []).apply_discount(150)


@pytest.mark.parametrize("percent", ["10", None, [10]])
def test_discount_wrong_type(percent):
    with pytest.raises(TypeError):
        Order(1, make_items()).apply_discount(percent)


@pytest.mark.parametrize("method, args", [("total", ()), ("most_expensive", ()), ("apply_discount", (10,))])
def test_missing_price_key(method, args):
    with pytest.raises(KeyError):
        getattr(Order(1, [{"quantity": 1}]), method)(*args)



@pytest.mark.parametrize("order_id, items, expected", [
    (42, make_items(), "<Order 42: 3 items>"),
    (1, [it(1)], "<Order 1: 1 items>"),
    ("A-1", [], "<Order A-1: 0 items>"),
])
def test_repr(order_id, items, expected):
    order = Order(order_id, items)
    assert repr(order) == expected
    assert str(order) == expected
