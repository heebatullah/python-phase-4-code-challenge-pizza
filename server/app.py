#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants", methods=['GET'])
def get_restaurants():

    restaurants = []

    for restaurant in Restaurant.query.all():
        # A simple dictionary for json output
        restaurant_dict ={
            "address": restaurant.address,
            "id":restaurant.id,
            "name":restaurant.name
        }
        restaurants.append(restaurant_dict)


    return make_response(restaurants, 200) 


@app.route("/restaurants/<int:id>", methods=['GET'])
def get_restaurant_by_id(id):

    restaurant = Restaurant.query.filter(Restaurant.id == id).first()
    # returns error message for invalid ids
    if not restaurant:
        return make_response({"error": "Restaurant not found"}, 404) 

    restaurant_dict ={
        "address": restaurant.address,
        "id":restaurant.id,
        "name":restaurant.name,
        "restaurant_pizzas":[]   # an empty list that will be appended to using a for loop 
        }  
    
    for restaurant_pizza in restaurant.restaurant_pizzas:
        restaurant_pizza_dict={
            "id":restaurant_pizza.id,
            "pizza":{
                "id":restaurant_pizza.pizza.id,
                "name":restaurant_pizza.pizza.name,
                "ingredients":restaurant_pizza.pizza.ingredients
            },
            "pizza_id":restaurant_pizza.pizza.id,
            "price":restaurant_pizza.price,
            "restaurant_id":restaurant_pizza.restaurant_id
        }

        # appends the dictionary under the for loop into the empty list declared earlier
        restaurant_dict["restaurant_pizzas"].append(restaurant_pizza_dict)
       
    return make_response(restaurant_dict, 200)

@app.route("/restaurants/<int:id>", methods = ['DELETE'])
def delete_restaurant_by_id(id):

    restaurant =Restaurant.query.filter(Restaurant.id == id).first()

    if not restaurant:
        return make_response({"error": "Restaurant not found"},404)
    
    db.session.delete(restaurant)
    db.session.commit()

    return make_response("", 204)  

@app.route("/pizzas", methods=['GET'])
def get_pizzas():

    pizzas = []

    for pizza in Pizza.query.all():
        pizza_dict={
            "id": pizza.id,
            "ingredients": pizza.ingredients,
            "name": pizza.name
        }
        pizzas.append(pizza_dict)

    return make_response(pizzas, 200)

@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    # helps fetch data from a json body
    data = request.get_json()

    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    errors = []

    # Validation
    if price is None:
        errors.append("Price is required")
    elif price < 1 or price > 30:
        errors.append("Price must be between 1 and 30")

    pizza = Pizza.query.get(pizza_id)
       
    if not pizza:
        errors.append(f"Pizza with id {pizza_id} does not exist")
    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        errors.append(f"Restaurant with id {restaurant_id} does not exist")

    if errors:
    # return generic error message to pass the test
        return make_response({"errors": ["validation errors"]}, 400)

    # Create RestaurantPizza
    new_restaurant_pizza = RestaurantPizza(
        price=price,
        pizza_id=pizza_id,
        restaurant_id=restaurant_id
    )

    db.session.add(new_restaurant_pizza)
    db.session.commit()

    # Build explicit response dict
    response = {
        "id": new_restaurant_pizza.id,
        "price": new_restaurant_pizza.price,
        "pizza_id": new_restaurant_pizza.pizza_id,
        "restaurant_id": new_restaurant_pizza.restaurant_id,
        "pizza": {
            "id": pizza.id,
            "name": pizza.name,
            "ingredients": pizza.ingredients
        },
        "restaurant": {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address
        }
    }

    return make_response(response, 201)

if __name__ == "__main__":
    app.run(port=5555, debug=True)
