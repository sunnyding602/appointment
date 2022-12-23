from collections import deque
from datetime import date
import datetime
from dateutil.relativedelta import relativedelta
from flask import Blueprint, jsonify
from http import HTTPStatus
from src.extensions import db
from src.models import Doctor, WorkingHours, Appointment
from webargs import fields
from webargs.flaskparser import use_args
import sys


home = Blueprint('/', __name__)


# Helpful documentation:
# https://webargs.readthedocs.io/en/latest/framework_support.html
# https://flask.palletsprojects.com/en/2.0.x/quickstart/#variable-rules


@home.route('/')
def index():
    db.session.add(Doctor(name='Strange'))
    db.session.add(Doctor(name='Who'))

    db.session.add(WorkingHours(doctor_id=1,day_of_week=0, start=9, end=17))
    db.session.add(WorkingHours(doctor_id=1,day_of_week=1, start=9, end=17))
    db.session.add(WorkingHours(doctor_id=1,day_of_week=2, start=9, end=17))
    db.session.add(WorkingHours(doctor_id=1,day_of_week=3, start=9, end=17))
    db.session.add(WorkingHours(doctor_id=1,day_of_week=4, start=9, end=17))

    db.session.add(WorkingHours(doctor_id=2,day_of_week=0, start=8, end=16))
    db.session.add(WorkingHours(doctor_id=2,day_of_week=1, start=8, end=16))
    db.session.add(WorkingHours(doctor_id=2,day_of_week=2, start=8, end=16))
    db.session.add(WorkingHours(doctor_id=2,day_of_week=3, start=8, end=16))
    db.session.add(WorkingHours(doctor_id=2,day_of_week=4, start=8, end=16))
    db.session.commit()
    return {'data': 'OK'}

# print('This is standard output', file=sys.stdout)


@home.route('/appointment', methods=['POST'])
@use_args({'doctor_id':fields.Integer(), 'start_time': fields.DateTime(), 'end_time': fields.DateTime()})
def appointment_create(args):
    start_time = args.get('start_time')
    end_time = args.get('end_time')
    if start_time >= end_time:
        return jsonify(None), HTTPStatus.NOT_ACCEPTABLE
    
    existing_appointments = Appointment.query.filter(
        Appointment.doctor_id == args.get('doctor_id'), 
        Appointment.start_time > start_time.date(),
        Appointment.end_time < end_time.date() + relativedelta(days=1)
        ).all()
    
    intervals = []
    intervals.append((start_time, end_time))
    for appt in existing_appointments:
        intervals.append((appt.start_time, appt.end_time))
    
    def has_overlap(intervals):
        intervals.sort()
        for i in range(len(intervals) - 1):
            if intervals[i][1] > intervals[i + 1][0]:
                return True
        return False

    if has_overlap(intervals):
        return jsonify(None), HTTPStatus.NOT_FOUND
    appointment = Appointment(doctor_id=args.get('doctor_id'),start_time=start_time, end_time=end_time)
    db.session.add(appointment)
    db.session.commit()
    return appointment.json()

@home.route('/appointments', methods=['GET'])
@use_args({'doctor_id':fields.Integer(), 'start_time': fields.DateTime(), 'end_time': fields.DateTime()})
def appointments(args):
    result = Appointment.query.filter(
        Appointment.doctor_id == args.get('doctor_id'), 
        Appointment.start_time >= args.get('start_time'), 
        Appointment.end_time <= args.get('end_time')
        ).all()
    print(result)
    return jsonify([appointment.serialize for appointment in result])

@home.route('/first_available_appointment', methods=['GET'])
@use_args({'doctor_id':fields.Integer(), 'start_time': fields.DateTime(), 'duration': fields.Integer()})
def first_available_appointment(args):
    # start_date should >= today

    working_hours_map = {}
    working_hours_map[1] = (9, 17)
    working_hours_map[2] = (8, 16)

    result = None
    doctor_id = args.get('doctor_id')
    duration = args.get('duration')
    start_time = args.get('start_time')
    after_a_month = start_time + relativedelta(months=1)

    # 1. get working hours
    _datetime = start_time
    working_hours = []
    for i in range((after_a_month-start_time).days):
        _datetime = start_time + relativedelta(days=i)
        if _datetime.weekday() < 5:
            working_hours.append({
                _datetime.date(): ( 
                    _datetime.date() + relativedelta(hours=working_hours_map[doctor_id][0]),
                    _datetime.date() + relativedelta(hours=working_hours_map[doctor_id][1])
                    )})
    # 2. get appointments and merge intervals
    appointments = Appointment.query.filter(Appointment.doctor_id == doctor_id, Appointment.start_time >= start_time, Appointment.end_time <= after_a_month).all()
    appointment_hours = {}
    for appointment in appointments:
        if appointment.start_time.date() not in appointment_hours:
            appointment_hours[appointment.start_time.date()] = []
        appointment_hours[appointment.start_time.date()].append([appointment.start_time, appointment.end_time])
 
    def merge(intervals):
        intervals.sort(key=lambda x: x[0])
        merged = []
        for interval in intervals:
            if not merged or merged[-1][1] < interval[0]:
                merged.append(interval)
            else:
                merged[-1][1] = max(merged[-1][1], interval[1])
        return merged

    for key, value in appointment_hours.items():
        appointment_hours[key] = merge(value)
    
    # 3. calculate first available appointment
    for working_hour in working_hours:
        de = deque([])  
        for working_date, hours in working_hour.items():
            if working_date in appointment_hours:
                for interval in appointment_hours[working_date]:
                    de.append(interval) 

                    
        de.appendleft([working_date + relativedelta(hours=working_hours_map[doctor_id][0]), working_date + relativedelta(hours=working_hours_map[doctor_id][0])])
        de.append([working_date + relativedelta(hours=working_hours_map[doctor_id][1]), working_date + relativedelta(hours=working_hours_map[doctor_id][1])])
        # deque([[900, 945], [1030, 1400], [1700, 1700]])
        for i in range(1, len(de)):
            # print(working_date, de[i-1][1], de[i][0]) # available duration
            if (de[i][0] - de[i-1][1]) >= datetime.timedelta(minutes=duration):
                result = {str(working_date) : [de[i-1][1], de[i-1][1] + relativedelta(minutes=duration)]}
                return jsonify(result)
            
    return jsonify(result)
