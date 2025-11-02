import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("OTOMOTO_URL", "https://www.otomoto.pl/osobowe/bmw/seria-5")