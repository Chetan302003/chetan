from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('mongodb+srv://htutorial2003:RILzU6NqJrEQAvYL@cluster0.7waqb7h.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['test']
orders_collection = db['orders']

@app.route('/')
def index():
    orders = db.orders.find()
    recommendations = process_orders(orders)
    print(recommendations)  
    return render_template('index.html', recommendations=recommendations)

def process_orders(orders):
    # Initialize an empty dictionary to store item quantities
    recommendations = db.orders.aggregate([
        {"$unwind": "$items"},
        {"$group": {"_id": "$items.itemName", "itemQty": {"$sum": 1}}},
        {"$sort": {"itemQty": -1}},
        {"$limit": 5}
    ])
    item_quantities = {}

    # Iterate over orders and count item quantities
    for order in orders:
        items = order.get('items', [])
        for item in items:
            item_name = item.get('itemName')
            item_quantities[item_name] = item_quantities.get(item_name, 0) + 1

    # Convert the dictionary to a list of dictionaries
    recommendations = [{'item': item, 'quantity': quantity} for item, quantity in item_quantities.items()]

    # Sort recommendations based on quantity in descending order
    recommendations = sorted(recommendations, key=lambda x: x['quantity'], reverse=True)

    return recommendations[:5]  # Return top 5 recommendations




if __name__ == '__main__':
    app.run(debug=True)
