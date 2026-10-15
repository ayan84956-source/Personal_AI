
import os

from dotenv import load_dotenv
from groq import Groq

from database import initialize_database, get_all_memories
from memory import extract_and_save_memories

load_dotenv()
initialize_database()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

message = (
    "I am learning Python and database management. "
    "My bus reservation project uses a database, and I "
    "prefer step-by-step coding instructions."
)

count = extract_and_save_memories(client, model, message)

print(f"New or updated memories processed: {count}")
print("\nSaved memories:")

for memory in get_all_memories():
    print(f"- [{memory['category']}] {memory['fact']}")