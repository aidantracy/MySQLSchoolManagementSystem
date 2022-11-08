from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-Z]+$')

db = 'trees_erd'

class User:

    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

        self.trees_planted = []
        
    
    # Register validation
    @staticmethod
    def validate_info(data):
        is_valid = True
        #check passwords parameters: >1 num, >1 uppercase, and >8 characters long
        if len(data['password']) < 8:
            flash('Password needs to be at least 8 characters long', 'register')
            is_valid = False
        elif re.search('[0-9]', data['password']) is None:
            flash('Password must contain at least 1 number', 'register')
            is_valid = False
        elif re.search('^[A-Z]', data['password']) is None:
            flash('Password must contain at least 1 uppercase', 'register')
            is_valid = False
        # confirm password
        if data['password'] != data['confirm']:
            flash('Password does not match', 'register')
            is_valid = False

        #check first and last name and the REGEX
        if len(data['first']) < 2:
            flash('First name needs to be min 2 letters', 'register')
            is_valid = False
        if len(data['last']) < 2:
            flash('Last name needs to be min 2 letters', 'register')
            is_valid = False
        if not NAME_REGEX.match(data['first']) or not NAME_REGEX.match(data['last']):
            flash('Name can only contain letters', 'register')
            is_valid = False

        #check email by REGEX
        if not EMAIL_REGEX.match(data['email']):
            flash('Invalid Email', 'register')
            is_valid = False
        else:
        #checks to see if email is already in database
            query = "SELECT * FROM users WHERE email = %(email)s;"
            results = connectToMySQL(db).query_db(query, data)
            if results:
                flash('This email already exists', 'register')
                is_valid = False
        return is_valid
    
    # registers user
    @classmethod
    def create_user(cls, data):

        query = """
                INSERT INTO users(first_name, last_name, email, password)
                VALUES (%(first)s, %(last)s, %(email)s, %(pw_hash)s)
                """
        return connectToMySQL(db).query_db(query, data)

    # retrieves the user with ID
    @classmethod
    def get_user(cls, data):
        query = "SELECT * FROM users WHERE id = %(user_id)s"
        result = connectToMySQL(db).query_db(query, data)
        #check to see if there was no email returned
        if len(result) < 1:
            return False
        return cls(result[0])
    
    # retrieves user by email
    @classmethod
    def get_user_by_email(cls, data):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        results = connectToMySQL(db).query_db(query, data)
        if len(results) < 1:
            return False
        return cls(results[0])
    