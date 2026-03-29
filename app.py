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

# 1. 로그인 (사용자가 이름을 입력하고 접속했을 때)
@socketio.on('login')
def handle_login(data):
    username = data.get('username')
    if username:
        # 사용자의 ID 자체를 '방 이름'으로 설정해서 1:1 메시지를 받을 수 있게 함
        join_room(username)
        print(f"🔥 [LOGIN] User: {username}")

# 2. 도전장 전송 (상대방 ID를 타겟으로 보낼 때)
@socketio.on('send_invite')
def handle_invite(data):
    sender = data.get('sender')
    target = data.get('target')
    
    if target:
        # target(받는 사람)의 ID 방으로만 신호를 보냄
        emit('receive_invite', {'from': sender}, room=target)
        print(f"📧 [INVITE] {sender} -> {target}")

# 3. 도전 수락 (게임 시작 세팅)
@socketio.on('accept_invite')
def handle_accept(data):
    inviter = data.get('from')  # 초대한 사람
    accepter = data.get('to')    # 수락한 사람 (나)
    
    # 두 사람이 함께 쓸 게임 방 생성
    room = f"game_{inviter}_{accepter}"
    join_room(room)
    
    # 초대한 사람도 방에 넣어야 하므로 신호를 보냄 (이건 프론트에서 처리하거나 서버에서 강제 조인)
    # 여기서는 간단하게 두 명에게 게임 시작 알림을 보냄
    emit('start_game', {'room': room, 'color': 'white'}, room=inviter)
    emit('start_game', {'room': room, 'color': 'black'}, room=accepter)
    print(f"🎮 [START] Room: {room} ({inviter} vs {accepter})")

# 4. 체스 말 이동 공유
@socketio.on('move')
def handle_move(data):
    room = data.get('room')
    move = data.get('move')
    # 내가 아닌 상대방에게만 이동 경로 전송
    emit('opponent_move', {'move': move}, room=room, include_self=False)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000)) # Render는 보통 10000 포트 사용
    socketio.run(app, host='0.0.0.0', port=port)
