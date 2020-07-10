import requests

from slack_integration_service.celery import app
from .api.slack_web_client import CustomSlackWebClient

from slack_integration.models import SlackApplication, Template


@app.task
def post_message(app_id, template_id):
    """Post message to Slack."""
    app_obj = SlackApplication.objects.get(id=app_id)
    template_obj = Template.objects.get(id=template_id)

    slack_web_client = CustomSlackWebClient(app_obj, template_obj)
    slack_response = slack_web_client.post_message()

    return slack_response.status_code


@app.task
def post_request(url, data):
    response = requests.post(url, json=data)
    return response.status_code
