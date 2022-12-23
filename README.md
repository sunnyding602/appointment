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

## Todos
1. transaction
2. unit test
3. extract logic into a service layer
4. check input

## Table structure
![image](https://user-images.githubusercontent.com/2386727/209404460-46a9ca55-8597-430c-b0f9-937272307c0d.png)
![image](https://user-images.githubusercontent.com/2386727/209404470-610de544-30e1-4683-a42b-c802bcb1f13b.png)
![image](https://user-images.githubusercontent.com/2386727/209404478-06aaf029-fd57-4980-b377-d6e53f185b50.png)




## Useful Commands
export FLASK_DEBUG=1


curl -H "Content-Type: application/json"  -d '{"doctor_id": 1, "start_time": "2022-12-26 12:30", "end_time": "2022-12-26 13:30"}' -X POST http://192.168.50.46:8000/appointment


curl -H "Content-Type: application/json"  -d '{"doctor_id": 1, "start_time": "2022-12-25 12:30", "end_time": "2022-12-26 17:30" }' -X GET http://192.168.50.46:8000/appointments


curl -H "Content-Type: application/json"  -d '{"doctor_id": 1, "start_time": "2022-12-25 00:00", "duration": "30"}' -X GET http://192.168.50.46:8000/first_available_appointment
