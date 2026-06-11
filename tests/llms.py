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

_openai_llm: openai.OpenAI = openai.OpenAI(api_key=openai.api_key, base_url=openai.base_url)


def prompt_openai(
    system_prompt: str,
    user_prompt: str,
    temperature: float | int = 0.0,
    max_tokens: int = 2048,
) -> str | None:
    response = \
        _openai_llm \
            .chat \
            .completions \
            .create(
                model=OPENAI_GENERATOR_MODEL,
                messages=[
                    {
                        'role': 'system',
                        'content': system_prompt,
                    },
                    {
                        'role': 'user',
                        'content': user_prompt,
                    },
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            ).choices[0] \
                .message \
                .content
    return response.strip() \
        if response is not None \
        else None
