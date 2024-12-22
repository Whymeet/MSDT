from flask import Flask, request, jsonify, session
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room, leave_room
# from cachelib.file import FileSystemCache   # Можно убрать, если не используете
import uuid

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# 1) Используем "filesystem", чтобы избежать ошибки Unrecognized value
app.config['SESSION_TYPE'] = 'filesystem'
# 2) Если хотите хранить файлы в отдельном месте, задайте папку
# app.config['SESSION_FILE_DIR'] = '/tmp/flask_session_cache'

Session(app)

socketio = SocketIO(app, manage_session=True)

users = {}

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    if username in users:
        return jsonify({'error': 'User already exists'}), 400

    users[username] = password
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    if username not in users or users[username] != password:
        return jsonify({'error': 'Invalid username or password'}), 401

    session['user'] = username
    return jsonify({'message': 'Login successful'}), 200

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'message': 'Logout successful'}), 200

@socketio.on('send_message')
def handle_send_message(data):
    if 'user' not in session:
        emit('error', {'error': 'Unauthorized'}, to=request.sid)
        return

    username = session['user']
    message_content = data.get('message')

    if not message_content:
        emit('error', {'error': 'Message content is required'}, to=request.sid)
        return

    message = {
        'id': str(uuid.uuid4()),
        'user': username,
        'content': message_content
    }
    emit('receive_message', message, broadcast=True)

@socketio.on('join')
def handle_join(data):
    if 'user' not in session:
        emit('error', {'error': 'Unauthorized'}, to=request.sid)
        return

    room = data.get('room')
    if not room:
        emit('error', {'error': 'Room name is required'}, to=request.sid)
        return

    join_room(room)
    emit('status', {'message': f'{session["user"]} has joined the room {room}'}, room=room)

@socketio.on('leave')
def handle_leave(data):
    if 'user' not in session:
        emit('error', {'error': 'Unauthorized'}, to=request.sid)
        return

    room = data.get('room')
    if not room:
        emit('error', {'error': 'Room name is required'}, to=request.sid)
        return

    leave_room(room)
    emit('status', {'message': f'{session["user"]} has left the room {room}'}, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
