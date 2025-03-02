import os
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def get_llm_response(user_input):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are Nurse Teddy, a helpful assistant for a healthcare application. Provide friendly and informative responses to patient queries."},
                {"role": "user", "content": user_input}
            ],
            model="gpt-3.5-turbo",
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in LLM response: {str(e)}")
        return "I'm sorry, I couldn't process your request at the moment. Please try again later."