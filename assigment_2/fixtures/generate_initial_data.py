import json
import random
from datetime import datetime, timedelta

def generate_random_date(start_year=2024, end_year=2025):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31, 23, 59, 59)
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)

# Existing base data
existing_data = [
    # ... (keep original 3 items, 1 PO, 1 SO)
]

# Generate 97 additional items (004-100)
items = []
for i in range(4, 101):
    item_code = f'ITEM{i:03d}'
    random_date = generate_random_date()
    created_at_str = random_date.isoformat() + 'Z'
    items.append({
        "model": "warehouse.item",
        "pk": item_code,
        "fields": {
            "name": f"Product {item_code}",
            "unit": "unit",
            "description": f"Test product {item_code}",
            "stock": 0,
            "balance": 0,
            "created_at": created_at_str,
            "updated_at": created_at_str,
            "is_deleted": False
        }
    })

# Generate 49 additional purchase orders (002-050)
purchases = []
po_date = datetime(2024, 3, 22)
for po_num in range(2, 51):
    po_code = f'PO{po_num:03d}'
    random_date = generate_random_date()
    
    # Purchase header
    purchases.append({
        "model": "warehouse.purchaseheader",
        "pk": po_code,
        "fields": {
            "date": random_date.strftime('%Y-%m-%d'),
            "description": f"Purchase order {po_code}",
            "created_at": random_date.isoformat() + 'Z',
            "updated_at": random_date.isoformat() + 'Z',
            "is_deleted": False
        }
    })
    
    # Purchase details (3-5 items per PO)
    for detail_num in range(1, 4):
        item_idx = (po_num * 3 + detail_num) % 97 + 4  # Distribute items
        purchases.append({
            "model": "warehouse.purchasedetail",
            "pk": (po_num-1)*3 + detail_num + 3,  # Continue existing PK sequence
            "fields": {
                "header": po_code,
                "item": f"ITEM{item_idx:03d}",
                "quantity": f"{(detail_num * 5):.2f}",
                "unit_price": f"{(50 + detail_num * 10):.2f}",
                "remaining_quantity": f"{(detail_num * 5):.2f}",
                "created_at": random_date.isoformat() + 'Z',
                "updated_at": random_date.isoformat() + 'Z',
                "is_deleted": False
            }
        })

# Generate 49 additional sales orders (002-050)
sales = []
so_date = datetime(2024, 3, 23)
for so_num in range(2, 51):
    so_code = f'SO{so_num:03d}'
    random_date = generate_random_date()
    
    # Sales header
    sales.append({
        "model": "warehouse.sellheader",
        "pk": so_code,
        "fields": {
            "date": random_date.strftime('%Y-%m-%d'),
            "description": f"Sales order {so_code}",
            "created_at": random_date.isoformat() + 'Z',
            "updated_at": random_date.isoformat() + 'Z',
            "is_deleted": False
        }
    })
    
    # Sales details (2-4 items per SO)
    for detail_num in range(1, 3):
        item_idx = (so_num * 2 + detail_num) % 97 + 4  # Distribute items
        sales.append({
            "model": "warehouse.selldetail",
            "pk": (so_num-1)*2 + detail_num + 2,  # Continue existing PK sequence
            "fields": {
                "header": so_code,
                "item": f"ITEM{item_idx:03d}",
                "quantity": f"{detail_num:.2f}",
                "created_at": random_date.isoformat() + 'Z',
                "updated_at": random_date.isoformat() + 'Z',
                "is_deleted": False
            }
        })

# Combine all data
full_data = existing_data + items + purchases + sales

# Write to file
with open('fixtures/initial_data.json', 'w') as f:
    json.dump(full_data, f, indent=2)