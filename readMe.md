## HubSpot CRM API

A basic flask app webhook that listens for HubSpot CRM events and logs them to a database.

### Gunicorn
This app using gunicorn server to run the app. To run the app, use the following command:
`gunicorn -b 0.0.0.0:8000 -c gunicorn_config.py app:app`

### Create requirements.txt
`pip freeze > requirements.txt`

### Install requirements with
`pip install -r requirements.txt`

## Start virtual environment
`source venv/bin/activate`
