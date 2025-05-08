from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import csv
from flask import Response

app = Flask(__name__)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["smart_pantry"]
collection = db["items"]

# ✅ Calculate days left from expiry date
def calculate_days_left(expiry_date_str):
    expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d")
    days_left = (expiry_date - datetime.now()).days
    return days_left

# ✅ Automatically determine status based on quantity
def get_status(quantity):
    if quantity > 3.0:
        return "Full"
    elif quantity >= 1.0:
        return "Medium"
    else:
        return "Low"

@app.route("/", methods=["GET"])
def index():
    search_query = request.args.get("q", "")
    status_filter = request.args.get("status", "")
    sort_by = request.args.get("sort", "")

    query = {}
    if search_query:
        query["item_name"] = {"$regex": search_query, "$options": "i"}
    if status_filter:
        query["status"] = status_filter

    # ✅ Default to expiry sorting
    if sort_by == "quantity":
        sort_option = [("quantity", -1)]
    else:
        sort_option = [("expiry_date", 1)]

    items = list(collection.find(query).sort(sort_option))

    for item in items:
        item["days_left"] = calculate_days_left(item["expiry_date"])

    return render_template("index.html", items=items, search_query=search_query, status_filter=status_filter, sort_by=sort_by)

@app.route("/add", methods=["GET", "POST"])
def add_item():
    if request.method == "POST":
        quantity = float(request.form["quantity"])
        data = {
            "item_name": request.form["item_name"],
            "quantity": quantity,
            "status": get_status(quantity),
            "expiry_date": request.form["expiry_date"],
            "image_url": request.form["image_url"]
        }
        collection.insert_one(data)
        return redirect("/")
    return render_template("add_item.html")

@app.route("/edit/<id>", methods=["GET", "POST"])
def edit_item(id):
    item = collection.find_one({"_id": ObjectId(id)})
    if request.method == "POST":
        quantity = float(request.form["quantity"])
        updated_data = {
            "item_name": request.form["item_name"],
            "quantity": quantity,
            "status": get_status(quantity),
            "expiry_date": request.form["expiry_date"],
            "image_url": request.form["image_url"]
        }
        collection.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
        return redirect("/")
    return render_template("edit_item.html", item=item)

@app.route("/delete/<id>")
def delete_item(id):
    collection.delete_one({"_id": ObjectId(id)})
    return redirect("/")

@app.route("/export")
def export_csv():
    items = list(collection.find())
    for item in items:
        item["days_left"] = calculate_days_left(item["expiry_date"])

    def generate():
        data = [["Item Name", "Quantity", "Status", "Expiry Date", "Days Left"]]
        for item in items:
            data.append([
                item["item_name"],
                item["quantity"],
                item["status"],
                item["expiry_date"],
                item["days_left"]
            ])
        output = ""
        for row in data:
            output += ",".join(map(str, row)) + "\\n"
        return output

    return Response(generate(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=smart_pantry_data.csv"})

# ✅ Run the app
if __name__ == "__main__":
    app.run(debug=True)
