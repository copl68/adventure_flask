from route_helper import simple_route
from flask import render_template, Markup


@simple_route('/')
def hello(world: dict) -> str:
    return render_template("entering.html")

ENCOUNTER_MONSTER = """
<!-- Curly braces let us inject values into the string -->
You are in {}. You found a monster!<br>

<!-- Image taken from site that generates random Corgi pictures-->
<img src="http://placecorgi.com/260/180" /><br>
    
What is its name?

<!-- Form allows you to have more text entry -->    
<form action="/save/name/">
    <input type="text" name="player"><br>
    <input type="submit" value="Submit"><br>
</form>
"""


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
    return Markup('<p> Your food is {food} </p>'.format(food=food))

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
