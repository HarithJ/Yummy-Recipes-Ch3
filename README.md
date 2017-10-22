TravisCI Badge: ![alt text](https://travis-ci.org/HarithJ/Yummy-Recipes.svg?branch=development)

coveralls badge: <a href='https://coveralls.io/github/HarithJ/Yummy-Recipes?branch=development'><img src='https://coveralls.io/repos/github/HarithJ/Yummy-Recipes/badge.svg?branch=development' alt='Coverage Status' /></a>


# Yummy-Recipes
To view the webiste please visit: https://yummy-recipes-harith.herokuapp.com/

You can also clone the development branch and take the following steps to view the website (this shud happen inside command-line prompt:

1. Move in the Yummy-Recipes directory: cd Yummy-Recipes
2. Activate the virtualenv: source bin/activate
3. From here you can use two ways:
    1. Set the variable for flask: export FLASK_APP=webapp/app.py
    2. Run flask: flask run
            OR
    1. gunicorn -w 4 webapp.app:app