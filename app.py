from gevent import monkey
monkey.patch_all()  # 무조건 1등으로 실행!

import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'giga_chad_chess_secret'

# async_mode를 'gevent'로 확실히 지정해서 에러 방지
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

@app.route('/')
def index():
    return render_template('index.html')

# 1. 로그인
@socketio.on('login')
def handle_login(data):
    username = data.get('username')
    if username:
        join_room(username)
        print(f"🔥 [LOGIN] User: {username}") # 로그인 로그 확인

# 2. 도전장 전송
@socketio.on('send_invite')
def handle_invite(data):
    sender = data.get('sender')
    target = data.get('target')
    if target:
        emit('receive_invite', {'from': sender}, room=target)
        print(f"📧 [INVITE] {sender} -> {target}") # 초대 로그 확인

# 3. 도전 수락 (게임 시작)
@socketio.on('accept_invite')
def handle_accept(data):
    inviter = data.get('from')
    accepter = data.get('to')
    room = f"game_{inviter}_{accepter}"
    join_room(room)
    
    # 초대한 사람도 해당 방에 조인하게 함 (통신을 위해 중요)
    emit('start_game', {'room': room, 'color': 'white'}, room=inviter)
    emit('start_game', {'room': room, 'color': 'black'}, room=accepter)
    print(f"🎮 [START] Room: {room} ({inviter} vs {accepter})") # 시작 로그 확인

# 4. 체스 말 이동 공유 (★로그 추가됨!)
@socketio.on('move')
def handle_move(data):
    room = data.get('room')
    move = data.get('move')
    
    # 실시간으로 누가 어떤 수를 뒀는지 서버 로그에 찍히게 함!
    print(f"📦 [MOVE] Room {room}: {move}") 
    
    # 상대방에게만 전송
    emit('opponent_move', {'move': move}, room=room, include_self=False)

if __name__ == '__main__':
    # Render는 환경 변수 PORT를 사용함
    port = int(os.environ.get("PORT", 10000)) 
    socketio.run(app, host='0.0.0.0', port=port)
