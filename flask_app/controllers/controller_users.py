from flask_app.models.model_user import User
from flask_app.models.model_tree import Tree
from flask_app import app
from flask import render_template, redirect, flash, session, request
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

@app.route('/')
def index():
    # if 'user_id' not in session:
    #     return redirect('/')
    # user = User.get_user(session['user_id'])
    return render_template('index.html', )

@app.route('/welcome')
def welcome_user():

    # check to see if a user is logged in
    if 'user_id' not in session:
        return redirect('/')

    # get information from the id num in session
    user = User.get_user(session)
    trees = Tree.get_all_data()
    
    # Uses the __init__ self variable declarations for jinja! 
    return render_template('user_dashboard.html', user = user, trees = trees)

@app.route('/register', methods=['POST'])
def register():

    #validates information input, redirects to same page if incorrect
    valid = User.validate_info(request.form)
    if not valid: 
        return redirect('/')
    
    #processes the information below if it is valid! 
    #hash the password and set it apart of the data being passed in. 
    data = {
        'first' : request.form['first'],
        'last' : request.form['last'],
        'email' : request.form['email'],
        'pw_hash' : bcrypt.generate_password_hash(request.form['password'])
    }
    user = User.create_user(data)

    #declare the session/logs in user
    session['user_id'] = user
    
    return redirect('/welcome')

@app.route('/login', methods=['POST'])
def login():
    # get user by the email
    user = User.get_user_by_email(request.form)
    if not user:
        flash('Invalid Email or Password', 'login')
        return redirect('/')
    
    # check hashed password against the inputted password
    if not bcrypt.check_password_hash(user.password, request.form['password']):
        flash('Invalid Email or Password', 'login')
        return redirect('/')

    # if everything passes, log in the user 
    session['user_id'] = user.id   
    return redirect('/welcome')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

