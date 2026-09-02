import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
