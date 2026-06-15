import os

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


def ask_ai(prompt):

    try:

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:

        return f"AI Error: {str(e)}"