
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def run_chat():
    print('You: (type exit to quit)')
    system_message = "Your name is Alex. You are a helpful and friendly assistant who helps students learn about technology and computer science. You explain things clearly and always encourage curiosity."
    history = []

    while True:
        user_input = input('>> ')

        if user_input.lower() == 'exit':
            break

        history.append({'role': 'user', 'content': user_input})

        response = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=2999,
            temperature=0.7,
            system=system_message,
            messages=history
        )

        reply = response.content[0].text
        print(f'Claude: {reply}')
        history.append({'role': 'assistant', 'content': reply})

run_chat()