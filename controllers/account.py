from flask import Blueprint, request, jsonify, session
from data.firebaseConfig import db
from helpers.passwordUtils import hash_password
from helpers.userHelper import is_unique_email, is_unique_username, is_unique_email_update, is_unique_username_update

account_bp = Blueprint('account', __name__)

# Rota para retornar todos os usuários


@account_bp.route('/users', methods=['GET'])
def get_all_users():
    if 'user_id' in session:
        users = db.collection('users').stream()
        users_list = [user.to_dict() for user in users]
        
        if users_list:
            return jsonify(users_list), 200
        
        return jsonify({
            "erro" : "Nenhum usuário cadastrado foi encontrado."
        }), 404
    
    return jsonify({
        "erro" : "Nenhum usuário conectado foi encontrado."    
    }), 401

# Rota para retornar um usuário
@account_bp.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    if 'user_id' in session:        
        doc_ref = db.collection('users').document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return jsonify(doc.to_dict()), 200
        
        return jsonify({
            "error": "Usuário não encontrado."
        }), 404
    
    return jsonify({
        "erro" : "Nenhum usuário conectado foi encontrado."    
    }), 401


# Rota para cadastrar usuário
@account_bp.route('/create_user', methods=['POST'])
def create_user():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not all([name, email, username, password]):
        return jsonify({
            "error": "Todos os campos são obrigatórios"
        }), 400
        
    if not is_unique_email(email):
        return jsonify({"error": "Esse e-mail já está sendo utilizado."}), 409
    
    if not is_unique_username(username):
        return jsonify({"error": "Esse nome de usuário já está sendo utilizado."}), 409

    hashed_password = hash_password(password)

    user_data = {
        "name": name,
        "email": email,
        "username": username,
        "password": hashed_password,
    }

    db.collection('users').add(user_data)
    return jsonify({
        "message": "Usuário criado com sucesso."
    }), 201


# Rota para atualizar dados do usuário
@account_bp.route('/update_user/', methods=['PUT'])
def update_user():
    if 'user_id' in session:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        
        if not all([name, email, username, password]):
            return jsonify({
                "error": "Todos os campos são obrigatórios"
            }), 400
                     
        current_user_id = session.get('user_id')
        
        if email != session.get('email') and not is_unique_email_update(email, current_user_id):
            return jsonify({"error": "Esse e-mail já está sendo utilizado."}), 409
        
        if username != session.get('username') and not is_unique_username_update(username, current_user_id):
            return jsonify({"error": "Esse nome de usuário já está sendo utilizado."}), 409

        hashed_password = hash_password(password)

        user_data = {
            "name": name,
            "email": email,
            "username": username,
            "password": hashed_password,
        }

        doc_ref = db.collection('users').document(current_user_id)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.update(user_data)
            return jsonify({
                "message": "Dados do usuário atualizado."
            }), 200
            
        return jsonify({
            "erro": "Usuário não encontrado."
        }), 404
        
    return jsonify({
        "erro" : "Nenhum usuário conectado foi encontrado."
    }), 401

# Rota para deletar usuário
@account_bp.route('/delete_user', methods=['DELETE'])
def delete_user():
    if 'user_id' in session: 
        user_id = session.get('user_id')       
        doc_ref = db.collection('users').document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.delete()
            return jsonify({
                "message": "Usuário deletado."
            }), 204
            
        return jsonify({
            "error": "Usuário não encontrado."
        }), 404
        
    return jsonify({
        "erro" : "Nenhum usuário conectado foi encontrado."
    }), 401
