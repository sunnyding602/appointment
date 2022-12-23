from src.extensions import db
from flask import jsonify

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)

    def json(self) -> str:
        return jsonify({'id': self.id, 'name': self.name})

class WorkingHours(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_id = db.Column(db.Integer, nullable=False, unique=False)
    day_of_week = db.Column(db.Integer, nullable=False)
    start = db.Column(db.Integer, nullable=False)
    end = db.Column(db.Integer, nullable=False)

    def json(self) -> str:
        return jsonify({'doctor_id': self.doctor_id, 'day_of_week': self.day_of_week, 'start': self.start, 'end': self.end})

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_id = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    @property
    def serialize(self):
        return {'id': self.id, 'doctor_id': self.doctor_id, 'start_time': self.start_time, 'end_time': self.end_time}

    def json(self) -> str:
        return jsonify({'id': self.id, 'doctor_id': self.doctor_id, 'start_time': self.start_time, 'end_time': self.end_time})