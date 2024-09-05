import random
from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)

messages = []
users = {}

colors = ["#FF5733", "#33FF57", "#3357FF", "#FF33A5", "#33FFF5"]

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('username')
def handle_username(username):
    color = random.choice(colors)
    users[request.sid] = {'username': username, 'color': color}
    emit('message_history', messages)
    send({'msg': f'{username} приєднався(-лась) до чату.', 'color': '#000000'}, broadcast=True)

@socketio.on('message')
def handle_message(msg):
    user = users.get(request.sid, {"username": "Анонім", "color": "#000000"})
    full_msg = {'msg': f'{user["username"]}: {msg}', 'color': user['color']}
    messages.append(full_msg)
    send(full_msg, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    user = users.pop(request.sid, {"username": "Анонім", "color": "#000000"})
    send({'msg': f'{user["username"]} залишив чат.', 'color': '#000000'}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
