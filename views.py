import json
import requests
from route_helper import simple_route
from flask import render_template, Markup


@simple_route('/')
def hello(world: dict) -> str:
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

def choose_food(world: dict, possible_foods: list):
    html = '''<select id='food_select'>'''
    for food in possible_foods:
        html = html + '''<option value={food}>{food}</option>'''.format(food=food)
    html = html + '</select>'
    return Markup(html)

@simple_route("/save/name/")
def save_name(world: dict, monsters_name: str) -> str:
    """
    Update the name of the monster.

    :param world: The current world
    :param monsters_name:
    :return:
    """
    world['name'] = monsters_name

    return GAME_HEADER+"""You are in {where}, and you are nearby {monster_name}
    <br><br>
    <a href='/'>Return to the start</a>
    """.format(where=world['location'], monster_name=world['name'])
