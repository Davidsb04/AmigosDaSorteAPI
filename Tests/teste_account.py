import pytest
from unittest.mock import patch, MagicMock
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = 'user123'
            sess['email'] = 'user@email.com'
            sess['username'] = 'user123'
        yield client


def test_get_all_users_success(client):
    with patch('data.firebaseConfig.db') as mock_db:
        mock_user = MagicMock()
        mock_user.to_dict.return_value = {'name': 'User'}
        mock_db.collection.return_value.stream.return_value = [mock_user]

        response = client.get('/users')
        assert response.status_code == 200
        assert b'User' in response.data

def test_get_all_users_empty(client):
    with patch('data.firebaseConfig.db') as mock_db:
        mock_db.collection.return_value.stream.return_value = []
        response = client.get('/users')
        assert response.status_code == 404
        assert b'Nenhum usuario cadastrado' in response.data

def test_get_all_users_unauthorized():
    with app.test_client() as client:
        response = client.get('/users')
        assert response.status_code == 401
        assert b'Nenhum usuario conectado' in response.data


def test_get_user_found(client):
    with patch('data.firebaseConfig.db') as mock_db:
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {'name': 'User'}
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        response = client.get('/user/user123')
        assert response.status_code == 200
        assert b'User' in response.data

def test_get_user_not_found(client):
    with patch('data.firebaseConfig.db') as mock_db:
        mock_doc = MagicMock()
        mock_doc.exists = False
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        response = client.get('/user/unknown')
        assert response.status_code == 404
        assert b'usuario nao encontrado' in response.data


def test_create_user_success(client):
    with patch('data.firebaseConfig.db') as mock_db, \
         patch('helpers.passwordUtils.hash_password', return_value='hashed'), \
         patch('helpers.userHelper.is_unique_email', return_value=True), \
         patch('helpers.userHelper.is_unique_username', return_value=True):

        response = client.post('/create_user', json={
            'name': 'User',
            'email': 'user@email.com',
            'username': 'user123',
            'password': '123456'
        })
        assert response.status_code == 201
        assert b'usuario criado com sucesso' in response.data

def test_create_user_missing_fields(client):
    response = client.post('/create_user', json={})
    assert response.status_code == 400
    assert b'Todos os campos sao obrigatorios' in response.data

def test_create_user_email_not_unique(client):
    with patch('helpers.userHelper.is_unique_email', return_value=False):
        response = client.post('/create_user', json={
            'name': 'User',
            'email': 'existing@email.com',
            'username': 'user123',
            'password': '123456'
        })
        assert response.status_code == 409
        assert b'e-mail ja esta sendo utilizado' in response.data

def test_create_user_username_not_unique(client):
    with patch('helpers.userHelper.is_unique_email', return_value=True), \
         patch('helpers.userHelper.is_unique_username', return_value=False):
        response = client.post('/create_user', json={
            'name': 'User',
            'email': 'user@email.com',
            'username': 'existing_user',
            'password': '123456'
        })
        assert response.status_code == 409
        assert b'nome de usuario ja esta sendo utilizado' in response.data


def test_update_user_success(client):
    with patch('data.firebaseConfig.db') as mock_db, \
         patch('helpers.userHelper.is_unique_email_update', return_value=True), \
         patch('helpers.userHelper.is_unique_username_update', return_value=True):

        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        response = client.put('/update_user', json={
            'name': 'New Name',
            'email': 'new@email.com',
            'username': 'newuser'
        })
        assert response.status_code == 200
        assert b'Dados do usuario atualizado' in response.data

def test_update_user_conflict_email(client):
    with patch('helpers.userHelper.is_unique_email_update', return_value=False):
        response = client.put('/update_user', json={
            'name': 'User',
            'email': 'conflict@email.com',
            'username': 'user123'
        })
        assert response.status_code == 409
        assert b'e-mail ja esta sendo utilizado' in response.data

def test_update_user_missing_fields(client):
    response = client.put('/update_user', json={})
    assert response.status_code == 400
    assert b'Todos os campos sao obrigatorios' in response.data


def test_delete_user_success(client):
    with patch('data.firebaseConfig.db') as mock_db:
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        response = client.delete('/delete_user')
        assert response.status_code == 204

def test_delete_user_not_found(client):
    with patch('data.firebaseConfig.db') as mock_db:
        mock_doc = MagicMock()
        mock_doc.exists = False
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        response = client.delete('/delete_user')
        assert response.status_code == 404
        assert b'Usuario nao encontrado' in response.data
