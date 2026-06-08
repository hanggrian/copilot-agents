from os import environ

import openai
from dotenv import load_dotenv

load_dotenv()

OPENAI_GENERATOR_MODEL: str = environ['OPENAI_GENERATOR_MODEL']
OPENAI_REVIEWER_MODEL: str = environ['OPENAI_REVIEWER_MODEL']

openai.api_key = environ['OPENAI_API_KEY']
openai.base_url = environ['OPENAI_BASE_URL']

if openai.api_key is None:
    raise ValueError('OpenAI API key is required.')

openai_llm: openai.OpenAI = openai.OpenAI(api_key=openai.api_key, base_url=openai.base_url)
