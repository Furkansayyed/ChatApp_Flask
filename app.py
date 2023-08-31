from flask import Flask, redirect, render_template, request
import time
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///chatapp.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)
socketio = SocketIO(app)

class ChatRoom(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    room = db.Column(db.String(200), nullable=False)

    def __repr__(self) -> str:
        return f" {self.room} "

class Messages(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    userName = db.Column(db.String(100), nullable=False)
    roomName = db.Column(db.String(200), nullable=False)
    message =  db.Column(db.String(1500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    # date_created = db.Column(db.DateTime, default=datetime.utcnow)        

with app.app_context():    
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def chatRoomName():
    if request.method == "POST":
        room = request.form['roomname']
        global rname 
        rname = room
        chatroom = ChatRoom(room=room)
        db.session.add(chatroom)
        db.session.commit()
        todo = ChatRoom.query.filter_by(room=rname).all()
        return redirect(f"/chatroom/")
        # return render_template(f"/chatroom/{rname}", data=todo)
    return render_template("index.html")  # For returning html

@socketio.on('message')
def handle_message(data):
    username = data['username']
    content = data['content']
    msg = Messages(userName=username,roomName=rname, message=content)
    db.session.add(msg)
    db.session.commit()
    emit('message', {'content': content}, broadcast=True)
    emit('message', {'username': username, 'content': content}, broadcast=True)

@app.route("/chatroom/")
def chats():  
    todo = Messages.query.filter_by(roomName=rname).all() 
    return render_template("chatroom.html", data2=todo)

if __name__ == "__main__":
    app.run(debug=True)
