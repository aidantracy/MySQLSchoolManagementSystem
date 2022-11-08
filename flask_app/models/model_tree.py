from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.model_user import User
from flask import flash, session


db = 'trees_erd'
class Tree:

    def __init__(self, data):
        self.id = data['id']
        self.species = data['species']
        self.location = data['location']
        self.reason = data['reason']
        self.date_planted = data['date_planted']

        self.all_visitors = []
        self.owner = None

    # validate tree information
    @staticmethod
    def validate_tree(data):
        is_valid = True
        if len(data['species']) < 5:
            flash('Species name must be at least 5 letters', 'tree')
            is_valid = False
        if len(data['location']) < 2:
            flash('location must be min 2 characters', 'tree')
            is_valid = False
        if len(data['reason']) > 50 or data['reason'] == "":
            flash('Reason must be between 1 and 50 characters', 'tree')
            is_valid = False
        if not data['date_planted']:
            flash('select a date planted', 'tree')
            is_valid = False
        return is_valid
    
    # CREATE - Tree
    @classmethod
    def plant(cls, data):
        query = """
                INSERT INTO trees (user_id, species, location, reason, date_planted)
                VALUES (%(user_id)s, %(species)s, %(location)s, %(reason)s, %(date_planted)s);
                """
        return connectToMySQL(db).query_db(query, data)
    
    # READ - all trees w/ Owner-info one-to-many - not used after many-to-many
    @classmethod
    def get_all_trees(cls):
        query = """
                SELECT * FROM trees
                JOIN users ON trees.user_id = users.id
                """
        results = connectToMySQL(db).query_db(query)

        trees = []
        for result in results:

            tree = cls(result)

            owner_info = {
                'id' : result['user_id'],
                'first_name' : result['first_name'],
                'last_name' : result['last_name'],
                'email' : result['email'],
                'password' : result['password'],
                'created_at' : result['users.created_at'],
                'updated_at' : result['users.updated_at']
            }

            owner = User(owner_info)
            tree.owner = owner
            trees.append(tree)
        
        return trees

    #get logged in user's trees
    @classmethod
    def get_user_trees(cls, data):
        query = "SELECT * FROM trees WHERE user_id = %(user_id)s;"
        return connectToMySQL(db).query_db(query, data)
    
    # get 1 tree's information to edit
    @classmethod
    def get_tree_by_id(cls, data):
        # get tree information
        query = """
                SELECT * FROM trees WHERE id = %(tree_id)s;
                """
        result = connectToMySQL(db).query_db(query, data)

        # get user information from tree
        user_data = {
            'user_id' : result[0]['user_id']
        }
        query2 ="""
                SELECT * FROM users WHERE id = %(user_id)s;
                """
        user = connectToMySQL(db).query_db(query2, user_data)

        # make user result a dict then add to the owner data for the tree.
        user = user[0]

        # make a class instance of tree to append owner info
        result = cls(result[0])
        result.owner = user

        # add tree id to session to pass back 
        session['tree_id'] = result.id
        return result

    # UPDATE after edit
    @classmethod
    def update(cls, data):
        query = """
                UPDATE trees
                SET species = %(species)s,
                    date_planted = %(date_planted)s,
                    location = %(location)s,
                    reason = %(reason)s
                WHERE id = %(tree_id)s;
                """
        return connectToMySQL(db).query_db(query, data)
    
    # DELETE tree 
    @classmethod
    def delete_tree(cls, data):

        # delete from visitors
        query1 = "DELETE FROM visitors WHERE visitors.tree_id = %(tree_id)s"
        connectToMySQL(db).query_db(query1, data)
        # delete from trees
        query2 = "DELETE FROM trees WHERE id = %(tree_id)s"
        return connectToMySQL(db).query_db(query2, data)
    
    # adds a new visitor
    @classmethod
    def visited(cls, data):
        query = """
                INSERT INTO visitors(tree_id, user_id)
                VALUES (%(tree_id)s, %(user_id)s);
                """
        return connectToMySQL(db).query_db(query, data)
    
    # MANY TO MANY
    @classmethod
    def get_all_data(cls):

        query = """
                SELECT * FROM trees
                JOIN users ON trees.user_id = users.id
                LEFT JOIN visitors ON visitors.tree_id = trees.id
                LEFT JOIN users AS users2 ON visitors.user_id = users2.id
                """
        
        results = connectToMySQL(db).query_db(query)

        visits = []
        for result in results:
            new_visitor = True

            visitor_data = {
                'id' : result['users2.id'],
                'first_name' : result['users2.first_name'],
                'last_name' : result['users2.last_name'],
                'email' : result['users2.email'],
                'password' : result['users2.password'],
                'created_at' : result['users2.created_at'],
                'updated_at' : result['users2.updated_at']
            }

            if len(visits) > 0 and visits[len(visits)-1].id == result['id']:
                visits[len(visits)-1].all_visitors.append(User(visitor_data))
                new_visitor = False
            
            if new_visitor:
                visit = cls(result)
                user_info = {
                    'id' : result['user_id'],
                    'first_name' : result['first_name'],
                    'last_name' : result['last_name'],
                    'email' : result['email'],
                    'password' : result['password'],
                    'created_at' : result['users.created_at'],
                    'updated_at' : result['users.updated_at']
                }
                user = User(user_info)
                visit.owner = user
                if result['users2.id']:
                    visit.all_visitors.append(User(visitor_data))
                visits.append(visit)
        return visits

    @classmethod
    def get_visitors(cls, data):

        query = """
                SELECT * FROM visitors
                LEFT JOIN users ON visitors.user_id = users.id
                WHERE visitors.tree_id = %(tree_id)s; 
                """
        results = connectToMySQL(db).query_db(query, data)
        print("RESULTS", results)
        visitors = []
        for result in results:
            visitor_info = {
                'first_name' : result['first_name'],
                'last_name' : result['last_name'],
                'id' : result['id']
            }
            if visitor_info not in visitors:
                visitors.append(visitor_info)
        
        return visitors

