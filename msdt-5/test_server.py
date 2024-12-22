import pytest
from flask import session
from server import app, socketio
from flask_socketio import SocketIOTestClient

def setup_module(module):
    app.testing = True
    module.client = app.test_client()
    module.socket_client = SocketIOTestClient(app, socketio, flask_test_client=app.test_client())

def teardown_module(module):
    module.socket_client.disconnect()

@pytest.fixture
def test_client():
    return app.test_client()

@pytest.fixture
def socket_test_client():
    flask_client = app.test_client()
    client = SocketIOTestClient(app, socketio, flask_test_client=flask_client)
    # Авторизация пользователя
    response = flask_client.post('/register', json={"username": "roomuser", "password": "testpass"})
    assert response.status_code in [201, 400]  # 201 - успешно, 400 - пользователь уже существует
    response = flask_client.post('/login', json={"username": "roomuser", "password": "testpass"})
    assert response.status_code == 200

    # Получение сессионных куки
    cookies = flask_client.cookie_jar._cookies['localhost.local']['/']
    session_cookie = cookies.get('session').value

    # Передача сессионных куки в заголовок WebSocket
    client.connect(headers={"Cookie": f"session={session_cookie}"})
    return client

# 1. Test Registration Success
def test_registration_success(test_client):
    response = test_client.post('/register', json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 201
    assert response.get_json()["message"] == "User registered successfully"

# 2. Test Registration Failure (User Already Exists)
def test_registration_failure_user_exists(test_client):
    test_client.post('/register', json={"username": "testuser", "password": "testpass"})
    response = test_client.post('/register', json={"username": "testuser", "password": "newpass"})
    assert response.status_code == 400
    assert response.get_json()["error"] == "User already exists"

# 3. Test Login Success
def test_login_success(test_client):
    test_client.post('/register', json={"username": "loginuser", "password": "loginpass"})
    response = test_client.post('/login', json={"username": "loginuser", "password": "loginpass"})
    assert response.status_code == 200
    assert response.get_json()["message"] == "Login successful"

# 4. Test Login Failure (Invalid Credentials)
def test_login_failure_invalid_credentials(test_client):
    response = test_client.post('/login', json={"username": "nonexistent", "password": "wrongpass"})
    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid username or password"

# 5. Test WebSocket Unauthorized Message
def test_websocket_unauthorized_message():
    unauth_client = SocketIOTestClient(app, socketio)
    unauth_client.emit('send_message', {'message': 'Test message'})
    received = unauth_client.get_received()
    unauth_client.disconnect()
    assert any(event["name"] == "error" and event["args"][0]["error"] == "Unauthorized" for event in received)

# 6. Test WebSocket Room Join and Broadcast
def test_websocket_join_room(socket_test_client):
    socket_test_client.emit('join', {'room': 'testroom'})
    received = socket_test_client.get_received()
    print("Received events (join):", received)
    assert any(event["name"] == "status" and "roomuser has joined the room" in event["args"][0]["message"] for event in received)

# 7. Parametrized Test for Missing Fields
@pytest.mark.parametrize("endpoint, payload, expected_status, expected_error", [
    ('/register', {"username": "user1"}, 400, "Username and password are required"),
    ('/register', {"password": "pass1"}, 400, "Username and password are required"),
    ('/login', {"username": "user1"}, 400, "Username and password are required"),
    ('/login', {"password": "pass1"}, 400, "Username and password are required"),
])
def test_missing_fields(test_client, endpoint, payload, expected_status, expected_error):
    response = test_client.post(endpoint, json=payload)
    assert response.status_code == expected_status
    assert response.get_json()["error"] == expected_error

# 8. Test Logout Functionality
def test_logout(test_client):
    test_client.post('/register', json={"username": "logoutuser", "password": "logoutpass"})
    test_client.post('/login', json={"username": "logoutuser", "password": "logoutpass"})
    response = test_client.post('/logout')
    assert response.status_code == 200
    assert response.get_json()["message"] == "Logout successful"

@pytest.fixture
def socket_test_client():
    flask_client = app.test_client()
    client = SocketIOTestClient(app, socketio, flask_test_client=flask_client)

    # 1. Регистрируем пользователя
    response = flask_client.post('/register', json={"username": "roomuser", "password": "testpass"})
    assert response.status_code in [201, 400]

    # 2. Логинимся — получаем ответ, содержащий Set-Cookie
    response = flask_client.post('/login', json={"username": "roomuser", "password": "testpass"})
    assert response.status_code == 200

    # 3. Считываем заголовок "Set-Cookie" из ответа
    set_cookie_header = response.headers.get("Set-Cookie")
    assert set_cookie_header is not None, "No Set-Cookie header found after login"

    # 4. Подключаемся по WebSocket, передавая "Cookie" из шага логина
    client.connect(headers={"Cookie": set_cookie_header})

    return client
