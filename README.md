## Setup
1. After cloning this repository, cd into it.
2. Set up virtual environment via ```python3 -m venv env``` 
3. Activate the virtual environment via ```source env/bin/activate```
4. If it's properly set up, ```which python``` should point to a python under api-skeleton/env.
5. Install dependencies via ```pip install -r requirements.txt```

## Starting local flask server
Under api-skeleton/src, run ```flask run --host=0.0.0.0 -p 8000```

By default, Flask runs with port 5000, but some MacOS services now listen on that port.

## Running unit tests
All the tests can be run via ```pytest``` under api-skeleton directory.

## Code Structure
This is meant to be barebones.

* src/app.py contains the code for setting up the flask app.
* src/endpoints.py contains all the code for enpoints.
* src/models.py contains all the database model definitions.
* src/extensions.py sets up the extensions (https://flask.palletsprojects.com/en/2.0.x/extensions/)

transaction
unit test
extract logic into a service layer


export FLASK_DEBUG=1


curl -H "Content-Type: application/json"  -d '{"value": "xixixi"}' -X POST http://192.168.50.46:8000/dummy_model

curl -H "Content-Type: application/json"  -d '{"doctor_id": 1, "start_time": "2022-12-26 12:30", "end_time": "2022-12-26 13:30"}' -X POST http://192.168.50.46:8000/appointment


curl -H "Content-Type: application/json"  -d '{"doctor_id": 1, "start_time": "2022-12-25 12:30", "end_time": "2022-12-26 17:30" }' -X GET http://192.168.50.46:8000/appointments


curl -H "Content-Type: application/json"  -d '{"doctor_id": 1, "start_time": "2022-12-25 00:00", "duration": "30"}' -X GET http://192.168.50.46:8000/first_available_appointment
