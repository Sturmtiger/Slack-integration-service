import requests

from slack_integration_service.celery import app
from .api.slack_web_client import CustomSlackWebClient


@app.task
def post_message(app_name, template_name):
    """Post message to Slack."""
    slack_web_client = CustomSlackWebClient(app_name, template_name)
    slack_response = slack_web_client.post_message()

    return slack_response.status_code


@app.task
def post_request(url, data):
    response = requests.post(url, json=data)
    return response.status_code
