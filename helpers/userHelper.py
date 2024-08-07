from data.firebaseConfig import db
import json

def is_unique_email(email):
    email_exists = db.collection('users').where('email', '==', email).stream()
    if any(email_exists):
        return False
    return True
    
def is_unique_username(username):
    username_exists = db.collection('users').where('username', '==', username).stream()
    if any(username_exists):
        return False
    return True

#Ler arquivo .json com as chaves secretas
def load_config():
    with open('config.json') as config_file:
        config = json.load(config_file)
    return config