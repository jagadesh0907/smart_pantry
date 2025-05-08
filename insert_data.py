from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["smart_pantry"]
collection = db["stock_items"]

# Clear old data to avoid duplicates
collection.delete_many({})

items = [
    {
        "item_name": "Rice",
        "quantity": 5.0,
        "status": "Full",
        "image_url": "/static/images/rice.jpg",
        "expiry_date": "2025-06-10"
    },
    {
        "item_name": "Sugar",
        "quantity": 1.0,
        "status": "Low",
        "image_url": "/static/images/sugar.jpg",
        "expiry_date": "2025-05-12"
    },
    {
        "item_name": "Wheat Flour",
        "quantity": 2.5,
        "status": "Medium",
        "image_url": "/static/images/flour.jpg",
        "expiry_date": "2025-05-20"
    }
]

collection.insert_many(items)
print("Data inserted successfully.")
