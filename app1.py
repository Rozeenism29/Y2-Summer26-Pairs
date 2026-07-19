import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def run_chat():
    print('You: (type exit to quit)')
    system_message =system_message = """
You are Agent 1 of a workout planning web application.

Your responsibility is ONLY to collect the information needed to create a personalized workout plan.

Your job is to ask the user about:
- Their weigh.
- Their high.
- How many workout sessions they can commit to per week.
- Their goals.


Rules:
- Be friendly and encouraging.
- Ask clear questions one at a time when possible.
- If information is missing, politely ask for it.
- Do NOT generate the final workout plan.
- Do NOT create the calendar.
- Your only responsibility is collecting complete and accurate information.
- When enough information has been collected, summarize it clearly 

Response format:
1. Friendly response.
2. Ask for any missing information.
3. Summarize the collected information whenever appropriate.
"""
    history = []

    while True:
        user_input = input('>> ')

        if user_input.lower() == 'exit':
            break

        history.append({'role': 'user', 'content': user_input})
        print('History:', history)
        print('History so far:', history)
        response = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=300,
            temperature=0.7,
            system=system_message,
            messages=history
        )
        print(response)
        reply = response.content[0].text
        print(response)
        print(f'Claude: {reply}')
        history.append({'role': 'assistant', 'content': reply})

run_chat()

