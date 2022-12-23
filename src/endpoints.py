from collections import deque
from datetime import date
from dateutil.relativedelta import relativedelta
from flask import Blueprint, jsonify
from http import HTTPStatus
from src.extensions import db
from src.models import DummyModel, Doctor, WorkingHours, Appointment
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

    db.session.add(WorkingHours(doctor_id=1,day_of_week=0, start=900, end=1700))
    db.session.add(WorkingHours(doctor_id=1,day_of_week=1, start=900, end=1700))
    db.session.add(WorkingHours(doctor_id=1,day_of_week=2, start=900, end=1700))
    db.session.add(WorkingHours(doctor_id=1,day_of_week=3, start=900, end=1700))
    db.session.add(WorkingHours(doctor_id=1,day_of_week=4, start=900, end=1700))

    db.session.add(WorkingHours(doctor_id=2,day_of_week=0, start=800, end=1600))
    db.session.add(WorkingHours(doctor_id=2,day_of_week=1, start=800, end=1600))
    db.session.add(WorkingHours(doctor_id=2,day_of_week=2, start=800, end=1600))
    db.session.add(WorkingHours(doctor_id=2,day_of_week=3, start=800, end=1600))
    db.session.add(WorkingHours(doctor_id=2,day_of_week=4, start=800, end=1600))
    db.session.commit()
    return {'data': 'OK'}


@home.route('/dummy_model/<id_>', methods=['GET'])
def dummy_model(id_):
    record = DummyModel.query.filter_by(id=id_).first()
    if record is not None:
        return record.json()
    else:
        return jsonify(None), HTTPStatus.NOT_FOUND


@home.route('/dummy_model', methods=['POST'])
@use_args({'value': fields.String()})
def dummy_model_create(args):
    # print('This is standard output', file=sys.stdout)
    new_record = DummyModel(value=args.get('value'))
    db.session.add(new_record)
    db.session.commit()
    return new_record.json()


@home.route('/appointment', methods=['POST'])
@use_args({'doctor_id':fields.Integer(), 'date': fields.Date(), 'start': fields.Integer(), 'end': fields.Integer()})
def appointment_create(args):
    existing_appointments = Appointment.query.filter(Appointment.doctor_id == args.get('doctor_id'), Appointment.date == args.get('date')).all()
    
    intervals = []
    intervals.append((args.get('start'), args.get('end')))
    for appt in existing_appointments:
        intervals.append((appt.start, appt.end))

    def has_overlap(intervals):
        intervals.sort()
        for i in range(len(intervals) - 1):
            if intervals[i][1] > intervals[i + 1][0]:
                return True
        return False

    if has_overlap(intervals):
        return jsonify(None), HTTPStatus.NOT_FOUND
    appointment = Appointment(doctor_id=args.get('doctor_id'),date=args.get('date'), start=args.get('start'), end=args.get('end'))
    db.session.add(appointment)
    db.session.commit()
    return appointment.json()

@home.route('/appointments', methods=['GET'])
@use_args({'doctor_id':fields.Integer(), 'start_date': fields.Date(), 'end_date': fields.Date()})
def appointments(args):
    result = Appointment.query.filter(Appointment.doctor_id == args.get('doctor_id'), Appointment.date >= args.get('start_date'), Appointment.date <= args.get('end_date')).all()
    return jsonify([appointment.serialize for appointment in result])

@home.route('/first_available_appointment', methods=['GET'])
@use_args({'doctor_id':fields.Integer(), 'start_date': fields.Date(), 'duration': fields.Integer()})
def first_available_appointment(args):
    # start_date should >= today

    working_hours_map = {}
    working_hours_map[1] = (900, 1700)
    working_hours_map[2] = (800, 1600)

    result = None
    doctor_id = args.get('doctor_id')
    duration = args.get('duration')
    start_date = args.get('start_date')
    after_a_month = start_date + relativedelta(months=1)

    # 1. get working hours
    date = start_date
    working_hours = []
    for i in range((after_a_month-start_date).days):
        date = start_date + relativedelta(days=i)
        if date.weekday() < 5:
            working_hours.append({date: working_hours_map[doctor_id]})

    # 2. get appointments and merge intervals
    appointments = Appointment.query.filter(Appointment.doctor_id == doctor_id, Appointment.date >= start_date, Appointment.date <= after_a_month).all()
    appointment_hours = {}
    for appointment in appointments:
        if appointment.date not in appointment_hours:
            appointment_hours[appointment.date] = []
        appointment_hours[appointment.date].append([appointment.start, appointment.end])

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
    #print(appointment_hours) {datetime.date(2022, 12, 25): [[1200, 1400]]}

    # 3. calculate first available appointment
    for working_hour in working_hours:
        de = deque([])  
        for working_date, hours in working_hour.items():
            if working_date in appointment_hours:
                for interval in appointment_hours[working_date]:
                    de.append(interval) 
        de.appendleft([working_hours_map[doctor_id][0], working_hours_map[doctor_id][0]]);
        de.append([working_hours_map[doctor_id][1], working_hours_map[doctor_id][1]])
        # deque([[900, 900], [1200, 1400], [1700, 1700]])
        for i in range(1, len(de)):
            current_duration = int((de[i][0] - de[i-1][1])/100 * 60)
            # print(working_date, de[i-1][1], de[i][0]) # available duration
            if current_duration >= duration:
                result = {str(working_date) : [de[i-1][1], de[i-1][1] + duration]}
                return jsonify(result)
            
    return jsonify(result)
