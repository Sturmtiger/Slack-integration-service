#!/bin/bash

celery -A slack_integration_service worker --beat --scheduler django --loglevel=info