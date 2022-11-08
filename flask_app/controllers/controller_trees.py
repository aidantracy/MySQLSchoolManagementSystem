from flask_app.models.model_user import User
from flask_app.models.model_tree import Tree
from flask_app import app
from flask import render_template, redirect, flash, session, request

#Plant a tree page
@app.route('/new_tree')
def new_tree():
    # check if logged in
    if 'user_id' not in session:
        return redirect('/')
    user = User.get_user(session)
    return render_template('new_tree.html', user = user)

# form for planting a tree
@app.route('/plant_tree', methods=['POST'])
def plant_tree():

    # validate the form information from planting
    valid = Tree.validate_tree(request.form)
    if not valid:
        return redirect('/new_tree')
    
    # consolidate information from form and session
    data = {
        'species' : request.form['species'],
        'location' : request.form['location'],
        'reason' : request.form['reason'],
        'date_planted' : request.form['date_planted'],
        'user_id' : session['user_id']
    }

    Tree.plant(data)
    # redirect to dashboard
    return redirect('/welcome')

# display user's trees
@app.route('/my_trees')
def get_user_trees():
    if 'user_id' not in session:
        return redirect('/')
    
    data = {'user_id' : session['user_id']}
    trees = Tree.get_user_trees(data)
    user = User.get_user(session)

    return render_template('user_trees.html', trees = trees, user = user)

# display tree to edit
@app.route('/edit/<int:tree_id>')
def edit_tree(tree_id):
    # check if logged in
    if 'user_id' not in session:
        return redirect('/')

    data = {
        'tree_id' : tree_id 
    }

    tree = Tree.get_tree_by_id(data)
    user = User.get_user(session)
    return render_template('edit_tree.html', tree = tree, user = user)

# UPDATE route
@app.route('/update_tree', methods=['POST'])
def update_tree():
    # check to see if user is still logged in
    if 'user_id' not in session:
        return redirect('/')
    valid = Tree.validate_tree(request.form)
    if not valid:
        return redirect(f'/edit/{session["tree_id"]}')
    
    data = {
        'tree_id' : session['tree_id'],
        'species' : request.form['species'],
        'location' : request.form['location'],
        'reason' : request.form['reason'],
        'date_planted' : request.form['date_planted']
    }

    Tree.update(data)
    session['tree_id'] = None
    # redirect back to manage trees if other edits are necessary
    return redirect('/my_trees')
    
# DELETE route
@app.route('/delete/<int:tree_id>')
def delete_tree(tree_id):
    if 'user_id' not in session:
        return redirect('/')

    data = {'tree_id' : tree_id}
    Tree.delete_tree(data)
    return redirect('/my_trees')

# READ TREE DETAILS
@app.route('/show/<int:tree_id>')
def show_tree(tree_id):
    # check if logged in
    if 'user_id' not in session:
        return redirect('/')
    
    data = {
        'tree_id' : tree_id
    }

    tree = Tree.get_tree_by_id(data)
    visitors = Tree.get_visitors(data)

    user = User.get_user(session)
    return render_template('show_tree.html', tree = tree, user = user, visitors = visitors)

#VISITED - MANY TO MANY
@app.route('/visited/<int:tree_id>')
def visited(tree_id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'user_id' : session['user_id'],
        'tree_id' : tree_id
    }
    
    Tree.visited(data)
    return redirect('/welcome')