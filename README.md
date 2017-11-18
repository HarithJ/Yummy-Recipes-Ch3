TravisCI Badge: [![Build Status](https://travis-ci.org/HarithJ/Yummy-Recipes.svg?branch=restructuring-ch2)](https://travis-ci.org/HarithJ/Yummy-Recipes)

coveralls badge: [![Coverage Status](https://coveralls.io/repos/github/HarithJ/Yummy-Recipes/badge.svg?branch=restructuring-ch2)](https://coveralls.io/github/HarithJ/Yummy-Recipes?branch=restructuring-ch2)


# Yummy-Recipes

Yummy recipes is a website where you, as a user, can register yourself, login, add a category for your recipes, add recipes to any of your category via fancy model and also signout when you are done. So how will it be of help to you? Well, when you stumble upon a great recipe, you can't save it in back of your head, with all the things you need to attend to.... Don't worry Yummy-Recipes is there to save your yummy recipe for you so that you can came back and have a good look at it so that you don't miss out on an important ingredient!!!

Try it NOW, visit:

        yummy-recipes-harith.herokuapp.com
        
And register yourself! After registering you will be taken to a login page, after logging in, you will be take to a page where you will be able to create a category, edit name of a current category and delete a category. After having your categories in place, you can visit any category and add recipes to it, or edit existing recipes, or delete a recipe once your taste-buds take a turn! When you are done you can move the mouse pointer on top-right corner of the screen and logout of the website.

PLEASE NOTE: The website is not using any database to store data, so data is not persistence. This means that whenever the server will get restarted your all info will go away.


To run the tests for the website:

1. Use Command Line to cd into the Yummy-Recipes folder.

2. Activate virtual environment by typing:

        virtualenv bin/activate
        
3. run the tests by typing:

        nosetests
        
