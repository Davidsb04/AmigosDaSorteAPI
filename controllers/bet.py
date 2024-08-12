from flask import Blueprint, request, jsonify, session
from data.firebaseConfig import db
import http.client
import json

bet_bp = Blueprint('bet', __name__)

#Acessando e configurando chave da API
with open('config.json') as config_file:
    config = json.load(config_file)
    
api_key = config['API_FOOTBALL_KEY']

#Rota para registrar aposta do usuário
@bet_bp.route('place_bet/<group_id>/<match_id>', methods=['POST'])
def place_bet(group_id, match_id):
    if 'user_id' in session:
        user_id = session['user_id']
        data = request.json
        home_score = data.get('home_score')
        away_score = data.get('away_score')
        
        if home_score is None or away_score is None:
            return jsonify({
                "erro" : "Placares da partida não inseridos."
            }), 400
        
        group_ref = db.collection('groups').document(group_id)
        group= group_ref.get()
        
        if group.exists and user_id in group.to_dict().get('members', []):
            bet_data = {
                "match_id" : match_id,
                "user_id" : user_id,
                "bet" : {
                    "fulltime" : {
                        "home" : home_score,
                        "away" : away_score
                    }
                },
                "result" : "aguardando resultado"
            }
            
            bet_ref = group_ref.collection('bets').document()
            bet_ref.set(bet_data)
            return jsonify({
                "message" : "Aposta registrada com sucesso."
            }), 201
        
        return jsonify({
            "erro" : "Usuário não autorizado ou grupo não encontrado."
        }), 403
    
    return jsonify({
        "erro" : "Nenhum usuário conectado foi encontrado."
    }), 401
    
#Rota para recuperar os próximos confrontros
@bet_bp.route('/next_round', methods=['GET'])
def get_next_round():
    if 'user_id' in session:
        
        conn = http.client.HTTPSConnection("v3.football.api-sports.io")    
        headers = {
            'x-rapidapi-host' : "v3.football.api-sports.io",
            'x-rapidapi-key': f"{api_key}"
        }
        
        conn.request("GET", "/fixtures?league=71&season=2024&next=10", headers=headers)
        
        res = conn.getresponse()
        data = res.read()
        
        if res.status == 200:
            fixtures = json.loads(data)
            filtered_fixtures = []
            
            for fixture in fixtures['response']:
                filtered_fixture = {
                    "match_id" : fixture['fixture']['id'],
                    "date" : fixture['fixture']['date'],
                    "home_team" : {
                        "id" : fixture['teams']['home']['id'],
                        "name" : fixture['teams']['home']['name'],
                        "logo" : fixture['teams']['home']['logo']
                    },
                    "away_team" : {
                        "id" : fixture['teams']['away']['id'],
                        "name" : fixture['teams']['away']['name'],
                        "logo" : fixture['teams']['away']['logo']
                    }
                }
                filtered_fixtures.append(filtered_fixture)
                
            return jsonify(filtered_fixtures), 200
        
        return jsonify({
            "erro" : "Não foi possível retornar os confrontos."
        }), res.status
        
    return jsonify({
        "erro" : "Nenhum usuário conectado foi encontrado."
    }), 401
    
#Rota para verificar resultado da aposta
@bet_bp.route('/check_bet/<group_id>/<match_id>', methods=['POST'])
def check_bet(group_id, match_id):
    if 'user_id' in session:
        user_id = session['user_id']
        bet_ref = db.collection('groups').document(group_id).collection('bets').where('match_id', '==', match_id).where('user_id', '==', user_id).stream()
        
        bets = list(bet_ref)
        if not bets:
            return jsonify({
                "erro" : "Aposta não encontrada."
            }), 404
        
        bet = bets[0].to_dict()
        
        conn = http.client.HTTPSConnection("v3.football.api-sports.io")
        headers = {
            'x-rapidapi-host' : "v3.football.api-sports.io",
            'x-rapidapi-key': f"{api_key}"
        }
        
        conn.request("GET", f"/fixtures?id={match_id}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        
        if res.status == 200:
            fixture = json.loads(data)['response'][0]
            
            home_score = fixture['goals']['home']
            away_score = fixture['goals']['away']
            
            if int(bet['bet']['fulltime']['home']) == home_score and int(bet['bet']['fulltime']['away']) == away_score:
                result = "ganhou"
            else:
                result = "perdeu"                
                
            bet_doc_ref = db.collection('groups').document(group_id).collection('bets').document(bets[0].id)
            bet_doc_ref.update({"result" : result})            
            return jsonify({
                "message" : f"{result} a aposta."
            }), 200
        
        return jsonify({
            "erro" : "Não foi possível obter o resultado da partida."
        }), res.status
        
    return jsonify({
        "erro" : "Nenhum usuário conectado foi encontrado."
    }), 401