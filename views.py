import json
import requests
from route_helper import simple_route
from flask import render_template, Markup, request


@simple_route('/')
def hello(world: dict) -> str:
    '''
    The starting page if the Caesara Rodney quest

    :param world: The current world
    :return: The HTML viewed by the user
    '''
    world['foods'] = []
    return render_template("entering.html")

@simple_route('/goto/<where>/')
def open_door(world: dict, where: str) -> str:
    '''
    This either redirects you to dine in at Caesar Rodney or takes you to the dine in page depending on if you chose to dine in or takeout

    :param world: The current world
    :param where: The location the player chose to go - either dine in or takeout
    :return: The HTML viewed by the user
    '''
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
   '''
   This use an api to collect all foods that matched the users input food.

   :param world: The current world
   :param food: The food that the user is searching for
   :return: The HTML viewed by the user
   '''
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
    '''
    This adds the selected food to the users list of existing foods.

    :param world: The current world
    :param food: The food the the user is selecting to add to their tray
    :return: The HTML viewed by the user
    '''
    world['foods'].append(food)
    food_list = get_current_foods(world)
    message = '''
    <div style="text-align: center"><br><p><span class='text-success'><strong>Success!</strong></span> Do you want to add another food?</p>
    <button type='button' class="button btn btn-success" onclick="window.location.href = '/goto/dinein/'" >Yes</button><button class="button btn btn-danger" type='button' onclick="window.location.href = '/end/'" >No</button></div> 
    '''
    return render_template('current_foods.html', code=Markup(message), foods=Markup(food_list))

@simple_route('/do_swap_foods/<food>')
def do_swap_foods(world: dict, food: str):
    '''
    Takes the user to the list of foods they can choose to swap with their new one.

    :param world: The current world
    :param food: The new food that the user chose, which will be swapped with an old food.
    :return: The HTML viewed by the user.
    '''
    food_list = get_current_foods(world)
    return render_template("swap_foods.html", food=food, food1=world['foods'][0], food2=world['foods'][1], food3=world['foods'][2], foods=Markup(food_list))

@simple_route('/swap_foods/<new_food>')
def swap_foods(world: dict, *args, new_food: str=''):
    '''
    This does the actual swapping of the two foods.

    :param world: The current world
    :param args: various arguments
    :param new_food: The food to be added to the list
    :return: The HTML viewed by the user.
    '''
    world['foods'][int(request.values.get('food'))] = new_food
    food_list = get_current_foods(world)
    message = '''
    <div style="text-align: center">
    <br><p><span class='text-success'><strong>Success!</strong></span> Do you want to add another food?</p>
    <button type='button' class="button btn btn-success" onclick="window.location.href = '/goto/dinein/'" >Yes</button><button class="button btn btn-danger" type='button' onclick="window.location.href = '/end/'" >No</button>
    </div> 
    '''
    return render_template('current_foods.html', code=Markup(message), foods=Markup(food_list))

@simple_route('/end/')
def end(world: dict):
    '''
    Takes the user to the end page, which will show their food and ask for allergies.

    :param world: The current world
    :return: The HTML viewed by the user
    '''
    food_list = get_current_foods(world)
    num_of_foods = len(world['foods'])
    return render_template('ending.html', foods=Markup(food_list), num_of_foods=num_of_foods, food=world['foods'])

@simple_route('/allergy_search/<allergic_ingredient>/')
def allergy_search(world: dict, allergic_ingredient: str):
    '''
    The page compares the inputted ingredient and compares it to the ingredients of their chosen foods by using
    the api. If there are matches, it warns the user and removes those foods from their tray.

    :param world: The current world
    :param allergic_ingredient: The ingredient the user is allergic to
    :return: The HTML viewed by the user
    '''
    food_list = get_current_foods(world)
    foods_allergic_to = []
    allergies = {}
    for food in world['foods']:
        allergies[food] = []
        food_for_url = food.replace(' ', '%20')
        response = requests.get('https://www.themealdb.com/api/json/v1/1/search.php?s=' + food_for_url)
        data = json.loads(response.text)
        food_ingredients = []
        ingredient_num = 1
        for meal in data['meals']:
            if food == meal['strMeal']:
                while (ingredient_num <= 20):
                    food_ingredients.append(meal['strIngredient' + str(ingredient_num)])
                    ingredient_num += 1
                for ingredient in food_ingredients:
                    if allergic_ingredient.lower() in ingredient.lower():
                        foods_allergic_to.append(food)
                        allergies[food].append(ingredient)
                    elif (allergic_ingredient[0:-1]).lower() in ingredient.lower():
                        foods_allergic_to.append(food)
                        allergies[food].append(ingredient)

    #removes duplicated meals from "foods_allergic_to"
    foods_allergic_to = list(dict.fromkeys(foods_allergic_to))

    if not foods_allergic_to:
        html = "<p>Your foods do not contain any " + allergic_ingredient + "</p><br><a class='btn btn-dark' role='button' href='/end/'>Go Back</a>"
        return render_template("allergic_foods.html", html=Markup(html), foods=Markup(food_list))

    #removed meals that do not have ingredients that the user is allergic to
    for meal in allergies.copy():
        if not allergies[meal]:
            allergies.pop(meal)

    for food in foods_allergic_to:
        world['foods'].remove(food)

    html = ''
    for meal in allergies:
        html += "<p>Ingredients in <strong>" + meal + "</strong> that contain <strong>" + allergic_ingredient + "</strong>:</p>"
        for ingredient in allergies[meal]:
           html += "<p>" + ingredient + "</p>"
    html += "<br><p>We have removed these meals from your tray so that you do not die</p><br><a class='btn btn-dark' role='button' href='/goto/dinein'>Find safer foods</a>"

    food_list = get_current_foods(world)
    return render_template("allergic_foods.html", html=Markup(html), foods=Markup(food_list))

def choose_food(world: dict, possible_foods: list):
    '''
    This creates html of a dropdown list to choose food from

    :param world: The current world
    :param possible_foods: A list of food that the user could choose from
    :return: The HTML viewed by the user
    '''
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
    '''
    This creates a list of foods the user has on their tray

    :param world: The current world
    :return: The foods the user has on their tray
    '''
    food_list = "<ul>"
    for food in world['foods']:
        food_list = food_list + '<li>' + food + '</li>'
    food_list = food_list + '</ul><hr>'
    return food_list