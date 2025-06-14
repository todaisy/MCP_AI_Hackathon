import os

API_TOKEN = os.getenv("API_TOKEN","")
ADMIN_ID = os.getenv("ADMIN_ID","")  
DB_PATH = os.getenv("DB_PATH","")
LOG_FILE = os.getenv("LOG_FILE","")

TOKEN = os.getenv("TOKEN", "")
FOLDER = os.getenv("FOLDER", "")

conn = psy.connect()
