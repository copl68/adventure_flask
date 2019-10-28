import json
import requests
from route_helper import simple_route
from flask import render_template, Markup, request


@simple_route('/')
def hello(world: dict) -> str:
    world['foods'] = []
    return render_template("entering.html")

@simple_route('/goto/<where>/')
def open_door(world: dict, where: str) -> str:
    food_list = get_current_foods(world)
    if where == 'takeout':
        text = Markup('''<div style="text-align: center"><p>CR ran out of boxes</p>
    <p>While the box-stocking man is being beaten in the back, you decide that you will stay to dine in</p>
    <a class="btn btn-dark" role="button" href="/goto/dinein">Grab a plate</a></div>''')
        return render_template("heading.html", code=text)
    elif where == 'dinein':
        return render_template('get_food.html', foods=Markup(food_list))

@simple_route('/search_food/<food>/')
def search_food(world: dict, food: str):
    try:
        response = requests.get('https://www.themealdb.com/api/json/v1/1/search.php?s=' + food)
        data = json.loads(response.text)
        possible_foods = []
        for meal in data['meals']:
            possible_foods.append(meal['strMeal'])
        return choose_food(world, possible_foods)
    except:
        food_list = get_current_foods(world)
        return render_template('food_not_found.html', food=food.lower(), foods=Markup(food_list))

@simple_route('/add_to_collection/<food>')
def add_to_collection(world: dict, food: str):
    world['foods'].append(food)
    food_list = get_current_foods(world)
    message = '''
    <div style="text-align: center"><br><p><span class='text-success'><strong>Success!</strong></span> Do you want to add another food?</p>
    <button type='button' onclick="window.location.href = '/goto/dinein/'" >Yes</button><br><button type='button' onclick="window.location.href = '/end/'" >No</button></div> 
    '''
    return render_template('current_foods.html', code=Markup(message), foods=Markup(food_list))

@simple_route('/do_swap_foods/<food>')
def do_swap_foods(world: dict, food: str):
    food_list = get_current_foods(world)
    return render_template("swap_foods.html", food=food, food1=world['foods'][0], food2=world['foods'][1], food3=world['foods'][2], foods=Markup(food_list))

@simple_route('/swap_foods/<new_food>')
def swap_foods(world: dict, *args, new_food: str=''):
    world['foods'][int(request.values.get('food'))] = new_food
    food_list = get_current_foods(world)
    message = '''
    <div style="text-align: center"><br><p><span class='text-success'><strong>Success!</strong></span> Do you want to add another food?</p>
    <button type='button' onclick="window.location.href = '/goto/dinein/'" >Yes</button><br><button type='button' onclick="window.location.href = '/end/'" >No</button></div> 
    '''
    return render_template('current_foods.html', code=Markup(message), foods=Markup(food_list))

@simple_route('/end/')
def end(world: dict):
    food_list = get_current_foods(world)
    num_of_foods = len(world['foods'])
    return render_template('ending.html', foods=Markup(food_list), num_of_foods=num_of_foods, food=world['foods'])

def choose_food(world: dict, possible_foods: list):
    food_list = get_current_foods(world)
    html = '''<div style="text-align: center"><br><br><form>
    <select id='food_select'>'''
    for food in possible_foods:
        html = html + '''<option value="{food}">{food}</option>'''.format(food=food)
    if len(world['foods']) >= 3:
        html = html + '</select><button class="button btn btn-dark" type="button" onclick="too_many()">Select</button></form>'
        return render_template("food_list.html", list=Markup(html), foods=Markup(food_list))
    elif 0 <= len(world['foods']) < 3:
        html = html + '</select><button class="button btn btn-dark" type="button" onclick="select()">Select</button></form></div>'
        return render_template("food_list.html", list=Markup(html), foods=Markup(food_list))

def get_current_foods(world: dict):
    food_list = "<ul>"
    for food in world['foods']:
        food_list = food_list + '<li>' + food + '</li>'
    food_list = food_list + '</ul><hr>'
    return food_list