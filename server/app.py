#!/usr/bin/env python3

from models import User
from flask_migrate import Migrate
from flask import Flask, request, session
from flask_restful import Resource
from config import app, db, api


class Signup(Resource):

    def post(self):
        username = request.get_json().get('username')
        password = request.get_json().get('password')

        if username and password and not User.query.filter(User.username == username).first():
            new_user = User(username = username)
            new_user.password_hash = password
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return new_user.to_dict(), 201
        
        return {'error': '422 Unprocessable Entity'}, 422
    

class Login(Resource):

    def post(self):

        data = request.get_json()
        username = data['username']
        password = data['password']

        user = User.query.filter(User.username == username).first()

        if user:
            if user.authenticate(password):
                session['user_id'] = user.id
                return user.to_dict(), 200
        
        return {'error': "Unauthorized"}, 401

class CheckSession(Resource):

    def get(self):
        if session.get('user_id'):
            user = User.query.filter(User.id == session.get('user_id')).first()
            return user.to_dict(), 200
        return {'error': 'Unauthorized'}, 401

class Logout(Resource):

    def delete(self):

        if session.get('user_id'):
            session['user_id'] = None
            return {}, 204
        
        return {'error': 'Unauthorized'}, 401

api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')

if __name__ == '__main__':
    app.run(port=5555, debug=False)
