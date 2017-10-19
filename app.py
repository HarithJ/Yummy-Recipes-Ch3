from flask import Flask, render_template, redirect, url_for
app = Flask(__name__, static_folder='designs/UI', template_folder='designs/UI')

@app.route('/')
@app.route('/index.html/')
def index():
    return render_template("index.html")

@app.route('/login.html/')
def login_page():
    return render_template("login.html")

if __name__== '__main__':
    app.run()
