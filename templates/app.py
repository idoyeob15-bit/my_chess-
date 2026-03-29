import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'giga_chad_chess_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

# 사용자가 접속했을 때 실행
@socketio.on('join')
def on_join(data):
    username = data.get('username', 'Guest')
    room = data.get('room', 'default_room') # 방 이름
    join_room(room)
    print(f"{username} joined room: {room}")

# 초대를 보낼 때 실행
@socketio.on('send_invitation')
def handle_invitation(data):
    room = data.get('room', 'default_room')
    sender = data.get('username', 'Someone')
    # 특정 방(room)에 있는 모든 사람에게 'receive_invitation' 신호를 보냄
    emit('receive_invitation', {'sender': sender}, room=room)

if __name__ == '__main__':
    # Render가 주는 포트 번호를 받아서 실행해야 한다
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
