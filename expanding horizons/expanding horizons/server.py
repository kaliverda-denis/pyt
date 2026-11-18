from flask import Flask, request, jsonify, send_file
import csv
import os
import uuid
from datetime import datetime

app = Flask(__name__)

DATA_DIR = 'data'
INVENTORY_FILE = os.path.join(DATA_DIR, 'inventory.csv')
FIELDNAMES = ['id', 'name', 'category', 'quantity', 'price', 'location', 'created_at']

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
if not os.path.exists(INVENTORY_FILE):
    with open(INVENTORY_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()

def read_inventory():
    items = []
    with open(INVENTORY_FILE, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append(row)
    return items

def write_inventory(items):
    with open(INVENTORY_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(items)

def validate_item_data(data, require_all=True):
    required_fields = ['name', 'category', 'quantity', 'price', 'location']
    
    if require_all:
        for field in required_fields:
            if field not in data:
                return False, f"Відсутнє поле: {field}"

    if 'quantity' in data:
        try:
            int(data['quantity'])
        except ValueError:
            return False, "Поле 'quantity' має бути цілим числом"
            
    if 'price' in data:
        try:
            float(data['price'])
        except ValueError:
            return False, "Поле 'price' має бути числом"
            
    if 'name' in data and not isinstance(data['name'], str):
        return False, "Поле 'name' має бути рядком"

    return True, None

@app.route('/items', methods=['GET'])
def get_items():
    return jsonify(read_inventory()), 200

@app.route('/items', methods=['POST'])
def add_item():
    data = request.json
    is_valid, error_msg = validate_item_data(data)
    if not is_valid:
        return jsonify({"error": error_msg}), 400

    new_item = {
        'id': str(uuid.uuid4()),
        'name': data['name'],
        'category': data['category'],
        'quantity': int(data['quantity']),
        'price': float(data['price']),
        'location': data['location'],
        'created_at': datetime.now().isoformat()
    }
    
    items = read_inventory()
    items.append(new_item)
    write_inventory(items)
    
    return jsonify(new_item), 201

@app.route('/items/<item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.json
    is_valid, error_msg = validate_item_data(data, require_all=False)
    if not is_valid:
        return jsonify({"error": error_msg}), 400

    items = read_inventory()
    for item in items:
        if item['id'] == item_id:
            for key in ['name', 'category', 'quantity', 'price', 'location']:
                if key in data:
                    item[key] = str(data[key])
            write_inventory(items)
            return jsonify(item), 200
            
    return jsonify({"error": "Товар не знайдено"}), 404

@app.route('/items/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    items = read_inventory()
    new_items = [item for item in items if item['id'] != item_id]
    
    if len(items) == len(new_items):
        return jsonify({"error": "Товар не знайдено"}), 404
        
    write_inventory(new_items)
    return jsonify({"message": "Видалено успішно"}), 200

@app.route('/export', methods=['GET'])
def export_csv():
    return send_file(INVENTORY_FILE, as_attachment=True, download_name='inventory_export.csv')

if __name__ == '__main__':
    app.run(debug=True, port=5000)