import requests
import socketio

# Настройки сервера
SERVER_URL = "http://127.0.0.1:5000"
USERNAME = "user1"
PASSWORD = "mypassword"

# HTTP-клиент для авторизации
session = requests.Session()

# Регистрация пользователя
response = session.post(f"{SERVER_URL}/register", json={"username": USERNAME, "password": PASSWORD})
if response.status_code == 201:
    print("Registration successful")
else:
    print("Registration failed (possibly already registered):", response.json())

# Авторизация через HTTP
response = session.post(f"{SERVER_URL}/login", json={"username": USERNAME, "password": PASSWORD})
if response.status_code == 200:
    print("Login successful")
else:
    print("Login failed:", response.json())
    exit()

# WebSocket-клиент
sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print("Connected to the server")

@sio.on('receive_message')
def on_message(data):
    print(f"New message from {data['user']}: {data['content']}")

@sio.on('status')
def on_status(data):
    print(f"Status: {data['message']}")

@sio.on('error')
def on_error(data):
    print(f"Error: {data}")

# Подключение к WebSocket с использованием куки из HTTP-сессии
try:
    sio.connect(SERVER_URL, headers={"Cookie": "; ".join([f"{key}={value}" for key, value in session.cookies.get_dict().items()])})
except Exception as e:
    print(f"Unable to connect to the server: {e}")
    exit()

# Основное меню
try:
    while True:
        print("\nOptions:")
        print("1. Send a message")
        print("2. Join a room")
        print("3. Leave a room")
        print("4. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            message = input("Enter your message: ")
            sio.emit('send_message', {'message': message})
        elif choice == "2":
            room = input("Enter room name to join: ")
            sio.emit('join', {'room': room})
        elif choice == "3":
            room = input("Enter room name to leave: ")
            sio.emit('leave', {'room': room})
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")
except KeyboardInterrupt:
    print("\nDisconnected from the server.")
finally:
    sio.disconnect()
