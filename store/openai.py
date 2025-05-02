from flask import current_app
from openai import OpenAI

def get_openai_client():
    api_key = current_app.config.get('OPENAI_API_KEY')
    return OpenAI(api_key=api_key)