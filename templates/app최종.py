from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import uuid

app = Flask(__name__, template_folder='.')
app.config['SECRET_KEY'] = 'gigachad_chess_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# 접속 중인 유저 데이터 {사용자명: 소켓ID}
users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('login')
def handle_login(data):
    username = data['username']
    if not username:
        return
    users[username] = request.sid
    print(f"--- [로그인 성공] 유저: {username} | SID: {request.sid} ---")
    print(f"현재 접속자 명단: {list(users.keys())}")

@socketio.on('send_invite')
def handle_invite(data):
    sender = data['sender']
    target = data['target']
    
    print(f" [초대 시도] {sender} -> {target}")
    
    if target in users:
        # 상대방에게 초대 이벤트 전송
        emit('receive_invite', {'from': sender}, room=users[target])
        print(f" [전송 완료] {target}에게 도전장을 보냈음.")
    else:
        # 보낸 사람에게 에러 알림
        emit('error_msg', {'msg': f"'{target}' 유저를 찾을 수 없다. (오프라인)"}, room=request.sid)
        print(f" [전송 실패] {target}이 접속자 명단에 없음.")

@socketio.on('accept_invite')
def handle_accept(data):
    sender = data['from']
    acceptor = data['to']
    
    room_id = str(uuid.uuid4())[:8]
    join_room(room_id, sid=users[sender])
    join_room(room_id, sid=users[acceptor])
    
    emit('start_game', {'room': room_id, 'color': 'white'}, room=users[sender])
    emit('start_game', {'room': room_id, 'color': 'black'}, room=users[acceptor])
    print(f" [게임 시작] 방 ID: {room_id} ({sender} vs {acceptor})")

@socketio.on('move')
def handle_move(data):
    emit('opponent_move', {'move': data['move']}, room=data['room'], include_self=False)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)