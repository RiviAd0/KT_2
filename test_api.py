import requests
import pytest
import random

BASE_URL = "https://qa-internship.avito.com"

def unique_seller_id():
    return random.randint(111111, 999999)

def valid_payload(seller_id=None, **overrides):
    payload = {
        "sellerID": seller_id if seller_id is not None else unique_seller_id(),
        "name": "Test Item",
        "price": 1000,
        "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}
    }
    payload.update(overrides)
    return payload


def test_tc01_create_item_success():
    r = requests.post(f"{BASE_URL}/api/1/item", json=valid_payload())
    assert r.status_code == 200, f"Ожидался 200, получен {r.status_code}: {r.text}"
    data = r.json()
    assert "id" in data, "В ответе отсутствует поле id"
    assert data["id"] is not None, "BUG-001: id равен null"


def test_tc02_create_item_missing_name():
    payload = valid_payload()
    del payload["name"]
    r = requests.post(f"{BASE_URL}/api/1/item", json=payload)
    assert r.status_code == 400, f"Ожидался 400, получен {r.status_code}"


def test_tc03_create_item_negative_price():
    r = requests.post(f"{BASE_URL}/api/1/item", json=valid_payload(price=-100))
    assert r.status_code == 400, f"Ожидался 400, получен {r.status_code}"


def test_tc04_create_item_empty_name():
    r = requests.post(f"{BASE_URL}/api/1/item", json=valid_payload(name=""))
    assert r.status_code == 400, f"Ожидался 400, получен {r.status_code}"


def test_tc05_get_item_by_id():
    create_resp = requests.post(f"{BASE_URL}/api/1/item", json=valid_payload())
    assert create_resp.status_code == 200
    item_id = create_resp.json().get("id")
    assert item_id is not None, "BUG-001: невозможно получить id"
    r = requests.get(f"{BASE_URL}/api/1/item/{item_id}")
    assert r.status_code == 200, f"Ожидался 200, получен {r.status_code}"
    data = r.json()
    if isinstance(data, list):
        data = data[0]
    assert data.get("id") == item_id


def test_tc06_get_nonexistent_item_returns_404():
    r = requests.get(f"{BASE_URL}/api/1/item/nonexistent-id-99999")
    assert r.status_code == 404, f"BUG-002: ожидался 404, получен {r.status_code}"


def test_tc07_get_items_by_seller_id():
    seller = unique_seller_id()
    requests.post(f"{BASE_URL}/api/1/item", json=valid_payload(seller_id=seller))
    r = requests.get(f"{BASE_URL}/api/1/{seller}/item")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if len(data) > 0:
        for item in data:
            assert item.get("sellerID") == seller, \
                f"BUG-004: возвращено объявление с sellerID={item.get('sellerID')}"


def test_tc08_get_statistic():
    create_resp = requests.post(f"{BASE_URL}/api/1/item", json=valid_payload())
    assert create_resp.status_code == 200
    item_id = create_resp.json().get("id")
    assert item_id is not None, "BUG-001: id null"
    r = requests.get(f"{BASE_URL}/api/1/statistic/{item_id}")
    assert r.status_code == 200, f"Ожидался 200, получен {r.status_code}"
    data = r.json()
    if isinstance(data, list):
        data = data[0]
    assert "likes" in data or "viewCount" in data


def test_tc09_get_nonexistent_statistic_returns_404():
    r = requests.get(f"{BASE_URL}/api/1/statistic/nonexistent-id-99999")
    assert r.status_code == 404, f"BUG-003: ожидался 404, получен {r.status_code}"


def test_tc10_create_item_invalid_seller_id_range():
    r = requests.post(f"{BASE_URL}/api/1/item", json=valid_payload(seller_id=100))
    assert r.status_code == 400, f"BUG-005: ожидался 400, получен {r.status_code}"