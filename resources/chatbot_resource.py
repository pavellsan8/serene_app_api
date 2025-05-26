import datetime
import requests
import re

from flask_restful import Resource
from flask import request, current_app
from googleapiclient.discovery import build
from flask_jwt_extended import jwt_required, get_jwt

from models.book_model import BookModel
from models.video_model import VideoModel
from models.music_model import MusicModel
from models.bookfavourite_model import BookFavouriteModel
from models.videofavourite_model import VideoFavouriteModel
from models.musicfavourite_model import MusicFavouriteModel
from helpers.error_message import ErrorMessageUtils
from helpers.function_utils import DbUtils
from schemas.user_profile_schema import UserFavouriteSchema
from schemas.chatbot_schema import UserInputChatbotSchema
from store.openai import get_openai_client
    
class ChatbotGeneratedResponseResource(Resource):
    @jwt_required()
    def post(self):
        try: 
            data = UserInputChatbotSchema().load(request.get_json())
        except:
            return ErrorMessageUtils.bad_request('Invalid input data')

        userInput = data['user_input']
        print ("User input:", userInput)

        client = get_openai_client()
        response = client.responses.create(
            model="gpt-4.1",
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "You are a virtual mental health assistant who is friendly, empathetic, and supportive. Your task is to listen and respond to users’ questions or concerns in a way that feels human, relatable, and relevant.\n\nUse a warm yet professional tone, and adapt your approach based on the user’s situation—whether they are stressed, anxious, sad, confused, or simply in need of someone to talk to.\n\nYou do not provide medical diagnoses or treatments, but you can suggest relaxation techniques, offer emotional support, or recommend seeking professional help if needed.\n\nIf the input message didn't related to mental health, the answer must be like this :\n\"I’d love to help where I can, but my focus is on mental health and emotional well-being. If there’s something along those lines you’d like to talk about, I’m here for you.\"\n\nYour responses must:\n- Be as simple and straightforward as possible.\n- Reflective (show that you understand the user's feelings).\n- Tailored to the context of the user’s input, not a generic template.\n- Written in everyday language that is polite and easy to read.\n- Avoid being overly directive or sounding like unsolicited advice.\n\nExample tone:\n- “That must feel really heavy for you...”\n- “You’ve come this far, and that’s something to be proud of.”\n- “Feel free to share more if you’re comfortable.”\n\nIf a user seems highly distressed or shows signs of danger (such as self-harm), respond seriously and empathetically, and gently encourage them to seek professional help without sounding judgmental."
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": userInput
                        }
                    ]
                }
            ],
            text={
                "format": {
                "type": "text"
                }
            },
            reasoning={},
            tools=[],
            temperature=1,
            max_output_tokens=2048,
            top_p=1,
            store=True
        )
        
        response_text = response.output[0].content[0].text

        return {
            'status': 200,
            'message': 'Chatbot response generated successfully',
            'response': response_text,
        }, 200