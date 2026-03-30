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

# 3. 도전 수락 (게임 시작 세팅)
@socketio.on('accept_invite')
def handle_accept(data):
    inviter = data.get('from')   # 초대한 사람 (예: 'a')
    accepter = data.get('to')    # 수락한 사람 (예: 'b')
    
    room = f"game_{inviter}_{accepter}"
    
    # [핵심 수정] 초대한 사람의 SID를 찾아서 방에 넣는 대신, 
    # 양쪽 클라이언트가 'start_game'을 받으면 스스로 방에 들어오게 유도하는 게 가장 확실함.
    # 일단 수락한 본인(흑)은 여기서 바로 입장
    join_room(room)
    
    # 양쪽 유저에게 시작 신호 보냄
    emit('start_game', {'room': room, 'color': 'white'}, room=inviter)
    emit('start_game', {'room': room, 'color': 'black'}, room=accepter)
    
    print(f"🎮 [START] Room: {room} ({inviter} vs {accepter})")

# [추가] 클라이언트가 방에 직접 조인할 수 있는 전용 통로
@socketio.on('join_chess_room')
def handle_join_chess_room(data):
    room = data.get('room')
    if room:
        join_room(room)
        print(f"✅ [JOIN] User joined: {room}")

# 4. 체스 말 이동 공유
@socketio.on('move')
def handle_move(data):
    room = data.get('room')
    move = data.get('move')
    
    if room:
        print(f"📦 [MOVE] Room {room}: {move}") 
        # room=room으로 쏘면 해당 방의 모든 사람(나 제외)에게 전달됨
        emit('opponent_move', {'move': move}, room=room, include_self=False)

if __name__ == '__main__':
    # Render는 환경 변수 PORT를 사용함
    port = int(os.environ.get("PORT", 10000)) 
    socketio.run(app, host='0.0.0.0', port=port)
