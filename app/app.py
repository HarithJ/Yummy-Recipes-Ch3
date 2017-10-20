from flask import Flask, render_template, redirect, url_for, request, session, g, abort, flash

#config
SECRET_KEY = 'development mode'

app = Flask(__name__, static_folder='../designs/UI', template_folder='../designs/UI')
app.config.from_object(__name__)

class User:
    def __init__(self, name, email, password, details):
        self.name = name
        self.email = email
        self.password = password
        self.details = details

    def is_valid(self, password):
        return self.password == password

users = {}

@app.route('/')
@app.route('/index.html/')
def index():
    return render_template("index.html")

@app.route('/login.html/')
def login_page():
    return render_template("login.html")

@app.route('/register/', methods=['POST'])
def register():
    error = None
    # check if the password and ver password are not the same
    if request.form['password'] != request.form['verpassword']:
        error = 'Password does not match the password in verify password field'
        return render_template('index.html', error=error)

    users[request.form['name']] = User(request.form['name'], request.form['email'], request.form['password'], request.form['details'])
    return redirect(url_for('login_page'))

@app.route('/validate/', methods=['POST'])
def validate():
    if request.form['name'] in users:
        if users[request.form['name']].is_valid(request.form['password']):
            return render_template("profile.html", value=request.form['name'])

    return redirect(url_for('login_page'))

if __name__== '__main__':
    app.run()
