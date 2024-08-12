from flask import Blueprint, jsonify, session, request
from data.firebaseConfig import db
from firebase_admin import firestore
from helpers.passwordUtils import hash_password, check_password
from helpers.groupHelper import get_group_for_update
import datetime

group_bp = Blueprint('group', __name__)

#Rota para criar o grupo de palpites
@group_bp.route('/create_group', methods=['POST'])
def create_group():
    if 'user_id' in session:
        data = request.json
        group_name = data.get('group_name')
        group_password = data.get('group_password')
        owner_id = session.get('user_id')
        
        if not group_name or not group_password:
            return jsonify({
                "erro" : "Insira todos os campo"
            }), 400
        
        hashed_password = hash_password(group_password)
        
        new_group = {
            'group_name' : group_name,
            'group_password' : hashed_password,
            'owner_id' : owner_id,
            'members' : [owner_id],
            'created_at' : datetime.datetime.now()
        }
        
        try:
            #Cria o documento e adiciona o Id gerado pelo Firebase dentro do próprio documento
            group_ref = db.collection('groups').add(new_group)
            group_id = group_ref[1].id
            db.collection('groups').document(group_id).update({'group_id' : group_id})
            
            return jsonify({
                "message" : "Grupo criado com sucesso."
            }), 200
        
        except:
            return jsonify({
                "erro" : "Não foi possível criar o grupo."
            })
        
    return jsonify({
        "erro" : "Nenhum usuário conectado foi encontrado."
    }), 400
    
#Rota para obter todos os grupos
@group_bp.route('/groups', methods=['GET'])
def get_all_groups():
    if 'user_id' in session:
        groups = db.collection('groups').stream()
        groups_list = [group.to_dict() for group in groups]       
        return jsonify(groups_list), 200
    
    return jsonify({
        "erro" : "Nenhum usuário conectado foi encontrado."
    }), 400
    
# Rota para retornar um grupo
@group_bp.route('/group/<group_name>', methods=['GET'])
def get_group(group_name):
    docs = db.collection('groups').where('group_name', '==', group_name).stream()
    docs_list = [doc.to_dict() for doc in docs]
    if docs_list:
        return jsonify(docs_list), 200
    return jsonify({
        "error": "Grupo não encontrado."
    }), 404
    
#Rota para atualizar informações do grupo
@group_bp.route('/update_group/<group_id>', methods=['PUT'])
def update_group(group_id):
    if 'user_id' in session:
        user_id = session.get('user_id')
        data = request.json
        group_name = data.get('group_name')
        group_password = data.get('group_password')
        
        if not all([group_name, group_password]):
            return jsonify({
                "erro" : "Todos os campos são obrigatórios."
            }), 400

        atual_group = get_group_for_update(group_id)
        if not atual_group: 
            return jsonify({
                "erro" : "Grupo não encontrado"
            }), 404
        
        data_group = atual_group[1]
        
        if user_id != data_group.get('owner_id'):
            return jsonify({
                "erro" : "Apenas o dono do grupo pode fazer alterações."
            }), 403
        
        hashed_group_password = hash_password(group_password)
        
        group_data = {
            "group_name" : group_name,
            "group_password" : hashed_group_password
        }
        
        doc_ref = db.collection('groups').document(group_id)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.update(group_data)
            return jsonify({
                "message" : "Dados do grupo atualizado."
            }), 200

    return jsonify({
        "error" : "Nenhum usuário conectado foi encontrado."
    }), 400


#Rota para deletar um grupo
@group_bp.route('/delete_group/<group_id>', methods=['DELETE'])
def delete_group(group_id):
    if 'user_id' in session:
        doc_ref = db.collection('groups').document(group_id)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.delete()
            return jsonify({
                "message" : "Grupo deletado com sucesso."
            }), 200
            
        return jsonify({
            "erro" : "Nenhum grupo foi encontrado."
        }), 400
        
    return jsonify({
        "erro" : "Nenhum usuário conectado foi encontrado."
    }), 400


#Rota para entrar em um grupo
@group_bp.route('/join_group/<group_id>', methods=['POST'])
def join_group(group_id):
    if 'user_id' in session:        
        data = request.json
        group_name = data.get('group_name')
        group_password = data.get('group_password')
        user_id = session.get('user_id')
        
        group_ref = db.collection('groups').document(group_id)
        group = group_ref.get()             
        
        if group.exists:
            group_data = group.to_dict()
            
            if group_name != group_data['group_name']:
                return jsonify({
                    "erro" : "Esse grupo não foi encontrado."
                }), 400
        
            if not check_password(group_data['group_password'], group_password):
                return jsonify({
                    "erro" : "Senha inválida."
                }), 400
            
            try:
                group_ref.update({"members" : firestore.ArrayUnion([user_id])})
                return jsonify({
                    "message" : "Usuário inserido no grupo."
                }), 200
                
            except Exception as e:
                return jsonify({
                    "erro" : str(e) or "Não foi possível ingressar no grupo."
                }), 500
        
        return jsonify({
                    "erro" : "Esse grupo não foi encontrado."
                }), 400
    return jsonify({
        "erro" : "Nenhum usuário conectado foi encontrado."
    }), 400
        
#Rota para sair do grupo
@group_bp.route('/leave_group/<group_id>', methods=['PUT'])
def leave_group(group_id):
    if 'user_id' in session:
        group_ref = db.collection('groups').document(group_id)
        group = group_ref.get()
        user_id = session.get('user_id')
        
        if group.exists:
            group_ref.update({"members" : firestore.ArrayRemove([user_id])})          
            return jsonify({
                "message" : "Usuário removido do grupo."
            }), 200
    return jsonify({
        "erro" : "Nhenhum usuário conectado foi encontrado."
    }), 400
    
#Rota para retornar últimas apostas do usuário
@group_bp.route('/user_bets/<group_id>', methods=['GET'])
def user_bets(group_id):
    if 'user_id' in session:
        user_id = session.get('user_id')
        bets_ref = db.collection('groups').document(group_id).collection('bets').where('user_id', '==', user_id).stream()
        
        bets_list = []
        for bet in bets_ref:
            bet_data = bet.to_dict()
            bets_list.append({
                "match_id" : bet_data.get('match_id'),
                "bet" : bet_data.get('bet'),
                "result" : bet_data.get('result')
            })
        
        if bets_list:
            return jsonify(bets_list), 200
        
        return jsonify({
            "erro" : "Não foi possível retornar nenhuma aposta."
        }), 400
    
    return jsonify({
        "erro" : "Nenhum usuário conectado foi encontrado."
    }), 400