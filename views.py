import json
import requests
from route_helper import simple_route
from flask import render_template, Markup


@simple_route('/')
def hello(world: dict) -> str:
    world['foods'] = []
    return render_template("entering.html")

@simple_route('/goto/<where>/')
def open_door(world: dict, where: str) -> str:
    if where == 'takeout':
        text = Markup('''<p>CR ran out of boxes</p>
    <p>While the box-stocking man is being beaten in the back, you decide that you will stay to dine in</p>
    <a href="/goto/dinein">Grab a plate</a>''')
        return render_template("heading.html", code=text)
    elif where == 'dinein':
        return render_template('get_food.html')

@simple_route('/search_food/<food>/')
def search_food(world: dict, food: str):
    response = requests.get('https://www.themealdb.com/api/json/v1/1/search.php?s=' + food)
    data = json.loads(response.text)
    possible_foods = []
    for meal in data['meals']:
        possible_foods.append(meal['strMeal'])
    return choose_food(world, possible_foods)

@simple_route('/add_to_collection/<food>')
def add_to_collection(world: dict, food: str):
    length = len(world['foods'])
    if length >= 3:
        pass
    elif 0 <= length < 3:
        pass

def choose_food(world: dict, possible_foods: list):
    html = '''<form>
    <select id='food_select'>'''
    for food in possible_foods:
        html = html + '''<option value="{food}">{food}</option>'''.format(food=food)
    html = html + '</select><button type="button" onclick="select()">Select</button></form>'
    return render_template("food_list.html", list=Markup(html))