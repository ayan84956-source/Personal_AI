
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("GROQ_API_KEY is missing from .env")
else:
    try:
        client = Groq(api_key=api_key, timeout=30, max_retries=1)

        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
            messages=[
                {"role": "user", "content": "Reply with: Connection successful"}
            ],
        )

        print(response.choices[0].message.content)

    except Exception as error:
        print("Error type:", type(error).__name__)
        print("Error details:", repr(error))
        print("Underlying cause:", repr(error.__cause__))