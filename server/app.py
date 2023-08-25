#!/usr/bin/env python3

from models import User, Calendar, Event, List, Task
from flask_migrate import Migrate
from flask import Flask, request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from config import app, db, api
from datetime import datetime


@app.route('/')
def home():
    return '<h1>Home Page</h1>'

class Signup(Resource):

    def post(self):
        username = request.get_json().get('username')
        password = request.get_json().get('password')
        date_time = datetime.now()
        new_calendar = Calendar(year = date_time.year)

        if username and password and not User.query.filter(User.username == username).first():
            new_user = User(username = username)
            new_user.password_hash = password
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            new_calendar.user_id = new_user.id
            db.session.add(new_calendar)
            db.session.commit()
            return new_calendar.to_dict(rules=('user',)), 201
        
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
    
class GetCalendar(Resource):

    def get(self):

        if session.get('user_id'):

            calendar = Calendar.query.filter(Calendar.user_id == session['user_id']).first()

            if calendar:
                return calendar.to_dict(), 200
            return {'error': 'No calendart found'}, 404

        return {'error': 'Unauthorized'}, 401

    
class Lists(Resource):

    def get(self):

        if session.get('user_id'):
            lists = List.query.filter(List.user_id == session['user_id'])
            if lists:
                return [l.to_dict() for l in lists], 200
            return {'error': 'No lists found'}, 404
        
    def post(self):

        if session.get('user_id'):
            name = request.get_json().get('name')
            user_id = session['user_id']
            try:
                new_list = List(name=name, user_id=user_id)
                db.session.add(new_list)
                db.session.commit()
                return new_list.to_dict()
            
            except IntegrityError:
                return {'error': 'Error in creating list'}, 422
                
        return {'error': 'Must be logged in to create a new list'}, 401
    
class ListById(Resource):
    
    def get(self, id):

        if session.get('user_id'):
            list = List.query.filter(List.user_id == session['user_id'] and List.id == id).first()
            if list:
                return list.to_dict(rules=('tasks',)), 200
            return {'error', 'List not found'}, 404
        return {'error', 'Must be logged in to retrieve lists'}, 401
    
    def patch(self, id):

        if session.get('user_id'):
            list = List.query.filter(List.user_id == session['user_id'] and List.id == id).first()
            if list:
                setattr(list, 'name', request.get_json()['name'])
                db.session.add(list)
                db.session.commit()
                return list.to_dict(rules=('tasks',)), 202
            return {'error': 'List not found'}, 404
        return {'error': 'Unauthorized'}, 401
    
    def delete(self, id):

        if session.get('user_id'):
            list = List.query.filter(List.user_id == session['user_id'] and List.id == id).first()
            if list:
                db.session.delete(list)
                db.session.commit()
                return {'Message': "List deleted"}, 204 
            return {'error': 'List not found'}, 404
        
    def post(self, id):

        if session.get('user_id'):

            try:
                new_task = Task(
                    description = request.get_json()['description'],
                    list_id = id,
                    status = 0,
                    updated = datetime.utcnow()
                )

                db.session.add(new_task)
                db.session.commit()

                return List.query.filter(List.id == id and User.id == session['user_id']).first().to_dict(rules=('tasks',)), 201
            
            except IntegrityError:

                return {'error': "Couldn't create task"}, 422
        
        return {'error': 'Must be logged in to create tasks'}, 401 


class TaskById(Resource):

    def get(self, id):

        if session.get('user_id'):
            task = Task.query.filter(Task.id == id and Task.list.user_id == session['user_id']).first()
            if task:
                return task.to_dict(), 200
            return {'error': 'Task not found'}, 404
        return {'error': 'Unauthoriezed'}, 401
    

    def patch(self, id):

        if session.get('user_id'):
            
            task = Task.query.filter(Task.id == id and Task.list.user_id == session['user_id']).first()

            if task:
                status = request.get_json()['status'] if request.get_json()['status'] == 1 or request.get_json()['status'] == 0 else 0
                setattr(task, 'description', request.get_json()['description'])
                setattr(task, 'status', status)
                setattr(task, 'updated' , datetime.utcnow())
                db.session.add(task)
                db.session.commit()
                return task.to_dict(), 200
            return {'error': 'Task not found'}, 404
        return {'error': 'Must be logged in to modify tasks'}, 401
    
    def delete(self, id):

        if session.get('user_id'):
            task = Task.query.filter(Task.id == id and Task.list.user_id == session['user_id']).first()
            if task:
                db.session.delete(task)
                db.session.commit()
                return {'Message':'Task deleted'}, 204
            return {'error': 'Task not found'}, 404
        return {'error': 'Must be logged in'}, 401

api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Lists, '/list', endpoint='list')
api.add_resource(ListById, '/list/<int:id>')
api.add_resource(TaskById, '/task/<int:id>')
api.add_resource(GetCalendar, '/calendar')

if __name__ == '__main__':
    app.run(port=5555, debug=False)
