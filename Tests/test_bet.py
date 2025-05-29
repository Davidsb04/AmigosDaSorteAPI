import json
from main import app
from unittest.mock import patch, MagicMock
import pytest


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = 'user123'
        yield client


def test_place_bet_success(client):
    with patch('controllers.bet.db') as mock_db:
        mock_group = MagicMock()
        mock_group.exists = True
        mock_group.to_dict.return_value = {'members': ['user123']}
        mock_db.collection.return_value.document.return_value.get.return_value = mock_group

        response = client.post('/bet/place_bet/group1/match123', json={
            'home_score': 2,
            'away_score': 1
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Aposta registrada com sucesso.'


def test_place_bet_missing_scores(client):
    response = client.post('/bet/place_bet/group1/match123', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'Placares da partida não inseridos.'


def test_place_bet_unauthorized(client):
    with patch("controllers.bet.db") as mock_db:
        mock_group = MagicMock()
        mock_group.exists = True
        mock_group.to_dict.return_value = {'members': ['outro_user']}
        mock_db.collection.return_value.document.return_value.get.return_value = mock_group

        response = client.post('/bet/place_bet/group1/match123', json={
            'home_score': 2,
            'away_score': 1
        })

        assert response.status_code == 403
        data = response.get_json()
        assert data['error'] == 'Usuário não autorizado ou grupo não encontrado.'


def test_next_round_success(client):
    fake_api_response = {
        "response": [{
            "fixture": {"id": 123, "date": "2024-06-12T20:00:00Z"},
            "teams": {
                "home": {"id": 1, "name": "Time A", "logo": "logoA"},
                "away": {"id": 2, "name": "Time B", "logo": "logoB"}
            }
        }]
    }

    with patch('http.client.HTTPSConnection') as mock_conn:
        mock_instance = mock_conn.return_value
        mock_instance.getresponse.return_value.status = 200
        mock_instance.getresponse.return_value.read.return_value = json.dumps(
            fake_api_response).encode()

        response = client.get('/bet/next_round')

        assert response.status_code == 200
        assert b'Time A' in response.data
        assert b'Time B' in response.data


def test_check_bet_win(client):
    fake_bet = {
        'bet': {'fulltime': {'home': 2, 'away': 1}},
        'result': 'aguardando resultado'
    }

    fake_fixture = {
        "response": [{
            "goals": {"home": 2, "away": 1}
        }]
    }

    with patch("controllers.bet.db") as mock_db, \
            patch("http.client.HTTPSConnection") as mock_conn:

        # Mock da busca da aposta
        mock_bet_doc = MagicMock()
        mock_bet_doc.to_dict.return_value = fake_bet
        mock_bet_doc.id = 'bet123'

        mock_db.collection.return_value \
            .document.return_value \
            .collection.return_value \
            .where.return_value \
            .where.return_value \
            .stream.return_value = [mock_bet_doc]

        # Mock da API externa
        mock_instance = mock_conn.return_value
        mock_instance.getresponse.return_value.status = 200
        mock_instance.getresponse.return_value.read.return_value = json.dumps(
            fake_fixture).encode()

        # Fazendo chamada para a rota
        response = client.post('/bet/check_bet/group1/match1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'ganhou a aposta.'


def test_check_bet_not_found(client):
    with patch("controllers.bet.db") as mock_db:
        mock_db.collection.return_value.document.return_value.collection.return_value.where.return_value.stream.return_value = []
        response = client.post('/bet/check_bet/group1/matchX')
        assert response.status_code == 404
        data = response.get_json()
        assert data['error'] == 'Aposta não encontrada.'
